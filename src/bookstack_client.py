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
            raise Exception(f"Erro na requisição para BookStack: {str(e)}")
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
            
            return {
                'success': True,
                'message': 'Conexão com BookStack estabelecida com sucesso',
                'user_info': response.get('data', {}),
                'api_version': response.get('version', 'desconhecida')
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Falha na conexão com BookStack: {str(e)}',
                'error': str(e)
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
    
    def create_page(self, book_id: int, name: str, html_content: str = '', 
                   markdown_content: str = '', chapter_id: int = None,
                   tags: List[str] = None, priority: int = None) -> Dict:
        """
        Cria uma nova página
        
        Args:
            book_id: ID do livro
            name: Nome da página
            html_content: Conteúdo em HTML
            markdown_content: Conteúdo em Markdown
            chapter_id: ID do capítulo (opcional)
            tags: Lista de tags
            priority: Prioridade/ordem da página
            
        Returns:
            Dados da página criada
        """
        data = {
            'name': name,
            'book_id': book_id
        }
        
        # Preferir HTML se ambos fornecidos
        if html_content:
            data['html'] = html_content
        elif markdown_content:
            data['markdown'] = markdown_content
        
        if chapter_id:
            data['chapter_id'] = chapter_id
            
        if tags:
            data['tags'] = [{'name': tag, 'value': ''} for tag in tags]
            
        if priority is not None:
            data['priority'] = priority
        
        response = self._make_request('POST', '/pages', data=data)
        return response.get('data', {})
    
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
    
    def update_page(self, page_id: int, name: str = None, html_content: str = None,
                   markdown_content: str = None, tags: List[str] = None) -> Dict:
        """
        Atualiza uma página existente
        
        Args:
            page_id: ID da página
            name: Novo nome da página
            html_content: Novo conteúdo em HTML
            markdown_content: Novo conteúdo em Markdown
            tags: Nova lista de tags
            
        Returns:
            Dados da página atualizada
        """
        data = {}
        
        if name:
            data['name'] = name
        
        if html_content:
            data['html'] = html_content
        elif markdown_content:
            data['markdown'] = markdown_content
            
        if tags:
            data['tags'] = [{'name': tag, 'value': ''} for tag in tags]
        
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
