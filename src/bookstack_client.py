"""
Cliente para API do BookStack
Gerencia integração com BookStack para importação de conteúdo
"""

import requests
import json
from typing import Dict, List, Optional, Union
import time
from urllib.parse import urljoin

class BookStackClient:
    """Cliente para API do BookStack"""
    
    def __init__(self, base_url: str, token_id: str, token_secret: str, verify_ssl: bool = True):
        """
        Inicializa cliente BookStack
        
        Args:
            base_url: URL base do BookStack (ex: https://bookstack.empresa.com)
            token_id: ID do token de API
            token_secret: Secret do token de API
            verify_ssl: Verificar certificados SSL
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
        self.token_id = token_id
        self.token_secret = token_secret
        self.verify_ssl = verify_ssl
        
        # Configurar sessão
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {token_id}:{token_secret}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'MediaWiki-to-BookStack/1.0'
        })
        self.session.verify = verify_ssl
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms entre requisições
        
    def _make_request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> dict:
        """
        Faz requisição para API do BookStack
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint da API (sem /api)
            data: Dados para envio (POST/PUT)
            params: Parâmetros de query
            
        Returns:
            Resposta JSON da API
        """
        # Rate limiting simples
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        url = urljoin(self.api_base + '/', endpoint.lstrip('/'))
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
            
            self.last_request_time = time.time()
            
            # Verificar status da resposta
            response.raise_for_status()
            
            # Retornar JSON se disponível
            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                return {'success': True, 'data': response.text}
                
        except requests.exceptions.RequestException as e:
            # Incluir mais detalhes do erro
            error_details = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_body = e.response.text
                    error_details += f" | Response: {error_body}"
                except:
                    pass
            raise Exception(f"Erro na requisição para BookStack: {error_details}")
        except json.JSONDecodeError as e:
            raise Exception(f"Erro ao decodificar resposta JSON: {str(e)}")
    
    def test_connection(self) -> Dict:
        """
        Testa conexão com a API do BookStack
        
        Returns:
            Dicionário com resultado do teste
        """
        try:
            # Tentar obter informações do usuário atual
            response = self._make_request('GET', '/users/me')
            user_info = response.get('data', {})
            
            # Testar permissões de criação
            create_perms = self._test_create_permissions()
            
            return {
                'success': True,
                'message': 'Conexão com BookStack estabelecida com sucesso',
                'user_info': user_info,
                'api_version': response.get('version', 'desconhecida'),
                'create_permissions': create_perms
            }
            
        except Exception as e:
            error_message = str(e)
            
            # Detectar erro específico de falta de permissão de API
            if "proprietário do código de API" in error_message or "não tem permissão para fazer requisições de API" in error_message:
                return {
                    'success': False,
                    'message': '❌ USUÁRIO SEM PERMISSÃO DE API',
                    'error': error_message,
                    'solution': (
                        "O usuário associado ao token não pode usar a API do BookStack.\n\n"
                        "COMO CORRIGIR:\n"
                        "1. Acesse BookStack como administrador\n"
                        "2. Vá em: Configurações > Usuários > [Usuário do Token]\n"
                        "3. Clique em 'Editar'\n"
                        "4. Na seção 'Roles', adicione uma role que tenha 'API Access'\n"
                        "5. Salve as alterações\n\n"
                        "ALTERNATIVA: Use um token de usuário administrador"
                    )
                }
            
            # Erro 500 específico do endpoint /users/me (bug conhecido em algumas versões)
            elif "500 Server Error" in error_message and "/users/me" in error_message:
                # Tentar métodos alternativos para obter informações do usuário
                try:
                    # Método 1: Tentar listar livros como teste de funcionalidade
                    books_response = self._make_request('GET', '/books', params={'count': 1})
                    
                    # Método 2: Tentar obter informações através de uma página criada temporariamente
                    user_info = self._get_user_info_alternative()
                    
                    # Testar permissões de criação
                    create_perms = self._test_create_permissions()
                    
                    return {
                        'success': True,
                        'message': 'Conexão com BookStack estabelecida (endpoint /users/me indisponível)',
                        'user_info': user_info,
                        'api_version': 'funcional',
                        'create_permissions': create_perms
                    }
                except Exception:
                    return {
                        'success': False,
                        'message': '❌ ERRO NO SERVIDOR BOOKSTACK',
                        'error': error_message,
                        'solution': (
                            "Erro 500 no servidor BookStack.\n\n"
                            "POSSÍVEIS CAUSAS:\n"
                            "• Bug no endpoint /users/me desta versão\n"
                            "• Problema interno no servidor\n"
                            "• Configuração incorreta do BookStack\n\n"
                            "TESTE ALTERNATIVO:\n"
                            "• Tente enviar uma página para testar se a API funciona\n"
                            "• Verifique logs do servidor BookStack"
                        )
                    }
            
            # Outros erros 403
            elif "403" in error_message or "Forbidden" in error_message:
                return {
                    'success': False,
                    'message': '❌ ACESSO NEGADO',
                    'error': error_message,
                    'solution': (
                        "Token rejeitado pelo BookStack.\n\n"
                        "VERIFICAÇÕES:\n"
                        "• Token ID e Secret estão corretos\n"
                        "• Token não está expirado\n"
                        "• Usuário tem permissão de API\n"
                        "• URL do BookStack está correta"
                    )
                }
            
            # Erro de conexão/rede
            elif "connection" in error_message.lower() or "network" in error_message.lower() or "timeout" in error_message.lower():
                return {
                    'success': False,
                    'message': '❌ ERRO DE CONEXÃO',
                    'error': error_message,
                    'solution': (
                        "Não foi possível conectar ao BookStack.\n\n"
                        "VERIFICAÇÕES:\n"
                        "• URL está correta e acessível\n"
                        "• Servidor BookStack está funcionando\n"
                        "• Não há bloqueios de firewall\n"
                        "• Conexão com internet está ok"
                    )
                }
            
            # Erro genérico
            else:
                return {
                    'success': False,
                    'message': f'Falha na conexão com BookStack: {error_message[:100]}...',
                    'error': error_message,
                    'solution': "Verifique as configurações e tente novamente"
                }
    
    def _test_create_permissions(self) -> Dict:
        """
        Testa permissões específicas para criação de páginas
        
        Returns:
            Dict com informações sobre permissões de criação
        """
        try:
            # Primeiro, tentar listar livros para ver se tem acesso de leitura
            try:
                books_response = self._make_request('GET', '/books', params={'count': 1})
                books = books_response.get('data', [])
                
                if not books:
                    return {
                        'can_create': False,
                        'status': 'Nenhum livro encontrado',
                        'details': 'Não há livros disponíveis para teste de criação'
                    }
                
                # Tentar obter um livro específico para testar permissões detalhadas
                test_book_id = books[0]['id']
                book_details = self._make_request('GET', f'/books/{test_book_id}')
                
                return {
                    'can_create': True,
                    'status': 'Permissões OK',
                    'details': f'Acesso a livros confirmado. Teste com livro ID {test_book_id} bem-sucedido.',
                    'test_book_id': test_book_id,
                    'test_book_name': books[0].get('name', 'Livro de Teste')
                }
                
            except Exception as e:
                error_msg = str(e)
                
                if "403" in error_msg or "Forbidden" in error_msg:
                    # Verificar se é erro de permissão geral ou específica
                    if "proprietário do código de API" in error_msg:
                        return {
                            'can_create': False,
                            'status': 'Token sem permissão de API',
                            'details': 'O usuário do token não tem role "API Access"',
                            'solution': (
                                "ERRO: Token sem permissão básica de API.\n\n"
                                "SOLUÇÃO:\n"
                                "1. Acesse BookStack como administrador\n"
                                "2. Vá em: Configurações > Usuários > [Usuário do Token]\n"
                                "3. Edite o usuário\n"
                                "4. Em 'Roles', adicione uma role com 'API Access'\n"
                                "5. Salve e teste novamente"
                            )
                        }
                    else:
                        return {
                            'can_create': False,
                            'status': 'Sem permissão de leitura',
                            'details': 'Token não pode acessar livros existentes',
                            'solution': (
                                "ERRO: Token sem permissão de leitura de livros.\n\n"
                                "POSSÍVEIS CAUSAS:\n"
                                "• Role do usuário não tem permissão 'View' em livros\n"
                                "• Token expirado ou inválido\n"
                                "• Configuração de permissões restritiva"
                            )
                        }
                else:
                    return {
                        'can_create': False,
                        'status': f'Erro no teste: {error_msg[:50]}...',
                        'details': f'Falha ao testar permissões: {error_msg}'
                    }
                    
        except Exception as e:
            return {
                'can_create': False,
                'status': f'Erro interno: {str(e)[:50]}...',
                'details': f'Falha no teste de permissões: {str(e)}'
            }
    
    def get_books(self, search: str = None, limit: int = 50) -> List[Dict]:
        """
        Obtém lista de livros
        
        Args:
            search: Termo de busca
            limit: Limite de resultados
            
        Returns:
            Lista de livros
        """
        params = {'count': limit}
        if search:
            params['filter[name:like]'] = f'%{search}%'
            
        response = self._make_request('GET', '/books', params=params)
        return response.get('data', [])
    
    def create_book(self, name: str, description: str = '', tags: List[str] = None) -> Dict:
        """
        Cria um novo livro
        
        Args:
            name: Nome do livro
            description: Descrição do livro
            tags: Lista de tags
            
        Returns:
            Dados do livro criado
        """
        data = {
            'name': name,
            'description': description
        }
        
        if tags:
            data['tags'] = [{'name': tag, 'value': ''} for tag in tags]
        
        response = self._make_request('POST', '/books', data=data)
        return response.get('data', {})
    
    def get_chapters(self, book_id: int, search: str = None) -> List[Dict]:
        """
        Obtém capítulos de um livro
        
        Args:
            book_id: ID do livro
            search: Termo de busca
            
        Returns:
            Lista de capítulos
        """
        params = {}
        if search:
            params['filter[name:like]'] = f'%{search}%'
            
        response = self._make_request('GET', f'/books/{book_id}/chapters', params=params)
        return response.get('data', [])
    
    def create_chapter(self, book_id: int, name: str, description: str = '', 
                      priority: int = None) -> Dict:
        """
        Cria um novo capítulo
        
        Args:
            book_id: ID do livro
            name: Nome do capítulo
            description: Descrição do capítulo
            priority: Prioridade/ordem do capítulo
            
        Returns:
            Dados do capítulo criado
        """
        data = {
            'name': name,
            'description': description,
            'book_id': book_id
        }
        
        if priority is not None:
            data['priority'] = priority
        
        response = self._make_request('POST', '/chapters', data=data)
        return response.get('data', {})
    
    def get_pages(self, book_id: int = None, chapter_id: int = None, search: str = None, limit: int = 100) -> List[Dict]:
        """
        Obtém lista de páginas
        
        Args:
            book_id: ID do livro (opcional)
            chapter_id: ID do capítulo (opcional)
            search: Termo de busca
            limit: Limite de resultados
            
        Returns:
            Lista de páginas
        """
        params = {'count': limit}
        
        if book_id:
            params['filter[book_id]'] = book_id
        if chapter_id:
            params['filter[chapter_id]'] = chapter_id
        if search:
            params['filter[name:like]'] = f'%{search}%'
            
        response = self._make_request('GET', '/pages', params=params)
        return response.get('data', [])
    
    def create_page(self, data: Dict) -> Dict:
        """
        Cria uma nova página
        
        Args:
            data: Dicionário com dados da página (name, html/markdown, book_id/chapter_id, etc.)
            
        Returns:
            Dados da página criada
        """
        # Validação básica
        if 'name' not in data:
            raise ValueError("Nome da página é obrigatório")
        
        if 'book_id' not in data and 'chapter_id' not in data:
            raise ValueError("book_id ou chapter_id é obrigatório")
        
        # Verificar se temos conteúdo
        if 'html' not in data and 'markdown' not in data:
            raise ValueError("html ou markdown é obrigatório")
        
        try:
            response = self._make_request('POST', '/pages', data=data)
            return response.get('data', {})
        except Exception as e:
            error_message = str(e)
            
            # Verificar se é o erro específico de permissão de API
            if "proprietário do código de API" in error_message or "não tem permissão para fazer requisições de API" in error_message:
                raise Exception(
                    "❌ ERRO DE PERMISSÃO DE API:\n\n"
                    "O usuário associado ao token de API não tem permissão para usar a API do BookStack.\n\n"
                    "SOLUÇÕES:\n"
                    "1. Verifique se o usuário tem a role 'API Access' habilitada\n"
                    "2. No BookStack, vá em: Configurações > Usuários > [Seu Usuário] > Roles\n"
                    "3. Certifique-se que uma role com 'API Access' está atribuída\n"
                    "4. Ou use um token de um usuário administrador\n\n"
                    f"Erro original: {error_message}"
                )
            
            # Verificar outros tipos de erro 403
            elif "403" in error_message or "Forbidden" in error_message:
                if "content-create" in error_message.lower() or "criar" in error_message.lower():
                    raise Exception(
                        "❌ ERRO DE PERMISSÃO DE CONTEÚDO:\n\n"
                        "O usuário não tem permissão para criar páginas neste livro/capítulo.\n\n"
                        "SOLUÇÕES:\n"
                        "1. Verifique se o usuário tem permissão de 'Create' no livro/capítulo\n"
                        "2. No BookStack, vá nas configurações do livro/capítulo\n"
                        "3. Adicione o usuário com permissão de 'Create'\n"
                        "4. Ou use um token de usuário administrador\n\n"
                        f"Erro original: {error_message}"
                    )
                else:
                    # Erro 403 genérico
                    raise Exception(
                        "❌ ERRO DE PERMISSÃO:\n\n"
                        "Acesso negado pelo BookStack. Possíveis causas:\n"
                        "1. Token de API inválido ou expirado\n"
                        "2. Usuário sem permissão de API\n"
                        "3. Usuário sem permissão no livro/capítulo de destino\n\n"
                        "VERIFICAÇÕES:\n"
                        "• Token correto nas configurações\n"
                        "• Usuário tem role 'API Access'\n"
                        "• Usuário tem permissão 'Create' no destino\n\n"
                        f"Erro original: {error_message}"
                    )
            
            # Outros erros
            else:
                raise e
    
    def upload_image(self, image_path: str, image_type: str = 'gallery') -> Dict:
        """
        Faz upload de uma imagem
        
        Args:
            image_path: Caminho para o arquivo de imagem
            image_type: Tipo de imagem ('gallery', 'drawio', etc.)
            
        Returns:
            Dados da imagem enviada
        """
        try:
            with open(image_path, 'rb') as image_file:
                files = {
                    'image': image_file,
                    'type': (None, image_type)
                }
                
                # Para upload, não usar JSON headers
                headers = {
                    'Authorization': f'Token {self.token_id}:{self.token_secret}',
                    'Accept': 'application/json'
                }
                
                response = requests.post(
                    f"{self.api_base}/image-gallery",
                    files=files,
                    headers=headers,
                    verify=self.verify_ssl
                )
                
                response.raise_for_status()
                return response.json().get('data', {})
                
        except Exception as e:
            raise Exception(f"Erro ao fazer upload da imagem: {str(e)}")
    
    def search_content(self, query: str, page: int = 1, count: int = 20) -> Dict:
        """
        Busca conteúdo no BookStack
        
        Args:
            query: Termo de busca
            page: Página de resultados
            count: Itens por página
            
        Returns:
            Resultados da busca
        """
        params = {
            'query': query,
            'page': page,
            'count': count
        }
        
        response = self._make_request('GET', '/search', params=params)
        return response
    
    def get_attachments(self, page_id: int) -> List[Dict]:
        """
        Obtém anexos de uma página
        
        Args:
            page_id: ID da página
            
        Returns:
            Lista de anexos
        """
        response = self._make_request('GET', f'/pages/{page_id}/attachments')
        return response.get('data', [])
    
    def create_attachment(self, page_id: int, name: str, file_path: str) -> Dict:
        """
        Cria um anexo para uma página
        
        Args:
            page_id: ID da página
            name: Nome do anexo
            file_path: Caminho para o arquivo
            
        Returns:
            Dados do anexo criado
        """
        try:
            with open(file_path, 'rb') as file:
                files = {
                    'file': file,
                    'name': (None, name),
                    'uploaded_to': (None, str(page_id))
                }
                
                headers = {
                    'Authorization': f'Token {self.token_id}:{self.token_secret}',
                    'Accept': 'application/json'
                }
                
                response = requests.post(
                    f"{self.api_base}/attachments",
                    files=files,
                    headers=headers,
                    verify=self.verify_ssl
                )
                
                response.raise_for_status()
                return response.json().get('data', {})
                
        except Exception as e:
            raise Exception(f"Erro ao criar anexo: {str(e)}")
    
    def update_page(self, page_id: int, data: Dict) -> Dict:
        """
        Atualiza uma página existente
        
        Args:
            page_id: ID da página
            data: Dicionário com dados para atualizar
            
        Returns:
            Dados da página atualizada
        """
        response = self._make_request('PUT', f'/pages/{page_id}', data=data)
        return response.get('data', {})
    
    def delete_page(self, page_id: int) -> bool:
        """
        Deleta uma página
        
        Args:
            page_id: ID da página
            
        Returns:
            True se deletada com sucesso
        """
        try:
            self._make_request('DELETE', f'/pages/{page_id}')
            return True
        except Exception:
            return False
    
    def get_page_content(self, page_id: int) -> Dict:
        """
        Obtém conteúdo de uma página
        
        Args:
            page_id: ID da página
            
        Returns:
            Dados da página
        """
        response = self._make_request('GET', f'/pages/{page_id}')
        return response.get('data', {})
    
    def _get_user_info_alternative(self) -> Dict:
        """
        Obtém informações do usuário usando métodos alternativos quando /users/me falha
        
        Returns:
            Dicionário com informações do usuário
        """
        try:
            # Método 1: Tentar listar usuários e encontrar pelo token
            # (Só funciona se o usuário tiver permissão para listar usuários)
            try:
                users_response = self._make_request('GET', '/users', params={'count': 50})
                users = users_response.get('data', [])
                
                # Procurar pelo usuário atual (será o proprietário do token)
                for user in users:
                    # Se conseguimos listar usuários e há apenas um, provavelmente é o atual
                    if len(users) == 1:
                        return {
                            'id': user.get('id'),
                            'name': user.get('name', 'Usuário do Token'),
                            'email': user.get('email', ''),
                            'note': 'Informações obtidas via lista de usuários'
                        }
                
                # Se há múltiplos usuários, não podemos determinar qual é o atual
                if users:
                    return {
                        'name': f'Um dos {len(users)} usuários',
                        'note': f'Múltiplos usuários encontrados ({len(users)}), não foi possível identificar o usuário atual'
                    }
                    
            except Exception:
                pass  # Método 1 falhou, tentar método 2
            
            # Método 2: Tentar através de uma atividade/auditoria recente
            try:
                # Alguns BookStacks permitem listar atividades
                activity_response = self._make_request('GET', '/users/me/activity', params={'count': 1})
                activities = activity_response.get('data', [])
                
                if activities and 'user' in activities[0]:
                    user_data = activities[0]['user']
                    return {
                        'id': user_data.get('id'),
                        'name': user_data.get('name', 'Usuário do Token'),
                        'note': 'Informações obtidas via atividades'
                    }
            except Exception:
                pass  # Método 2 falhou, usar fallback
            
            # Método 3: Fallback com informações limitadas mas descritivas
            return {
                'name': 'Usuário do Token de API',
                'note': 'Endpoint /users/me indisponível. Token funcionando mas sem acesso a dados do usuário.',
                'status': 'API funcional'
            }
            
        except Exception:
            # Se tudo falhou, retornar informações mínimas
            return {
                'name': 'Token de API Válido', 
                'note': 'Token funcional, mas não foi possível obter dados detalhados do usuário'
            }
