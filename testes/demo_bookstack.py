#!/usr/bin/env python3
"""
Demo de Integração BookStack - MediaWiki to BookStack
=====================================================

Este script demonstra como usar o cliente BookStack para:
1. Conectar ao BookStack
2. Criar ou localizar um livro
3. Criar capítulos e páginas
4. Importar conteúdo extraído do MediaWiki

Configuração necessária:
- URL do BookStack (ex: https://bookstack.empresa.com)
- Token ID da API
- Token Secret da API

Obtenha os tokens em: BookStack > Configurações > API Tokens
"""

import os
import sys
from src.config_manager import ConfigManager
from src.bookstack_client import BookStackClient
from src.logger import Logger

def main():
    print("📚 Demo de Integração BookStack")
    print("=" * 50)
    
    # Configurar logger
    logger = Logger()
    
    # Carregar configurações
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # Verificar se as configurações do BookStack estão disponíveis
    bookstack_url = config.get('bookstack_url', '').strip()
    token_id = config.get('bookstack_token_id', '').strip()
    token_secret = config.get('bookstack_token_secret', '').strip()
    verify_ssl = config.get('bookstack_verify_ssl', True)
    
    if not all([bookstack_url, token_id, token_secret]):
        print("❌ Configurações do BookStack não encontradas!")
        print("\nPara usar este demo:")
        print("1. Execute a aplicação principal (python main.py)")
        print("2. Vá em Configurações")
        print("3. Configure as credenciais do BookStack:")
        print("   - URL Base do BookStack")
        print("   - Token ID da API")
        print("   - Token Secret da API")
        print("4. Teste a conexão")
        print("5. Salve as configurações")
        return
    
    try:
        print(f"🔗 Conectando ao BookStack: {bookstack_url}")
        
        # Criar cliente BookStack
        client = BookStackClient(
            base_url=bookstack_url,
            token_id=token_id,
            token_secret=token_secret,
            verify_ssl=verify_ssl
        )
        
        print("✅ Conexão estabelecida!")
        
        # Teste 1: Listar livros existentes
        print("\n📖 Livros disponíveis:")
        books = client.get_books(limit=5)  # Corrigido: usar 'limit' ao invés de 'count'
        if books:
            for book in books:
                print(f"  - {book.get('name', 'Sem nome')} (ID: {book.get('id')})")
        else:
            print("  Nenhum livro encontrado ou acesso negado")
        
        # Teste 2: Criar um livro de demonstração
        print("\n📝 Criando livro de demonstração...")
        
        demo_book_data = {
            'name': 'MediaWiki Import Demo',
            'description': 'Livro criado automaticamente pelo MediaWiki to BookStack'
        }
        
        try:
            new_book = client.create_book(demo_book_data)
            if new_book and 'id' in new_book:
                book_id = new_book['id']
                print(f"✅ Livro criado com sucesso! ID: {book_id}")
                
                # Teste 3: Criar um capítulo
                print("\n📑 Criando capítulo de demonstração...")
                
                demo_chapter_data = {
                    'name': 'Procedimentos Importados',
                    'description': 'Capítulo com procedimentos extraídos do MediaWiki',
                    'book_id': book_id
                }
                
                new_chapter = client.create_chapter(demo_chapter_data)
                if new_chapter and 'id' in new_chapter:
                    chapter_id = new_chapter['id']
                    print(f"✅ Capítulo criado com sucesso! ID: {chapter_id}")
                    
                    # Teste 4: Criar uma página de exemplo
                    print("\n📄 Criando página de demonstração...")
                    
                    demo_page_data = {
                        'name': 'Página de Teste - MediaWiki Import',
                        'html': '''
                        <h1>Página Importada do MediaWiki</h1>
                        <p>Esta página foi criada automaticamente pelo sistema de importação.</p>
                        
                        <h2>Funcionalidades Implementadas:</h2>
                        <ul>
                            <li>✅ Extração de conteúdo do MediaWiki</li>
                            <li>✅ Download automático de imagens</li>
                            <li>✅ Criação automática no BookStack</li>
                            <li>✅ Preservação da estrutura</li>
                        </ul>
                        
                        <h2>Próximos Passos:</h2>
                        <ol>
                            <li>Configure o MediaWiki na aplicação</li>
                            <li>Extraia as páginas desejadas</li>
                            <li>Use a função de importação para BookStack</li>
                        </ol>
                        
                        <p><strong>Data de criação:</strong> {}</p>
                        '''.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
                        'chapter_id': chapter_id
                    }
                    
                    new_page = client.create_page(demo_page_data)
                    if new_page and 'id' in new_page:
                        page_id = new_page['id']
                        print(f"✅ Página criada com sucesso! ID: {page_id}")
                        
                        # Mostrar URL da página criada
                        page_url = f"{bookstack_url}/books/{book_id}/page/{page_id}"
                        print(f"\n🌐 Acesse a página em: {page_url}")
                    
                else:
                    print("❌ Erro ao criar página")
                    
            else:
                print("❌ Erro ao criar capítulo")
                
        except Exception as e:
            if "already exists" in str(e).lower():
                print("ℹ️  Livro já existe, continuando...")
            else:
                print(f"❌ Erro ao criar livro: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Demo concluído com sucesso!")
        print("\nPara usar a integração completa:")
        print("1. Configure o MediaWiki na aplicação principal")
        print("2. Extraia as páginas que deseja importar")
        print("3. Use o botão 'Importar para BookStack' (em desenvolvimento)")
        
    except Exception as e:
        print(f"❌ Erro na demonstração: {e}")
        logger.log_error("Demo BookStack", e)

if __name__ == "__main__":
    # Importações necessárias para datetime
    from datetime import datetime
    main()
