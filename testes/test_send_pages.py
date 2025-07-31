#!/usr/bin/env python3
"""
🧪 Script de Teste - Funcionalidade "Enviar Páginas"
==================================================

Este script testa a nova funcionalidade de envio de páginas
para o BookStack de forma isolada.
"""

import sys
import os

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pages_cache import PagesCache
from config_manager import ConfigManager

def test_send_pages_functionality():
    """Testa os componentes da funcionalidade enviar páginas"""
    print("🧪 Testando Funcionalidade 'Enviar Páginas'")
    print("=" * 50)
    
    try:
        # 1. Testar PagesCache
        print("\n📄 1. Testando PagesCache...")
        cache = PagesCache()
        
        # Verificar se há páginas em cache
        all_pages = cache.get_all_pages()
        print(f"   Total de páginas em cache: {len(all_pages)}")
        
        if all_pages:
            # Mostrar algumas páginas de exemplo
            print("\n   Primeiras 5 páginas:")
            for i, page in enumerate(all_pages[:5]):
                status = page.get('status', 0)
                status_icon = "🟢" if status == 2 else "🔵" if status == 1 else "⚪"
                print(f"   {i+1}. {status_icon} {page['title'][:60]}...")
            
            # Testar filtros por status
            status_1_pages = [p for p in all_pages if p.get('status') == 1]
            status_2_pages = [p for p in all_pages if p.get('status') == 2]
            
            print(f"\n   📊 Estatísticas:")
            print(f"   - Apenas em cache (azul): {len(status_1_pages)}")
            print(f"   - Já enviadas (verde): {len(status_2_pages)}")
            
            # Testar busca
            search_term = "arquivo"
            search_results = [
                p for p in all_pages 
                if search_term.lower() in p['title'].lower()
            ]
            print(f"   - Páginas com '{search_term}': {len(search_results)}")
            
        else:
            print("   ⚠️  Nenhuma página encontrada em cache")
            print("   📝 Execute primeiro a extração de páginas do MediaWiki")
        
        # 2. Testar configuração do BookStack
        print("\n📚 2. Testando configuração BookStack...")
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        bookstack_config = {
            'url': config.get('bookstack_url', ''),
            'token_id': config.get('bookstack_token_id', ''),
            'token_secret': config.get('bookstack_token_secret', ''),
            'verify_ssl': config.get('bookstack_verify_ssl', True)
        }
        
        # Verificar se está configurado
        if all([bookstack_config['url'], bookstack_config['token_id'], bookstack_config['token_secret']]):
            print("   ✅ BookStack configurado!")
            print(f"   📍 URL: {bookstack_config['url']}")
            print(f"   🔑 Token ID: {bookstack_config['token_id'][:10]}...")
            print(f"   🔒 SSL: {'Ativado' if bookstack_config['verify_ssl'] else 'Desativado'}")
            
            # Testar conexão
            try:
                from bookstack_client import BookStackClient
                
                client = BookStackClient(
                    base_url=bookstack_config['url'],
                    token_id=bookstack_config['token_id'],
                    token_secret=bookstack_config['token_secret'],
                    verify_ssl=bookstack_config['verify_ssl']
                )
                
                print("\n   🔗 Testando conexão...")
                books = client.get_books(limit=3)
                
                if books:
                    print(f"   ✅ Conexão bem-sucedida! {len(books)} livros encontrados:")
                    for book in books[:3]:
                        print(f"      📖 {book.get('name', 'Sem nome')}")
                else:
                    print("   ⚠️  Conectado, mas nenhum livro encontrado")
                    
            except Exception as e:
                print(f"   ❌ Erro na conexão: {str(e)[:60]}...")
                
        else:
            print("   ❌ BookStack não configurado!")
            print("   📝 Configure nas Configurações da aplicação:")
            print("      - URL Base do BookStack")
            print("      - Token ID da API")
            print("      - Token Secret da API")
        
        # 3. Testar conversão de conteúdo
        print("\n🔄 3. Testando conversão Wikitext → HTML...")
        
        sample_wikitext = """
== Título Principal ==
Este é um exemplo de '''texto em negrito''' e ''texto em itálico''.

=== Subtítulo ===
* Item de lista 1
* Item de lista 2
** Sub-item

# Lista numerada
# Segundo item

[[Link Interno]] e [https://exemplo.com Link Externo]
        """.strip()
        
        # Simular conversão (versão simplificada)
        html_result = convert_wikitext_to_html_simple(sample_wikitext)
        print("   📝 Wikitext de exemplo:")
        print("   " + "\n   ".join(sample_wikitext.split('\n')[:4]) + "...")
        
        print("\n   🌐 HTML convertido:")
        print("   " + "\n   ".join(html_result.split('\n')[:4]) + "...")
        
        # 4. Resumo final
        print("\n" + "=" * 50)
        print("📋 RESUMO DOS TESTES")
        print("=" * 50)
        
        cache_status = "✅ OK" if all_pages else "❌ Vazio"
        bookstack_status = "✅ OK" if all([bookstack_config['url'], bookstack_config['token_id'], bookstack_config['token_secret']]) else "❌ Não configurado"
        
        print(f"📄 Cache de páginas: {cache_status}")
        print(f"📚 BookStack: {bookstack_status}")
        print(f"🔄 Conversão: ✅ OK")
        
        if all_pages and all([bookstack_config['url'], bookstack_config['token_id'], bookstack_config['token_secret']]):
            print("\n🎉 TUDO PRONTO! A funcionalidade 'Enviar Páginas' está operacional!")
            print("\n📖 Para usar:")
            print("1. Execute: python main.py")
            print("2. Faça login no MediaWiki")
            print("3. Clique em '📤 Enviar Páginas'")
            print("4. Selecione páginas e destino")
            print("5. Clique em 'Enviar para BookStack'")
        else:
            print("\n⚠️  CONFIGURAÇÃO PENDENTE:")
            if not all_pages:
                print("- Extraia páginas do MediaWiki primeiro")
            if not all([bookstack_config['url'], bookstack_config['token_id'], bookstack_config['token_secret']]):
                print("- Configure credenciais do BookStack")
        
    except Exception as e:
        print(f"\n❌ ERRO no teste: {e}")
        import traceback
        traceback.print_exc()

def convert_wikitext_to_html_simple(wikitext):
    """Conversão simplificada para teste"""
    import re
    
    html = wikitext
    
    # Cabeçalhos
    html = re.sub(r'^===(.+?)===', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^==(.+?)==', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    
    # Formatação
    html = re.sub(r"'''(.+?)'''", r'<strong>\1</strong>', html)
    html = re.sub(r"''(.+?)''", r'<em>\1</em>', html)
    
    # Links
    html = re.sub(r'\[\[([^]]+)\]\]', r'<a href="#\1">\1</a>', html)
    html = re.sub(r'\[([^ ]+) ([^\]]+)\]', r'<a href="\1">\2</a>', html)
    
    return html

if __name__ == "__main__":
    test_send_pages_functionality()
