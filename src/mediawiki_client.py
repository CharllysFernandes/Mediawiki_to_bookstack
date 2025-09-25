import requests
import json
from urllib.parse import urljoin
import urllib3

class MediaWikiClient:
    def __init__(self, api_url, username, password, verify_ssl=False, timeout=30, user_agent='MediaWiki-to-BookStack/1.0'):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        
        # Opções de bypass
        self.bypass_restrictions = True
        self.bot_mode = False
        
        # Tokens para operações avançadas
        self.csrf_token = ''
        self.edit_token = ''
        
        # Desabilitar avisos de SSL se verificação estiver desabilitada
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent
        })
        
        # Configurar verificação SSL
        self.session.verify = verify_ssl
        
    def _make_request(self, params, method='GET', retry_on_403=True):
        """Faz requisição para a API do MediaWiki com estratégias de bypass"""
        last_exception = None
        
        # Lista de estratégias para tentar
        strategies = [
            self._request_standard,
            self._request_with_csrf,
            self._request_with_referer,
            self._request_as_form,
        ]
        
        for strategy in strategies:
            try:
                return strategy(params, method)
            except requests.exceptions.HTTPError as e:
                last_exception = e
                if e.response.status_code == 403 and retry_on_403:
                    # Erro 403 - tentar próxima estratégia
                    continue
                else:
                    # Outros erros HTTP - re-lançar
                    raise
            except Exception as e:
                last_exception = e
                # Para outros erros, tentar próxima estratégia
                continue
        
        # Se todas as estratégias falharam, lançar último erro
        if last_exception:
            raise last_exception
        else:
            raise Exception("Todas as estratégias de requisição falharam")
    
    def _request_standard(self, params, method):
        """Estratégia padrão de requisição"""
        if method == 'GET':
            response = self.session.get(
                self.api_url, 
                params=params, 
                timeout=self.timeout,
                verify=self.verify_ssl
            )
        else:
            response = self.session.post(
                self.api_url, 
                data=params, 
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            
        response.raise_for_status()
        return response.json()
    
    def _request_with_csrf(self, params, method):
        """Requisição incluindo token CSRF se disponível"""
        if hasattr(self, 'csrf_token') and self.csrf_token:
            params = params.copy()
            params['token'] = self.csrf_token
        
        return self._request_standard(params, method)
    
    def _request_with_referer(self, params, method):
        """Requisição com header Referer configurado"""
        # Temporariamente adicionar referer
        original_headers = self.session.headers.copy()
        
        base_url = self.api_url.replace('/api.php', '')
        self.session.headers['Referer'] = base_url
        
        try:
            return self._request_standard(params, method)
        finally:
            # Restaurar headers originais
            self.session.headers = original_headers
    
    def _request_as_form(self, params, method):
        """Requisição com Content-Type de form"""
        try:
            if method == 'POST':
                # Temporariamente modificar content-type
                original_headers = self.session.headers.copy()
                self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded'
                
                try:
                    response = self.session.post(
                        self.api_url,
                        data=params,
                        timeout=self.timeout,
                        verify=self.verify_ssl
                    )
                    response.raise_for_status()
                    return response.json()
                finally:
                    self.session.headers = original_headers
            else:
                return self._request_standard(params, method)
        except requests.exceptions.SSLError as e:
            raise Exception(f"Erro SSL: {str(e)}. Considere desabilitar verificação SSL.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro na requisição: {str(e)}")
        except Exception as e:
            raise Exception(f"Erro geral: {str(e)}")
    
    def login(self):
        """Realiza login com estratégias múltiplas para contornar restrições"""
        try:
            # Estratégia 1: Login padrão
            if self._standard_login():
                # Após login bem-sucedido, obter tokens adicionais
                self._get_additional_tokens()
                # Configurar headers extras para bypass
                self._setup_bypass_headers()
                return True
            
            return False
                
        except Exception as e:
            # Estratégia 2: Tentar login com bot flag
            try:
                return self._bot_login()
            except:
                raise Exception(f"Erro durante o login: {str(e)}")
    
    def _standard_login(self):
        """Login padrão com tokens"""
        # Obter token de login
        login_token_params = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json'
        }
        
        token_response = self._make_request(login_token_params)
        login_token = token_response['query']['tokens']['logintoken']
        
        # Realizar login
        login_params = {
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password,
            'lgtoken': login_token,
            'format': 'json'
        }
        
        login_response = self._make_request(login_params, method='POST')
        
        if login_response.get('login', {}).get('result') == 'Success':
            return True
        else:
            reason = login_response.get('login', {}).get('reason', 'Motivo desconhecido')
            raise Exception(f"Falha no login: {reason}")
    
    def _bot_login(self):
        """Tentativa de login com flag de bot"""
        try:
            # Configurar como bot user-agent
            self.session.headers.update({
                'User-Agent': f'MediaWiki-Bot/1.0 ({self.username})',
                'Api-User-Agent': f'MediaWiki-Bot/1.0 ({self.username})'
            })
            
            return self._standard_login()
        except:
            return False
    
    def _get_additional_tokens(self):
        """Obtém tokens adicionais para operações avançadas"""
        try:
            # Obter tokens de edição e outros
            token_params = {
                'action': 'query',
                'meta': 'tokens',
                'type': 'csrf|edit|move|delete|protect|patrol',
                'format': 'json'
            }
            
            response = self._make_request(token_params)
            tokens = response.get('query', {}).get('tokens', {})
            
            # Armazenar tokens para uso posterior
            self.csrf_token = tokens.get('csrftoken', '')
            self.edit_token = tokens.get('edittoken', '')
            
        except Exception as e:
            # Tokens opcionais - não falhamos se não conseguirmos
            pass
    
    def _setup_bypass_headers(self):
        """Configura headers adicionais para contornar restrições"""
        self.session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
    
    def get_site_info(self):
        """Obtém informações básicas do site"""
        params = {
            'action': 'query',
            'meta': 'siteinfo',
            'format': 'json'
        }
        
        response = self._make_request(params)
        return response.get('query', {}).get('general', {})
    
    def get_namespaces(self):
        """Obtém todos os namespaces da wiki"""
        params = {
            'action': 'query',
            'meta': 'siteinfo',
            'siprop': 'namespaces',
            'format': 'json'
        }
        
        response = self._make_request(params)
        return response.get('query', {}).get('namespaces', {})
    
    def get_page_content(self, page_title):
        """Obtém conteúdo de uma página específica"""
        params = {
            'action': 'query',
            'titles': page_title,
            'prop': 'revisions',
            'rvprop': 'content',
            'format': 'json'
        }
        
        response = self._make_request(params)
        pages = response.get('query', {}).get('pages', {})
        
        for page_id, page_data in pages.items():
            if 'revisions' in page_data:
                return page_data['revisions'][0]['*']
        
        return None
    
    def get_page_content_html(self, page_title):
        """Obtém conteúdo de uma página em formato HTML"""
        params = {
            'action': 'parse',
            'page': page_title,
            'format': 'json',
            'prop': 'text|displaytitle|categories|links|images'
        }
        
        try:
            response = self._make_request(params)
            
            # Verificar se a resposta é um dicionário válido
            if not isinstance(response, dict):
                raise Exception(f"Resposta inválida da API: {str(response)}")
            
            # Verificar se há erro na resposta
            if 'error' in response:
                error_info = response['error']
                error_code = error_info.get('code', 'unknown')
                error_msg = error_info.get('info', 'Erro desconhecido')
                raise Exception(f"Erro da API ({error_code}): {error_msg}")
            
            # Verificar se a página existe e foi parseada
            if 'parse' in response:
                parse_data = response['parse']
                
                # Verificar se há dados válidos
                if not parse_data:
                    raise Exception("Dados de parse vazios retornados pela API")
                
                return {
                    'title': parse_data.get('displaytitle', page_title),
                    'html': parse_data.get('text', {}).get('*', '') if isinstance(parse_data.get('text'), dict) else '',
                    'categories': [cat.get('*', '') for cat in parse_data.get('categories', []) if isinstance(cat, dict)],
                    'links': [link.get('*', '') for link in parse_data.get('links', []) if isinstance(link, dict)],
                    'images': [img.get('*', '') for img in parse_data.get('images', []) if isinstance(img, dict)]
                }
            else:
                # Tentar método alternativo para páginas com caracteres especiais
                return self._get_page_html_alternative(page_title)
                
        except Exception as e:
            # Log detalhado do erro para debug
            error_msg = str(e)
            if "does not exist" in error_msg.lower() or "missing" in error_msg.lower():
                raise Exception(f"Página '{page_title}' não encontrada")
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                raise Exception(f"Sem permissão para acessar '{page_title}'")
            else:
                raise Exception(f"Erro ao obter HTML da página '{page_title}': {error_msg}")
    
    def _get_page_html_alternative(self, page_title):
        """Método alternativo para obter HTML de páginas com problemas"""
        try:
            # Primeiro tentar obter informações básicas da página
            page_info_params = {
                'action': 'query',
                'titles': page_title,
                'prop': 'info|categories',
                'format': 'json'
            }
            
            info_response = self._make_request(page_info_params)
            
            if 'query' not in info_response or 'pages' not in info_response['query']:
                raise Exception("Não foi possível obter informações da página")
            
            pages = info_response['query']['pages']
            page_data = None
            page_exists = False
            
            for page_id, page_info in pages.items():
                if page_id != '-1':  # -1 indica página inexistente
                    page_data = page_info
                    page_exists = True
                    break
            
            if not page_exists:
                raise Exception("Página não existe")
            
            # Tentar obter conteúdo usando action=query com prop=revisions
            content_params = {
                'action': 'query',
                'titles': page_title,
                'prop': 'revisions',
                'rvprop': 'content',
                'rvparse': '1',
                'format': 'json'
            }
            
            content_response = self._make_request(content_params)
            
            if 'query' in content_response and 'pages' in content_response['query']:
                for page_id, page_content in content_response['query']['pages'].items():
                    if 'revisions' in page_content and page_content['revisions']:
                        revision = page_content['revisions'][0]
                        html_content = revision.get('*', '')
                        
                        return {
                            'title': page_data.get('title', page_title),
                            'html': html_content,
                            'categories': [cat.get('title', '').replace('Category:', '') 
                                         for cat in page_data.get('categories', [])],
                            'links': [],  # Não disponível neste método
                            'images': []  # Não disponível neste método
                        }
            
            # Se tudo falhar, retornar estrutura mínima
            return {
                'title': page_title,
                'html': '<p><em>Conteúdo não pôde ser extraído automaticamente.</em></p>',
                'categories': [],
                'links': [],
                'images': []
            }
            
        except Exception as e:
            raise Exception(f"Método alternativo falhou: {str(e)}")

    def get_all_pages(self, namespace=None, limit=None, callback=None):
        """Obtém todas as páginas da wiki com paginação"""
        all_pages = []
        continue_param = None
        batch_size = 50  # Tamanho do lote por requisição
        total_processed = 0
        
        try:
            while True:
                params = {
                    'action': 'query',
                    'list': 'allpages',
                    'aplimit': batch_size,
                    'format': 'json'
                }
                
                # Filtrar por namespace se especificado
                if namespace is not None:
                    params['apnamespace'] = namespace
                
                # Continuação para paginação
                if continue_param:
                    params['apcontinue'] = continue_param
                
                response = self._make_request(params)
                
                if 'query' not in response or 'allpages' not in response['query']:
                    break
                
                pages = response['query']['allpages']
                if not pages:
                    break
                
                all_pages.extend(pages)
                total_processed += len(pages)
                
                # Callback para atualização de progresso
                if callback:
                    callback(total_processed, len(pages))
                
                # Verificar se há mais páginas
                if 'continue' in response and 'apcontinue' in response['continue']:
                    continue_param = response['continue']['apcontinue']
                else:
                    break
                
                # Limite opcional
                if limit and total_processed >= limit:
                    all_pages = all_pages[:limit]
                    break
                    
        except Exception as e:
            raise Exception(f"Erro ao obter páginas: {str(e)}")
        
        return all_pages
    
    def get_page_content_wikitext(self, page_title, bypass_restrictions=True):
        """
        Obtém conteúdo de uma página em formato wikitext (código fonte)
        
        Args:
            page_title: Título da página
            bypass_restrictions: Tentar contornar restrições de permissão
        """
        # Estratégia 1: Método padrão
        try:
            return self._get_wikitext_standard(page_title)
        except Exception as e:
            if not bypass_restrictions:
                raise e
            
            error_msg = str(e).lower()
            
            # Se for erro de permissão, tentar métodos alternativos
            if any(keyword in error_msg for keyword in ['403', 'forbidden', 'permission', 'unauthorized']):
                # Estratégia 2: Usar revisões antigas
                try:
                    return self._get_wikitext_via_revisions(page_title)
                except Exception as e2:
                    # Estratégia 3: Usar exportação
                    try:
                        return self._get_wikitext_via_export(page_title)
                    except Exception as e3:
                        # Estratégia 4: Parse da página renderizada
                        try:
                            return self._get_wikitext_via_parse(page_title)
                        except Exception as e4:
                            # Se tudo falhar, tentar método raw
                            try:
                                return self._get_wikitext_raw(page_title)
                            except Exception as e5:
                                # Último recurso: informar erro original
                                raise Exception(f"Todas as estratégias falharam. Erro original: {str(e)}")
            else:
                # Para outros tipos de erro, re-lançar
                raise e
    
    def _get_wikitext_standard(self, page_title):
        """Método padrão para obter wikitext"""
        params = {
            'action': 'query',
            'titles': page_title,
            'prop': 'revisions|categories|info',
            'rvprop': 'content',
            'format': 'json'
        }
        
        response = self._make_request(params)
        
        if not isinstance(response, dict):
            raise Exception(f"Resposta inválida da API: {str(response)}")
        
        if 'error' in response:
            error_info = response['error']
            error_code = error_info.get('code', 'unknown')
            error_msg = error_info.get('info', 'Erro desconhecido')
            raise Exception(f"Erro da API ({error_code}): {error_msg}")
        
        if 'query' in response and 'pages' in response['query']:
            pages = response['query']['pages']
            
            for page_id, page_data in pages.items():
                if page_id == '-1':
                    raise Exception("Página não encontrada")
                
                if 'revisions' in page_data and page_data['revisions']:
                    wikitext = page_data['revisions'][0].get('*', '')
                    
                    # Extrair categorias
                    categories = []
                    if 'categories' in page_data:
                        categories = [cat.get('title', '').replace('Category:', '') 
                                    for cat in page_data.get('categories', [])]
                    
                    return {
                        'title': page_data.get('title', page_title),
                        'wikitext': wikitext,
                        'categories': categories,
                        'pageid': page_data.get('pageid', ''),
                        'length': page_data.get('length', 0),
                        'touched': page_data.get('touched', '')
                    }
                else:
                    raise Exception("Página sem conteúdo ou revisões")
        else:
            raise Exception("Resposta da API não contém dados de páginas")
    
    def _get_wikitext_via_revisions(self, page_title):
        """Obtém wikitext através de revisões históricas"""
        # Primeiro obter lista de revisões
        params = {
            'action': 'query',
            'titles': page_title,
            'prop': 'revisions',
            'rvprop': 'ids|timestamp|user|size',
            'rvlimit': 10,  # Pegar últimas 10 revisões
            'format': 'json'
        }
        
        response = self._make_request(params)
        
        if 'query' in response and 'pages' in response['query']:
            for page_id, page_data in response['query']['pages'].items():
                if 'revisions' in page_data:
                    # Tentar cada revisão até encontrar uma acessível
                    for revision in page_data['revisions']:
                        rev_id = revision.get('revid')
                        try:
                            return self._get_revision_content(page_title, rev_id)
                        except:
                            continue
        
        raise Exception("Não foi possível acessar nenhuma revisão")
    
    def _get_revision_content(self, page_title, rev_id):
        """Obtém conteúdo de uma revisão específica"""
        params = {
            'action': 'query',
            'revids': rev_id,
            'prop': 'revisions',
            'rvprop': 'content',
            'format': 'json'
        }
        
        response = self._make_request(params)
        
        if 'query' in response and 'pages' in response['query']:
            for page_id, page_data in response['query']['pages'].items():
                if 'revisions' in page_data and page_data['revisions']:
                    wikitext = page_data['revisions'][0].get('*', '')
                    return {
                        'title': page_data.get('title', page_title),
                        'wikitext': wikitext,
                        'categories': [],  # Não disponível via revisão
                        'pageid': page_data.get('pageid', ''),
                        'length': len(wikitext),
                        'touched': ''
                    }
        
        raise Exception("Revisão não acessível")
    
    def _get_wikitext_via_export(self, page_title):
        """Obtém wikitext através da funcionalidade de exportação"""
        # Usar Special:Export que às vezes tem permissões diferentes
        export_params = {
            'action': 'query',
            'export': '1',
            'titles': page_title,
            'format': 'json'
        }
        
        try:
            response = self._make_request(export_params)
            
            if 'query' in response and 'export' in response['query']:
                export_data = response['query']['export']
                
                # Parse do XML export (simplificado)
                import re
                xml_content = str(export_data)
                
                # Extrair texto da revisão do XML
                text_match = re.search(r'<text[^>]*>(.*?)</text>', xml_content, re.DOTALL)
                if text_match:
                    wikitext = text_match.group(1)
                    # Decodificar entidades XML
                    wikitext = wikitext.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
                    
                    return {
                        'title': page_title,
                        'wikitext': wikitext,
                        'categories': [],
                        'pageid': '',
                        'length': len(wikitext),
                        'touched': ''
                    }
            
        except Exception as e:
            pass  # Falha silenciosa para tentar próximo método
        
        raise Exception("Export não acessível")
    
    def _get_wikitext_via_parse(self, page_title):
        """Obtém wikitext através da ação parse (método indireto)"""
        # Usar parse com wikitext=1 para obter código fonte
        params = {
            'action': 'parse',
            'page': page_title,
            'prop': 'wikitext',
            'format': 'json'
        }
        
        try:
            response = self._make_request(params)
            
            if 'parse' in response and 'wikitext' in response['parse']:
                wikitext = response['parse']['wikitext'].get('*', '')
                
                return {
                    'title': response['parse'].get('title', page_title),
                    'wikitext': wikitext,
                    'categories': [],
                    'pageid': response['parse'].get('pageid', ''),
                    'length': len(wikitext),
                    'touched': ''
                }
        except Exception as e:
            pass
        
        raise Exception("Parse não acessível")
    
    def _get_wikitext_raw(self, page_title):
        """Último recurso: tentar acesso raw via URL direta"""
        try:
            # Construir URL para acesso raw
            base_url = self.api_url.replace('/api.php', '')
            raw_url = f"{base_url}/index.php"
            
            params = {
                'title': page_title,
                'action': 'raw'
            }
            
            response = self.session.get(raw_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # Se conseguiu acessar, o conteúdo é o wikitext raw
            wikitext = response.text
            
            return {
                'title': page_title,
                'wikitext': wikitext,
                'categories': [],
                'pageid': '',
                'length': len(wikitext),
                'touched': ''
            }
            
        except Exception as e:
            pass
        
        raise Exception("Acesso raw não disponível")
    
    
    def _get_current_datetime(self):
        """Retorna data/hora atual formatada"""
        from datetime import datetime
        return datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    def get_page_content_batch(self, page_titles, callback=None, format_type='wikitext', expand_templates=True):
        """
        Obtém conteúdo de múltiplas páginas em lote
        
        Args:
            page_titles: Lista de títulos das páginas
            callback: Função de callback para progresso
            format_type: Tipo de formato ('wikitext', 'html')
            expand_templates: Se deve expandir templates
        """
        contents = {}
        total_processed = 0
        batch_size = 10  # Processar em lotes de 10 páginas
        
        for i in range(0, len(page_titles), batch_size):
            batch = page_titles[i:i + batch_size]
            
            for title in batch:
                try:
                    if format_type == 'wikitext':
                        content = self.get_page_content_wikitext(title)
                    elif format_type == 'html':
                        content = self.get_page_content_html(title)
                    else:
                        content = self.get_page_content(title)
                    
                    contents[title] = content
                    total_processed += 1
                    
                    if callback:
                        callback(total_processed, len(batch))
                        
                except Exception as e:
                    contents[title] = f"ERRO: {str(e)}"
                    total_processed += 1
                    
                    if callback:
                        callback(total_processed, len(batch))
        
        return contents
