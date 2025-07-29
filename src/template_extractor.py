"""
Módulo para extração avançada de templates do MediaWiki
"""

import mwparserfromhell
import re
from typing import Dict, List, Any, Optional

class MediaWikiTemplateExtractor:
    """Extrator de conteúdo de templates do MediaWiki"""
    
    def __init__(self, mediawiki_client):
        self.client = mediawiki_client
        self.template_cache = {}  # Cache para evitar requisições repetidas
        
    def extract_and_expand_templates(self, wikitext: str, page_title: str = "") -> str:
        """
        Extrai templates do wikitext e expande com conteúdo real
        
        Args:
            wikitext: Texto em formato MediaWiki
            page_title: Título da página (para contexto)
            
        Returns:
            Wikitext com templates expandidos
        """
        try:
            # Parse do wikitext
            wikicode = mwparserfromhell.parse(wikitext)
            
            # Encontrar todos os templates
            templates = wikicode.filter_templates()
            
            if not templates:
                return wikitext
            
            print(f"📋 Encontrados {len(templates)} templates na página '{page_title}'")
            
            # Expandir cada template
            expanded_wikitext = str(wikicode)
            
            for template in templates:
                try:
                    expanded_content = self._expand_template(template, page_title)
                    if expanded_content:
                        # Substituir template original pelo conteúdo expandido
                        template_str = str(template)
                        expanded_wikitext = expanded_wikitext.replace(template_str, expanded_content)
                        print(f"✅ Template expandido: {str(template.name).strip()}")
                    else:
                        print(f"⚠️ Template não expandido: {str(template.name).strip()}")
                except Exception as e:
                    print(f"❌ Erro ao expandir template {str(template.name).strip()}: {e}")
                    continue
            
            return expanded_wikitext
            
        except Exception as e:
            print(f"❌ Erro no processamento de templates: {e}")
            return wikitext  # Retorna original se falhar
    
    def _expand_template(self, template, context_page: str = "") -> str:
        """Expande um template individual"""
        template_name = str(template.name).strip()
        
        # Verificar cache primeiro
        if template_name in self.template_cache:
            return self._apply_template_params(self.template_cache[template_name], template)
        
        # Tentar obter conteúdo do template
        template_content = self._get_template_content(template_name)
        
        if template_content:
            # Armazenar no cache
            self.template_cache[template_name] = template_content
            # Aplicar parâmetros
            return self._apply_template_params(template_content, template)
        
        return ""
    
    def _get_template_content(self, template_name: str) -> str:
        """Obtém o conteúdo de um template"""
        # Formatar nome do template
        template_page = f"Template:{template_name}"
        
        try:
            # Método 1: Tentar via API expandtemplates
            expanded = self._expand_via_api(template_name)
            if expanded:
                return expanded
            
            # Método 2: Obter wikitext do template diretamente
            template_wikitext = self._get_template_wikitext(template_page)
            if template_wikitext:
                return template_wikitext
            
            # Método 3: Tentar variações do nome
            variations = self._get_template_name_variations(template_name)
            for variation in variations:
                template_wikitext = self._get_template_wikitext(f"Template:{variation}")
                if template_wikitext:
                    return template_wikitext
            
            return ""
            
        except Exception as e:
            print(f"❌ Erro ao obter template '{template_name}': {e}")
            return ""
    
    def _expand_via_api(self, template_name: str) -> str:
        """Tenta expandir template via API expandtemplates"""
        try:
            params = {
                'action': 'expandtemplates',
                'text': f"{{{{{template_name}}}}}",
                'format': 'json',
                'prop': 'wikitext'
            }
            
            response = self.client._make_request(params)
            
            if 'expandtemplates' in response and 'wikitext' in response['expandtemplates']:
                expanded = response['expandtemplates']['wikitext']
                # Se expandiu para algo diferente do original, é válido
                if expanded != f"{{{{{template_name}}}}}":
                    return expanded
            
            return ""
            
        except Exception as e:
            return ""
    
    def _get_template_wikitext(self, template_page: str) -> str:
        """Obtém wikitext de uma página de template"""
        try:
            content = self.client.get_page_content_wikitext(template_page)
            if content and content.get('wikitext'):
                return content['wikitext']
            return ""
        except Exception as e:
            return ""
    
    def _get_template_name_variations(self, template_name: str) -> List[str]:
        """Gera variações possíveis do nome do template"""
        variations = []
        
        # Versão original
        variations.append(template_name)
        
        # Com primeira letra maiúscula
        variations.append(template_name.capitalize())
        
        # Substituir underscores por espaços
        variations.append(template_name.replace('_', ' '))
        
        # Combinações
        variations.append(template_name.replace('_', ' ').capitalize())
        
        # Remover duplicatas mantendo ordem
        seen = set()
        return [v for v in variations if not (v in seen or seen.add(v))]
    
    def _apply_template_params(self, template_content: str, template) -> str:
        """Aplica parâmetros do template ao conteúdo"""
        try:
            result_content = template_content
            
            # Mapear parâmetros do template
            params = {}
            for i, param in enumerate(template.params):
                param_name = str(param.name).strip()
                param_value = str(param.value).strip()
                
                # Parâmetros nomeados
                if param_name:
                    params[param_name] = param_value
                
                # Parâmetros posicionais (1, 2, 3, ...)
                params[str(i + 1)] = param_value
            
            # Substituir placeholders no conteúdo do template
            # Formato: {{{parametro}}} ou {{{parametro|valor_default}}}
            def replace_param(match):
                param_text = match.group(1)
                
                # Verificar se tem valor default
                if '|' in param_text:
                    param_name, default_value = param_text.split('|', 1)
                    param_name = param_name.strip()
                    default_value = default_value.strip()
                else:
                    param_name = param_text.strip()
                    default_value = ""
                
                # Retornar valor do parâmetro ou default
                return params.get(param_name, default_value)
            
            # Substituir todos os {{{parametro}}}
            result_content = re.sub(r'\{\{\{([^}]+)\}\}\}', replace_param, result_content)
            
            return result_content
            
        except Exception as e:
            print(f"❌ Erro ao aplicar parâmetros: {e}")
            return template_content

