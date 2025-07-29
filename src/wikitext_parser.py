"""
Módulo para parsing avançado de wikitext usando mwparserfromhell
"""

import mwparserfromhell
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

class WikitextToMarkdownConverter:
    """Conversor avançado de wikitext para markdown usando mwparserfromhell"""
    
    def __init__(self):
        # Mapear templates conhecidos para conversões específicas
        self.template_converters = {
            'infobox': self._convert_infobox,
            'cite': self._convert_citation,
            'note': self._convert_note,
            'warning': self._convert_warning,
            'code': self._convert_code_template,
            'quote': self._convert_quote,
        }
        
        # Configurações de conversão
        self.config = {
            'preserve_templates': True,
            'convert_links': True,
            'extract_categories': True,
            'process_tables': True,
            'handle_images': True,
        }
    
    def convert(self, wikitext: str, page_title: str = "", categories: List[str] = None) -> str:
        """
        Converte wikitext para markdown usando parsing estruturado
        
        Args:
            wikitext: Texto em formato MediaWiki
            page_title: Título da página
            categories: Lista de categorias da página
        
        Returns:
            String em formato markdown otimizado para BookStack
        """
        if not wikitext.strip():
            return f"# {page_title}\n\n> Conteúdo não disponível"
        
        try:
            # Parse do wikitext
            wikicode = mwparserfromhell.parse(wikitext)
            
            # Processar elementos estruturalmente
            markdown_content = self._process_wikicode(wikicode)
            
            # Criar cabeçalho
            header = self._create_header(page_title, categories)
            
            # Pós-processamento e limpeza
            final_markdown = self._post_process_markdown(markdown_content)
            
            return header + final_markdown
            
        except Exception as e:
            # Fallback para conversão básica se parsing falhar
            return self._fallback_conversion(wikitext, page_title, categories, str(e))
    
    def _process_wikicode(self, wikicode) -> str:
        """Processa o wikicode parseado e converte para markdown"""
        result_parts = []
        
        for node in wikicode.nodes:
            converted = self._convert_node(node)
            if converted:
                result_parts.append(converted)
        
        return '\n'.join(result_parts)
    
    def _convert_node(self, node) -> str:
        """Converte um nó individual do wikicode"""
        
        # Texto simples
        if isinstance(node, mwparserfromhell.nodes.Text):
            return self._clean_text(str(node))
        
        # Cabeçalhos
        elif isinstance(node, mwparserfromhell.nodes.Heading):
            return self._convert_heading(node)
        
        # Templates
        elif isinstance(node, mwparserfromhell.nodes.Template):
            return self._convert_template(node)
        
        # Links
        elif isinstance(node, mwparserfromhell.nodes.Wikilink):
            return self._convert_wikilink(node)
        
        # Links externos
        elif isinstance(node, mwparserfromhell.nodes.ExternalLink):
            return self._convert_external_link(node)
        
        # Tags HTML
        elif isinstance(node, mwparserfromhell.nodes.Tag):
            return self._convert_tag(node)
        
        # Argumentos de template (ignorar)
        elif isinstance(node, mwparserfromhell.nodes.Argument):
            return ""
        
        # Comentários (ignorar)
        elif isinstance(node, mwparserfromhell.nodes.Comment):
            return ""
        
        # Outros tipos
        else:
            return str(node)
    
    def _convert_heading(self, heading) -> str:
        """Converte cabeçalhos wiki para markdown"""
        level = heading.level
        title = str(heading.title).strip()
        
        # Ajustar nível (h1 é reservado para título da página)
        markdown_level = min(level + 1, 6)
        return f"\n{'#' * markdown_level} {title}\n"
    
    def _convert_template(self, template) -> str:
        """Converte templates usando conversores específicos"""
        template_name = str(template.name).strip().lower()
        
        # Tentar encontrar conversor específico
        for pattern, converter in self.template_converters.items():
            if pattern in template_name:
                return converter(template)
        
        # Conversão genérica
        return self._convert_generic_template(template)
    
    def _convert_infobox(self, template) -> str:
        """Converte infoboxes para tabelas markdown"""
        result = ["\n### Informações\n"]
        result.append("| Campo | Valor |")
        result.append("|-------|-------|")
        
        for param in template.params:
            name = str(param.name).strip()
            value = str(param.value).strip()
            
            if name and value:
                # Limpar o valor
                clean_value = self._clean_template_value(value)
                result.append(f"| **{name}** | {clean_value} |")
        
        return '\n'.join(result) + '\n'
    
    def _convert_citation(self, template) -> str:
        """Converte citações para formato markdown"""
        author = ""
        title = ""
        url = ""
        
        for param in template.params:
            name = str(param.name).strip().lower()
            value = str(param.value).strip()
            
            if name in ['author', 'autor']:
                author = value
            elif name in ['title', 'título']:
                title = value
            elif name in ['url', 'link']:
                url = value
        
        if url and title:
            return f"[{title}]({url})"
        elif title:
            return f"*{title}*"
        else:
            return f"[Citação: {str(template)}]"
    
    def _convert_note(self, template) -> str:
        """Converte notas para blockquotes"""
        content = ""
        for param in template.params:
            if str(param.name).strip().isdigit() or not str(param.name).strip():
                content = str(param.value).strip()
                break
        
        return f"\n> **Nota:** {self._clean_template_value(content)}\n"
    
    def _convert_warning(self, template) -> str:
        """Converte avisos para blockquotes com destaque"""
        content = ""
        for param in template.params:
            if str(param.name).strip().isdigit() or not str(param.name).strip():
                content = str(param.value).strip()
                break
        
        return f"\n> ⚠️ **Aviso:** {self._clean_template_value(content)}\n"
    
    def _convert_code_template(self, template) -> str:
        """Converte templates de código para blocos de código"""
        code_content = ""
        language = ""
        
        for param in template.params:
            name = str(param.name).strip().lower()
            value = str(param.value).strip()
            
            if name in ['1', ''] and not code_content:
                code_content = value
            elif name in ['lang', 'language', 'linguagem']:
                language = value
        
        if language:
            return f"\n```{language}\n{code_content}\n```\n"
        else:
            return f"\n```\n{code_content}\n```\n"
    
    def _convert_quote(self, template) -> str:
        """Converte citações para blockquotes"""
        quote_text = ""
        author = ""
        
        for param in template.params:
            name = str(param.name).strip().lower()
            value = str(param.value).strip()
            
            if name in ['1', 'text', 'texto', ''] and not quote_text:
                quote_text = value
            elif name in ['author', 'autor', 'source', 'fonte']:
                author = value
        
        result = f"\n> {self._clean_template_value(quote_text)}"
        if author:
            result += f"\n> \n> — *{author}*"
        result += "\n"
        
        return result
    
    def _convert_generic_template(self, template) -> str:
        """Conversão genérica para templates não reconhecidos"""
        template_name = str(template.name).strip()
        
        # Para templates simples, tentar extrair conteúdo principal
        if template.params:
            first_param = template.params[0]
            param_name = str(first_param.name).strip()
            param_value = str(first_param.value).strip()
            
            # Se o primeiro parâmetro não tem nome (posicional)
            if not param_name or param_name.isdigit():
                return self._clean_template_value(param_value)
        
        # Marcar template não convertido
        return f"[Template: {template_name}]"
    
    def _convert_wikilink(self, link) -> str:
        """Converte links internos wiki"""
        target = str(link.title).strip()
        text = str(link.text).strip() if link.text else target
        
        # Verificar se é link para arquivo/imagem
        if target.lower().startswith(('file:', 'arquivo:', 'image:', 'imagem:')):
            return f"![{text}](#{target})"
        
        # Links para outras páginas - converter para texto em negrito
        # (BookStack não tem o conceito de links internos automáticos)
        return f"**{text}**"
    
    def _convert_external_link(self, link) -> str:
        """Converte links externos"""
        url = str(link.url).strip()
        title = str(link.title).strip() if link.title else url
        
        return f"[{title}]({url})"
    
    def _convert_tag(self, tag) -> str:
        """Converte tags HTML"""
        tag_name = str(tag.tag).lower()
        contents = str(tag.contents) if tag.contents else ""
        
        # Conversões específicas por tag
        if tag_name == 'code':
            return f"`{contents}`"
        elif tag_name == 'pre':
            return f"\n```\n{contents}\n```\n"
        elif tag_name == 'blockquote':
            return f"\n> {contents}\n"
        elif tag_name == 'strong' or tag_name == 'b':
            return f"**{contents}**"
        elif tag_name == 'em' or tag_name == 'i':
            return f"*{contents}*"
        elif tag_name == 'br':
            return "\n"
        elif tag_name in ['p', 'div']:
            return f"\n{contents}\n"
        elif tag_name.startswith('h') and len(tag_name) == 2 and tag_name[1].isdigit():
            level = int(tag_name[1])
            return f"\n{'#' * min(level + 1, 6)} {contents}\n"
        else:
            # Para outras tags, retornar apenas o conteúdo
            return contents
    
    def _clean_text(self, text: str) -> str:
        """Limpa texto simples"""
        # Remover quebras de linha excessivas
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        return text
    
    def _clean_template_value(self, value: str) -> str:
        """Limpa valores de templates para markdown"""
        # Parse recursivo se necessário
        try:
            if '{{' in value or '[[' in value:
                sub_wikicode = mwparserfromhell.parse(value)
                return self._process_wikicode(sub_wikicode)
        except:
            pass
        
        # Limpeza básica
        value = re.sub(r'<[^>]+>', '', value)  # Remover HTML
        value = re.sub(r'\s+', ' ', value)     # Normalizar espaços
        return value.strip()
    
    def _create_header(self, title: str, categories: List[str] = None) -> str:
        """Cria cabeçalho da página em markdown"""
        header = f"# {title}\n\n"
        header += f"> **Conteúdo extraído do MediaWiki**  \n"
        header += f"> Data de extração: {datetime.now().strftime('%d/%m/%Y às %H:%M')}  \n\n"
        
        if categories:
            header += f"**Categorias:** {', '.join(categories)}\n\n"
            header += "---\n\n"
        
        return header
    
    def _post_process_markdown(self, markdown: str) -> str:
        """Pós-processamento final do markdown"""
        # Limpar quebras de linha excessivas
        markdown = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown)
        
        # Garantir que cabeçalhos tenham espaço antes e depois
        markdown = re.sub(r'([^\n])\n(#{1,6}\s)', r'\1\n\n\2', markdown)
        markdown = re.sub(r'(#{1,6}[^\n]+)\n([^\n#])', r'\1\n\n\2', markdown)
        
        return markdown.strip()
    
    def _fallback_conversion(self, wikitext: str, title: str, categories: List[str], error: str) -> str:
        """Conversão de fallback se o parsing falhar"""
        header = self._create_header(title, categories)
        content = f"\n> ⚠️ **Aviso:** Erro no parsing avançado: {error}\n"
        content += f"> Usando conversão básica.\n\n"
        
        # Conversão básica com regex (método anterior)
        basic_conversion = self._basic_regex_conversion(wikitext)
        
        return header + content + basic_conversion
    
    def _basic_regex_conversion(self, wikitext: str) -> str:
        """Conversão básica usando regex (fallback)"""
        import re
        
        markdown = wikitext
        
        # Conversões básicas com regex
        markdown = re.sub(r'^======\s*(.*?)\s*======', r'###### \1', markdown, flags=re.MULTILINE)
        markdown = re.sub(r'^=====\s*(.*?)\s*=====', r'##### \1', markdown, flags=re.MULTILINE)
        markdown = re.sub(r'^====\s*(.*?)\s*====', r'#### \1', markdown, flags=re.MULTILINE)
        markdown = re.sub(r'^===\s*(.*?)\s*===', r'### \1', markdown, flags=re.MULTILINE)
        markdown = re.sub(r'^==\s*(.*?)\s*==', r'## \1', markdown, flags=re.MULTILINE)
        
        markdown = re.sub(r"'''(.*?)'''", r'**\1**', markdown, flags=re.DOTALL)
        markdown = re.sub(r"''(.*?)''", r'*\1*', markdown, flags=re.DOTALL)
        
        return markdown.strip()

# Função utilitária para uso simples
def convert_wikitext_to_markdown(wikitext: str, title: str = "", categories: List[str] = None) -> str:
    """
    Função utilitária para conversão rápida de wikitext para markdown
    
    Args:
        wikitext: Texto em formato MediaWiki
        title: Título da página
        categories: Lista de categorias
    
    Returns:
        String em formato markdown
    """
    converter = WikitextToMarkdownConverter()
    return converter.convert(wikitext, title, categories)
