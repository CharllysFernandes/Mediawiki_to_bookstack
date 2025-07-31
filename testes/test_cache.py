#!/usr/bin/env python3
"""
Teste do sistema de cache de páginas
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pages_cache import PagesCache

def test_cache():
    """Testa o sistema de cache"""
    print("🔄 Testando sistema de cache de páginas...")
    
    # Criar instância do cache
    cache = PagesCache("config/test_cache.json")
    
    # Simular páginas da API
    mock_pages = [
        {"pageid": 1, "title": "Página de Teste 1"},
        {"pageid": 2, "title": "Página de Teste 2"},
        {"pageid": 3, "title": "Página de Teste 3"},
    ]
    
    # Atualizar cache
    new_count = cache.update_pages_from_api(mock_pages)
    print(f"✅ {new_count} páginas adicionadas ao cache")
    
    # Salvar cache
    if cache.save_cache():
        print("✅ Cache salvo com sucesso")
    else:
        print("❌ Erro ao salvar cache")
    
    # Verificar estatísticas
    stats = cache.get_statistics()
    print(f"📊 Estatísticas:")
    print(f"   Total: {stats['total_pages']}")
    print(f"   Pendentes: {stats['pending_pages']}")
    print(f"   Processadas: {stats['processed_pages']}")
    print(f"   Progresso: {stats['progress_percentage']:.1f}%")
    
    # Testar atualização de status
    cache.update_page_status(1, 1)  # Marcar primeira página como processada
    cache.save_cache()
    
    # Verificar estatísticas novamente
    stats = cache.get_statistics()
    print(f"📊 Após processar uma página:")
    print(f"   Pendentes: {stats['pending_pages']}")
    print(f"   Processadas: {stats['processed_pages']}")
    print(f"   Progresso: {stats['progress_percentage']:.1f}%")
    
    print("✅ Teste do cache concluído!")

if __name__ == "__main__":
    test_cache()