class AdvancedMediaWikiConverter:
    """Conversor avançado que inclui expansão de templates"""
    
    def __init__(self, mediawiki_client):
        self.client = mediawiki_client
        self.template_extractor = MediaWikiTemplateExtractor(mediawiki_client)
    
    def get_page_content_with_expanded_templates(self, page_title: str) -> dict:
        """Obtém conteúdo da página com templates expandidos"""
        try:
            # Obter wikitext original
            content = self.client.get_page_content_wikitext(page_title)
            
            if not content or not content.get('wikitext'):
                return content
            
            original_wikitext = content['wikitext']
            print(f"📄 Processando página: {page_title}")
            print(f"📏 Tamanho original: {len(original_wikitext)} caracteres")
            
            # Expandir templates
            expanded_wikitext = self.template_extractor.extract_and_expand_templates(
                original_wikitext, page_title
            )
            
            print(f"📏 Tamanho após expansão: {len(expanded_wikitext)} caracteres")
            
            # Atualizar conteúdo
            content['wikitext'] = expanded_wikitext
            content['templates_expanded'] = True
            
            return content
            
        except Exception as e:
            print(f"❌ Erro ao expandir templates da página '{page_title}': {e}")
            # Retornar conteúdo original se falhar
            return self.client.get_page_content_wikitext(page_title)
    
    def get_page_content_markdown_with_templates(self, page_title: str) -> dict:
        """Obtém página em markdown com templates expandidos"""
        try:
            # Obter conteúdo com templates expandidos
            content = self.get_page_content_with_expanded_templates(page_title)
            
            if not content:
                return None
            
            # Converter para markdown usando o conversor existente
            from .wikitext_parser import convert_wikitext_to_markdown
            
            markdown = convert_wikitext_to_markdown(
                content.get('wikitext', ''),
                page_title,
                content.get('categories', [])
            )
            
            return {
                'title': content.get('title', page_title),
                'markdown': markdown,
                'categories': content.get('categories', []),
                'pageid': content.get('pageid', ''),
                'length': len(markdown),
                'touched': content.get('touched', ''),
                'templates_expanded': content.get('templates_expanded', False)
            }
            
        except Exception as e:
            print(f"❌ Erro ao converter para markdown: {e}")
            # Fallback para método padrão
            return self.client.get_page_content_markdown(page_title)

def create_advanced_converter(mediawiki_client):
    """Factory function para criar conversor avançado"""
    return AdvancedMediaWikiConverter(mediawiki_client)
