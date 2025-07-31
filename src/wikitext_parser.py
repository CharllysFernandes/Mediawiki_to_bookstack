"""
Módulo para parsing de wikitext usando mwparserfromhell
"""

import mwparserfromhell
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

class WikitextParser:
    """Parser de wikitext usando mwparserfromhell"""
    
    def __init__(self):
        # Configurações de parsing
        self.config = {
            'extract_categories': True,
            'process_templates': True,
            'clean_output': True,
        }
    
    
    def parse_wikitext(self, wikitext: str, page_title: str = "", categories: List[str] = None) -> Dict[str, Any]:
        """
        Parse wikitext e extrai informações estruturadas
        
        Args:
            wikitext: Texto em formato MediaWiki
            page_title: Título da página
            categories: Lista de categorias da página
        
        Returns:
            Dict com informações extraídas do wikitext
        """
        if not wikitext.strip():
            return {
                'title': page_title,
                'content': "",
                'categories': categories or [],
                'templates': [],
                'links': [],
                'sections': []
            }
        
        try:
            # Parse do wikitext
            wikicode = mwparserfromhell.parse(wikitext)
            
            # Extrair informações estruturalmente
            parsed_data = self._extract_wikicode_data(wikicode)
            
            # Adicionar metadados
            parsed_data['title'] = page_title
            parsed_data['categories'] = categories or []
            parsed_data['timestamp'] = datetime.now().isoformat()
            
            return parsed_data
            
        except Exception as e:
            # Fallback para parsing básico se falhar
            return self._fallback_parsing(wikitext, page_title, categories, str(e))
    
    def _extract_wikicode_data(self, wikicode) -> Dict[str, Any]:
        """Extrai dados estruturados do wikicode parseado"""
        data = {
            'content': str(wikicode),
            'templates': [],
            'links': [],
            'sections': [],
            'images': []
        }
        
        # Extrair templates
        for template in wikicode.filter_templates():
            template_data = {
                'name': str(template.name).strip(),
                'params': {}
            }
            for param in template.params:
                param_name = str(param.name).strip()
                param_value = str(param.value).strip()
                template_data['params'][param_name] = param_value
            data['templates'].append(template_data)
        
        # Extrair links
        for link in wikicode.filter_wikilinks():
            link_data = {
                'target': str(link.title).strip(),
                'text': str(link.text).strip() if link.text else str(link.title).strip()
            }
            data['links'].append(link_data)
        
        # Extrair seções/cabeçalhos
        for heading in wikicode.filter_headings():
            section_data = {
                'level': heading.level,
                'title': str(heading.title).strip()
            }
            data['sections'].append(section_data)
        
        return data
    
    def clean_wikitext(self, wikitext: str) -> str:
        """Limpa wikitext removendo elementos indesejados"""
        if not self.config.get('clean_output', False):
            return wikitext
        
        try:
            wikicode = mwparserfromhell.parse(wikitext)
            
            # Remover comentários
            for comment in wikicode.filter_comments():
                wikicode.remove(comment)
            
            # Limpar texto resultante
            cleaned = str(wikicode)
            
            # Remover quebras de linha excessivas
            cleaned = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned)
            
            return cleaned.strip()
            
        except Exception:
            # Fallback para limpeza básica
            return self._basic_clean(wikitext)
    
    def _basic_clean(self, wikitext: str) -> str:
        """Limpeza básica usando regex"""
        # Remover comentários HTML
        wikitext = re.sub(r'<!--.*?-->', '', wikitext, flags=re.DOTALL)
        
        # Normalizar quebras de linha
        wikitext = re.sub(r'\n\s*\n\s*\n+', '\n\n', wikitext)
        
        return wikitext.strip()
    
    def _fallback_parsing(self, wikitext: str, title: str, categories: List[str], error: str) -> Dict[str, Any]:
        """Parsing de fallback se o parsing avançado falhar"""
        return {
            'title': title,
            'content': wikitext,
            'categories': categories or [],
            'templates': [],
            'links': [],
            'sections': [],
            'images': [],
            'parse_error': error,
            'timestamp': datetime.now().isoformat()
        }

# Função utilitária para uso simples
def parse_wikitext(wikitext: str, title: str = "", categories: List[str] = None) -> Dict[str, Any]:
    """
    Função utilitária para parsing rápido de wikitext
    
    Args:
        wikitext: Texto em formato MediaWiki
        title: Título da página
        categories: Lista de categorias
    
    Returns:
        Dict com dados extraídos do wikitext
    """
    parser = WikitextParser()
    return parser.parse_wikitext(wikitext, title, categories)
