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
        
        # Otimização: Índices para acesso rápido O(1)
        self._pages_by_id = {}      # {pageid: page_dict}
        self._pages_by_status = {}  # {status: [page_dict, ...]}
        self._indices_built = False
        
        self.load_cache()
    
    def _build_indices(self):
        """Constrói índices para acesso rápido"""
        self._pages_by_id.clear()
        self._pages_by_status.clear()
        
        for page in self.pages_data:
            page_id = page.get('pageid')
            status = page.get('status', 0)
            
            # Índice por ID
            if page_id:
                self._pages_by_id[page_id] = page
            
            # Índice por status
            if status not in self._pages_by_status:
                self._pages_by_status[status] = []
            self._pages_by_status[status].append(page)
        
        self._indices_built = True
    
    def _ensure_indices(self):
        """Garante que os índices estão construídos"""
        if not self._indices_built:
            self._build_indices()
    
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
        # Reconstruir índices após atualização
        self._build_indices()
        return new_count
    
    def get_pages_by_status(self, status: int) -> List[Dict]:
        """Retorna páginas filtradas por status (otimizado com índices)"""
        self._ensure_indices()
        return self._pages_by_status.get(status, []).copy()  # Retorna cópia para segurança
    
    def get_pending_pages(self) -> List[Dict]:
        """Retorna páginas não processadas (status = 0) - otimizado"""
        return self.get_pages_by_status(0)
    
    def get_processed_pages(self) -> List[Dict]:
        """Retorna páginas processadas (status = 1) - otimizado"""
        return self.get_pages_by_status(1)
    
    def update_page_status(self, pageid: int, status: int, error_message: str = None) -> bool:
        """Atualiza o status de uma página específica (otimizado com índice)"""
        self._ensure_indices()
        
        # Busca rápida O(1) usando índice
        page = self._pages_by_id.get(pageid)
        if page:
            old_status = page.get('status', 0)
            
            # Atualizar dados
            page['status'] = status
            page['last_processed'] = datetime.now().isoformat()
            if error_message:
                page['error_message'] = error_message
            elif status == 1:  # Sucesso - limpar erro anterior
                page['error_message'] = None
            
            # Atualizar índices apenas se status mudou
            if old_status != status:
                # Remover da lista do status antigo
                if old_status in self._pages_by_status:
                    self._pages_by_status[old_status] = [
                        p for p in self._pages_by_status[old_status] if p.get('pageid') != pageid
                    ]
                
                # Adicionar na lista do novo status
                if status not in self._pages_by_status:
                    self._pages_by_status[status] = []
                self._pages_by_status[status].append(page)
            
            return True
        return False
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do cache (otimizado)"""
        self._ensure_indices()
        
        total = len(self.pages_data)
        # Usar índices para contagem rápida
        pending = len(self._pages_by_status.get(0, []))
        processed = len(self._pages_by_status.get(1, []))
        
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
        
        # Reconstruir índices após reset
        self._build_indices()
    
    def mark_pages_as_processed(self, pageids: List[int]):
        """Marca múltiplas páginas como processadas (otimizado)"""
        self._ensure_indices()
        
        for pageid in pageids:
            self.update_page_status(pageid, 1)
    
    def get_page_by_id(self, pageid: int) -> Optional[Dict]:
        """Retorna uma página específica por ID (otimizado com índice)"""
        self._ensure_indices()
        return self._pages_by_id.get(pageid)
    
    def remove_deleted_pages(self, current_pageids: List[int]):
        """Remove páginas que não existem mais na wiki"""
        current_ids_set = set(current_pageids)
        self.pages_data = [
            page for page in self.pages_data 
            if page.get('pageid') in current_ids_set
        ]
        
        # Reconstruir índices após remoção
        self._build_indices()
