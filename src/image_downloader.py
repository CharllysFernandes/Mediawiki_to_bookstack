"""
Sistema de Download de Imagens do MediaWiki
Extrai e salva imagens referenciadas nas páginas
"""

import os
import re
import requests
import urllib.parse
from urllib.parse import urljoin, urlparse
from pathlib import Path
import mimetypes
from typing import List, Dict, Tuple, Optional
import time

class MediaWikiImageDownloader:
    """Downloader de imagens do MediaWiki"""
    
    def __init__(self, mediawiki_client, base_url: str = None):
        """
        Inicializa o downloader de imagens
        
        Args:
            mediawiki_client: Cliente MediaWiki configurado
            base_url: URL base da wiki (ex: https://wiki.exemplo.com)
        """
        self.client = mediawiki_client
        self.session = mediawiki_client.session
        
        # Determinar URL base da wiki
        if base_url:
            self.base_url = base_url.rstrip('/')
        else:
            # Tentar extrair da URL da API
            api_url = mediawiki_client.api_url
            self.base_url = api_url.replace('/api.php', '').rstrip('/')
        
        # Configurações de download
        self.timeout = 30
        self.max_retries = 3
        self.delay_between_downloads = 0.5
        
        # Extensões de imagem suportadas
        self.image_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', 
            '.svg', '.tiff', '.tif', '.ico', '.pdf'
        }
        
        # Cache de URLs de imagens já processadas
        self.image_url_cache = {}
        
    def extract_images_from_wikitext(self, wikitext: str) -> List[str]:
        """
        Extrai nomes de arquivos de imagem do wikitext
        
        Args:
            wikitext: Texto wiki da página
            
        Returns:
            Lista de nomes de arquivos de imagem
        """
        image_names = []
        
        # Padrões para encontrar imagens no wikitext
        patterns = [
            # [[Arquivo:nome.ext]]
            r'\[\[(?:Arquivo|File|Image|Imagem):([^\]|]+?)(?:\|[^\]]*?)?\]\]',
            # [[File:nome.ext|thumb|...]]
            r'\[\[(?:File|Image):([^\]|]+?)(?:\|[^\]]*?)?\]\]',
            # {{Arquivo|nome.ext}}
            r'\{\{(?:Arquivo|File|Image|Imagem):([^}|]+?)(?:\|[^}]*?)?\}\}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, wikitext, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Limpar o nome do arquivo
                filename = match.strip()
                
                # Verificar se tem extensão de imagem
                if self._is_image_file(filename):
                    image_names.append(filename)
        
        # Remover duplicatas mantendo ordem
        seen = set()
        unique_images = []
        for img in image_names:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)
        
        return unique_images
    
    def extract_images_from_html(self, html_content: str) -> List[str]:
        """
        Extrai URLs de imagens do HTML renderizado
        
        Args:
            html_content: Conteúdo HTML da página
            
        Returns:
            Lista de URLs de imagens
        """
        image_urls = []
        
        # Padrões para encontrar imagens no HTML
        patterns = [
            # <img src="...">
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',
            # <a href="...image...">
            r'<a[^>]+href=["\']([^"\']+\.(?:jpg|jpeg|png|gif|bmp|webp|svg))["\'][^>]*>',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                # Normalizar URL
                if match.startswith('//'):
                    url = 'https:' + match
                elif match.startswith('/'):
                    url = self.base_url + match
                elif not match.startswith('http'):
                    url = urljoin(self.base_url + '/', match)
                else:
                    url = match
                
                if self._is_image_url(url):
                    image_urls.append(url)
        
        return list(set(image_urls))  # Remover duplicatas
    
    def get_image_info(self, filename: str) -> Optional[Dict]:
        """
        Obtém informações de uma imagem via API
        
        Args:
            filename: Nome do arquivo (ex: "exemplo.jpg")
            
        Returns:
            Dicionário com informações da imagem ou None
        """
        try:
            # Garantir que tem prefixo File:
            if not filename.startswith(('File:', 'Arquivo:', 'Image:', 'Imagem:')):
                filename = f"File:{filename}"
            
            params = {
                'action': 'query',
                'titles': filename,
                'prop': 'imageinfo',
                'iiprop': 'url|size|mime|timestamp',
                'format': 'json'
            }
            
            response = self.client._make_request(params)
            
            if 'query' in response and 'pages' in response['query']:
                for page_id, page_data in response['query']['pages'].items():
                    if page_id != '-1' and 'imageinfo' in page_data:
                        image_info = page_data['imageinfo'][0]
                        return {
                            'title': page_data.get('title', filename),
                            'url': image_info.get('url', ''),
                            'width': image_info.get('width', 0),
                            'height': image_info.get('height', 0),
                            'size': image_info.get('size', 0),
                            'mime': image_info.get('mime', ''),
                            'timestamp': image_info.get('timestamp', ''),
                            'filename': filename
                        }
            
            return None
            
        except Exception as e:
            print(f"❌ Erro ao obter info da imagem {filename}: {str(e)}")
            return None
    
    def download_image(self, image_url: str, output_path: str) -> bool:
        """
        Faz download de uma imagem
        
        Args:
            image_url: URL da imagem
            output_path: Caminho onde salvar
            
        Returns:
            True se sucesso, False caso contrário
        """
        try:
            # Tentar download com retry
            for attempt in range(self.max_retries):
                try:
                    response = self.session.get(
                        image_url, 
                        timeout=self.timeout,
                        stream=True
                    )
                    response.raise_for_status()
                    
                    # Verificar se é realmente uma imagem
                    content_type = response.headers.get('content-type', '').lower()
                    if not any(img_type in content_type for img_type in 
                              ['image/', 'application/pdf']):
                        print(f"⚠️ URL não é uma imagem: {image_url}")
                        return False
                    
                    # Criar diretório se não existe
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Salvar arquivo
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    print(f"✅ Imagem salva: {os.path.basename(output_path)}")
                    return True
                    
                except requests.exceptions.RequestException as e:
                    if attempt < self.max_retries - 1:
                        print(f"⚠️ Tentativa {attempt + 1} falhou, tentando novamente...")
                        time.sleep(1)
                        continue
                    else:
                        raise e
                        
        except Exception as e:
            print(f"❌ Erro ao baixar {image_url}: {str(e)}")
            return False
    
    def download_page_images(self, page_title: str, page_content: Dict, 
                           output_dir: str) -> Dict:
        """
        Baixa todas as imagens de uma página
        
        Args:
            page_title: Título da página
            page_content: Conteúdo da página (dict com wikitext/html)
            output_dir: Diretório de saída
            
        Returns:
            Estatísticas do download
        """
        print(f"\n🖼️ Processando imagens da página: {page_title}")
        
        # Criar diretório para imagens da página
        safe_title = self._sanitize_filename(page_title)
        page_images_dir = os.path.join(output_dir, "images", safe_title)
        
        stats = {
            'total_found': 0,
            'downloaded': 0,
            'failed': 0,
            'skipped': 0,
            'image_files': [],
            'errors': []
        }
        
        all_images = set()
        
        # Extrair imagens do wikitext
        if 'wikitext' in page_content:
            wikitext_images = self.extract_images_from_wikitext(page_content['wikitext'])
            all_images.update(wikitext_images)
            print(f"   📝 Wikitext: {len(wikitext_images)} imagens encontradas")
        
        # Extrair imagens do HTML
        if 'html' in page_content:
            html_images = self.extract_images_from_html(page_content['html'])
            all_images.update(html_images)
            print(f"   🌐 HTML: {len(html_images)} imagens encontradas")
        
        stats['total_found'] = len(all_images)
        
        if not all_images:
            print("   ℹ️ Nenhuma imagem encontrada nesta página")
            return stats
        
        print(f"   🎯 Total de {len(all_images)} imagens únicas para download")
        
        # Processar cada imagem
        for i, image_ref in enumerate(all_images, 1):
            print(f"   📥 [{i}/{len(all_images)}] Processando: {image_ref}")
            
            try:
                # Determinar se é nome de arquivo ou URL
                if image_ref.startswith('http'):
                    # É uma URL direta
                    image_url = image_ref
                    filename = os.path.basename(urlparse(image_url).path)
                    if not filename or '.' not in filename:
                        filename = f"image_{i}.jpg"
                else:
                    # É nome de arquivo, obter URL via API
                    image_info = self.get_image_info(image_ref)
                    if not image_info or not image_info.get('url'):
                        print(f"      ⚠️ Não foi possível obter URL para: {image_ref}")
                        stats['failed'] += 1
                        stats['errors'].append(f"URL não encontrada: {image_ref}")
                        continue
                    
                    image_url = image_info['url']
                    filename = self._sanitize_filename(image_ref)
                
                # Determinar extensão
                if not self._has_image_extension(filename):
                    # Tentar determinar extensão pela URL ou content-type
                    ext = self._guess_extension(image_url)
                    if ext:
                        filename += ext
                    else:
                        filename += '.jpg'  # Fallback
                
                # Caminho de saída
                output_path = os.path.join(page_images_dir, filename)
                
                # Verificar se já existe
                if os.path.exists(output_path):
                    print(f"      ⏭️ Arquivo já existe, pulando...")
                    stats['skipped'] += 1
                    stats['image_files'].append(filename)
                    continue
                
                # Fazer download
                if self.download_image(image_url, output_path):
                    stats['downloaded'] += 1
                    stats['image_files'].append(filename)
                else:
                    stats['failed'] += 1
                    stats['errors'].append(f"Falha no download: {image_ref}")
                
                # Delay entre downloads
                if i < len(all_images):
                    time.sleep(self.delay_between_downloads)
                    
            except Exception as e:
                print(f"      ❌ Erro processando {image_ref}: {str(e)}")
                stats['failed'] += 1
                stats['errors'].append(f"Erro: {image_ref} - {str(e)}")
        
        # Relatório final da página
        print(f"   📊 Resultado: {stats['downloaded']} baixadas, "
              f"{stats['failed']} falharam, {stats['skipped']} puladas")
        
        return stats
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza nome de arquivo para filesystem"""
        # Remover caracteres inválidos
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        filename = re.sub(invalid_chars, '_', filename)
        
        # Remover prefixos wiki
        filename = re.sub(r'^(?:File|Arquivo|Image|Imagem):', '', filename, flags=re.IGNORECASE)
        
        # Substituir espaços e múltiplos underscores
        filename = re.sub(r'[_\s]+', '_', filename)
        
        # Remover underscores do início e fim
        filename = filename.strip('_')
        
        # Limitar tamanho
        if len(filename) > 200:
            name, ext = os.path.splitext(filename)
            filename = name[:200-len(ext)] + ext
        
        return filename or "image"
    
    def _is_image_file(self, filename: str) -> bool:
        """Verifica se arquivo tem extensão de imagem"""
        return self._has_image_extension(filename)
    
    def _has_image_extension(self, filename: str) -> bool:
        """Verifica se filename tem extensão de imagem"""
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.image_extensions
    
    def _is_image_url(self, url: str) -> bool:
        """Verifica se URL parece ser de uma imagem"""
        # Verificar extensão na URL
        parsed = urlparse(url.lower())
        ext = os.path.splitext(parsed.path)[1]
        
        if ext in self.image_extensions:
            return True
        
        # URLs de upload do MediaWiki geralmente contêm estas palavras
        return any(keyword in url.lower() for keyword in [
            '/upload/', '/images/', '/thumb/', '/media/'
        ])
    
    def _guess_extension(self, url: str) -> Optional[str]:
        """Tenta adivinhar extensão da imagem pela URL"""
        parsed = urlparse(url.lower())
        ext = os.path.splitext(parsed.path)[1]
        
        if ext in self.image_extensions:
            return ext
        
        # Tentar determinar pelo MIME type
        try:
            response = self.session.head(url, timeout=10)
            content_type = response.headers.get('content-type', '').lower()
            
            mime_to_ext = {
                'image/jpeg': '.jpg',
                'image/jpg': '.jpg', 
                'image/png': '.png',
                'image/gif': '.gif',
                'image/bmp': '.bmp',
                'image/webp': '.webp',
                'image/svg+xml': '.svg',
                'image/tiff': '.tif',
                'application/pdf': '.pdf'
            }
            
            for mime, extension in mime_to_ext.items():
                if mime in content_type:
                    return extension
                    
        except:
            pass
        
        return None
