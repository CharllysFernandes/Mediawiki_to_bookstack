import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class PagesCache:
    """Gerencia cache de páginas da wiki para melhorar performance"""
    
    def __init__(self, cache_file: str = "config/pages_cache.json"):
        self.cache_file = cache_file
        self.pages_data = []
        self.last_updated = None
        self.load_cache()
    
    def load_cache(self) -> bool:
        """Carrega o cache do arquivo JSON"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.pages_data = data.get('pages', [])
                    self.last_updated = data.get('last_updated')
                    return True
            return False
        except Exception as e:
            print(f"Erro ao carregar cache: {e}")
            return False
    
    def save_cache(self) -> bool:
        """Salva o cache no arquivo JSON"""
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            
            cache_data = {
                'last_updated': datetime.now().isoformat(),
                'total_pages': len(self.pages_data),
                'pages': self.pages_data
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.last_updated = cache_data['last_updated']
            return True
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
            return False
    
    def update_pages_from_api(self, api_pages: List[Dict]) -> int:
        """Atualiza o cache com páginas da API, preservando status existente"""
        # Criar dicionário de páginas existentes por ID para lookup rápido
        existing_pages = {page['pageid']: page for page in self.pages_data}
        
        updated_pages = []
        new_count = 0
        
        for api_page in api_pages:
            pageid = api_page.get('pageid')
            title = api_page.get('title', '')
            
            # Se página já existe, preservar status
            if pageid in existing_pages:
                existing_page = existing_pages[pageid]
                updated_page = {
                    'pageid': pageid,
                    'title': title,
                    'link': f"index.php?curid={pageid}",
                    'status': existing_page.get('status', 0),  # Preservar status
                    'last_processed': existing_page.get('last_processed'),
                    'error_message': existing_page.get('error_message')
                }
            else:
                # Nova página
                updated_page = {
                    'pageid': pageid,
                    'title': title,
                    'link': f"index.php?curid={pageid}",
                    'status': 0,  # Não processada
                    'last_processed': None,
                    'error_message': None
                }
                new_count += 1
            
            updated_pages.append(updated_page)
        
        self.pages_data = updated_pages
        return new_count
    
    def get_pages_by_status(self, status: int) -> List[Dict]:
        """Retorna páginas filtradas por status"""
        return [page for page in self.pages_data if page.get('status') == status]
    
    def get_pending_pages(self) -> List[Dict]:
        """Retorna páginas não processadas (status = 0)"""
        return self.get_pages_by_status(0)
    
    def get_processed_pages(self) -> List[Dict]:
        """Retorna páginas processadas (status = 1)"""
        return self.get_pages_by_status(1)
    
    def update_page_status(self, pageid: int, status: int, error_message: str = None) -> bool:
        """Atualiza o status de uma página específica"""
        for page in self.pages_data:
            if page.get('pageid') == pageid:
                page['status'] = status
                page['last_processed'] = datetime.now().isoformat()
                if error_message:
                    page['error_message'] = error_message
                elif status == 1:  # Sucesso - limpar erro anterior
                    page['error_message'] = None
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do cache"""
        total = len(self.pages_data)
        pending = len(self.get_pending_pages())
        processed = len(self.get_processed_pages())
        
        return {
            'total_pages': total,
            'pending_pages': pending,
            'processed_pages': processed,
            'progress_percentage': (processed / total * 100) if total > 0 else 0,
            'last_updated': self.last_updated
        }
    
    def search_pages(self, search_term: str) -> List[Dict]:
        """Busca páginas por termo no título"""
        search_term = search_term.lower()
        return [
            page for page in self.pages_data 
            if search_term in page.get('title', '').lower()
        ]
    
    def reset_all_status(self):
        """Reseta o status de todas as páginas para 0 (não processado)"""
        for page in self.pages_data:
            page['status'] = 0
            page['last_processed'] = None
            page['error_message'] = None
    
    def mark_pages_as_processed(self, pageids: List[int]):
        """Marca múltiplas páginas como processadas"""
        for pageid in pageids:
            self.update_page_status(pageid, 1)
    
    def get_page_by_id(self, pageid: int) -> Optional[Dict]:
        """Retorna uma página específica por ID"""
        for page in self.pages_data:
            if page.get('pageid') == pageid:
                return page
        return None
    
    def remove_deleted_pages(self, current_pageids: List[int]):
        """Remove páginas que não existem mais na wiki"""
        current_ids_set = set(current_pageids)
        self.pages_data = [
            page for page in self.pages_data 
            if page.get('pageid') in current_ids_set
        ]
