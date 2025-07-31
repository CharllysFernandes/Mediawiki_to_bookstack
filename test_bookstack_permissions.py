#!/usr/bin/env python3
"""
Diagnóstico de Permissões BookStack - Teste Detalhado
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bookstack_client import BookStackClient
from src.config_manager import ConfigManager

def test_bookstack_permissions():
    """Testa permissões detalhadas do BookStack"""
    print("🔧 DIAGNÓSTICO DE PERMISSÕES BOOKSTACK")
    print("=" * 50)
    
    # Carregar configurações
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    if not config:
        print("❌ Nenhuma configuração encontrada!")
        print("   Configure o BookStack primeiro na interface gráfica.")
        return
    
    # Verificar se tem configuração BookStack
    required_fields = ['bookstack_url', 'bookstack_token_id', 'bookstack_token_secret']
    missing_fields = [field for field in required_fields if not config.get(field)]
    
    if missing_fields:
        print(f"❌ Configurações BookStack incompletas!")
        print(f"   Campos faltando: {', '.join(missing_fields)}")
        return
    
    # Criar cliente
    client = BookStackClient(
        base_url=config['bookstack_url'],
        token_id=config['bookstack_token_id'],
        token_secret=config['bookstack_token_secret'],
        verify_ssl=config.get('bookstack_verify_ssl', True)
    )
    
    print(f"🌐 Testando: {client.base_url}")
    print(f"🔑 Token ID: {client.token_id[:10]}...")
    print()
    
    # TESTE 1: Conexão básica
    print("1️⃣ TESTE DE CONEXÃO BÁSICA")
    print("-" * 30)
    
    result = client.test_connection()
    
    if result.get('success'):
        print("✅ Conexão estabelecida")
        
        user_info = result.get('user_info', {})
        if user_info:
            print(f"👤 Usuário: {user_info.get('name', 'N/A')}")
            if user_info.get('email'):
                print(f"📧 Email: {user_info['email']}")
            if user_info.get('id'):
                print(f"🆔 ID: {user_info['id']}")
        
        # Verificar permissões de criação
        create_perms = result.get('create_permissions', {})
        if create_perms:
            can_create = create_perms.get('can_create', False)
            status = create_perms.get('status', 'Desconhecido')
            print(f"🔐 Permissões de criação: {'✅' if can_create else '❌'} {status}")
            
            if not can_create:
                print("⚠️  PROBLEMA DETECTADO:")
                print(f"   {create_perms.get('details', 'Sem detalhes')}")
                if 'solution' in create_perms:
                    print("\n💡 SOLUÇÃO:")
                    for line in create_perms['solution'].split('\n'):
                        if line.strip():
                            print(f"   {line}")
                return  # Parar aqui se não tem permissões básicas
        
        print()
        
    else:
        print("❌ Falha na conexão")
        print(f"   {result.get('message', 'Erro desconhecido')}")
        if 'solution' in result:
            print("\n💡 SOLUÇÃO:")
            for line in result['solution'].split('\n'):
                if line.strip():
                    print(f"   {line}")
        return
    
    # TESTE 2: Listar livros
    print("2️⃣ TESTE DE ACESSO A LIVROS")
    print("-" * 30)
    
    try:
        books = client.get_books(limit=5)
        if books:
            print(f"✅ {len(books)} livro(s) encontrado(s):")
            for book in books[:3]:
                print(f"   📚 {book.get('name', 'Sem nome')} (ID: {book.get('id')})")
            if len(books) > 3:
                print(f"   ... e mais {len(books) - 3} livros")
        else:
            print("⚠️  Nenhum livro encontrado")
            print("   Pode não ter permissão de leitura ou não há livros criados")
    except Exception as e:
        print(f"❌ Erro ao listar livros: {e}")
        return
    
    print()
    
    # TESTE 3: Teste de criação simulada (sem criar realmente)
    print("3️⃣ TESTE SIMULADO DE CRIAÇÃO")
    print("-" * 30)
    
    if books:
        test_book = books[0]
        print(f"📖 Testando com livro: {test_book.get('name')} (ID: {test_book.get('id')})")
        
        # Tentar obter detalhes do livro
        try:
            book_details = client._make_request('GET', f"/books/{test_book['id']}")
            print("✅ Acesso a detalhes do livro confirmado")
        except Exception as e:
            print(f"❌ Erro ao acessar detalhes do livro: {e}")
            if "403" in str(e):
                print("   → Token não tem permissão de leitura detalhada")
        
        # Preparar dados de teste (sem enviar)
        test_page_data = {
            'name': 'TESTE_CONEXAO_API_NAO_CRIAR',
            'html': '<p>Esta é uma página de teste que não deveria ser criada</p>',
            'book_id': test_book['id']
        }
        
        print("ℹ️  Dados de teste preparados (não serão enviados)")
        print(f"   Nome: {test_page_data['name']}")
        print(f"   Destino: Livro {test_book['id']}")
        
    print()
    
    # TESTE 4: Verificação de roles/permissões do usuário
    print("4️⃣ VERIFICAÇÃO DE ROLES")
    print("-" * 30)
    
    try:
        # Tentar acessar endpoint de roles (pode falhar dependendo da versão)
        try:
            roles_response = client._make_request('GET', '/roles')
            roles = roles_response.get('data', [])
            print(f"✅ {len(roles)} role(s) no sistema:")
            for role in roles[:5]:
                print(f"   🎭 {role.get('display_name', role.get('name', 'Sem nome'))}")
        except:
            print("ℹ️  Não foi possível listar roles (normal em algumas versões)")
        
        # Tentar verificar permissões do usuário atual
        user_info = result.get('user_info', {})
        if user_info.get('id'):
            try:
                user_details = client._make_request('GET', f"/users/{user_info['id']}")
                user_roles = user_details.get('roles', [])
                if user_roles:
                    print(f"👤 Roles do usuário atual:")
                    for role in user_roles:
                        print(f"   🎭 {role.get('display_name', role.get('name', 'Sem nome'))}")
                else:
                    print("⚠️  Usuário sem roles atribuídas")
            except:
                print("ℹ️  Não foi possível verificar roles do usuário")
    except Exception as e:
        print(f"ℹ️  Verificação de roles limitada: {e}")
    
    print()
    
    # RESUMO FINAL
    print("📋 RESUMO DO DIAGNÓSTICO")
    print("=" * 30)
    
    if result.get('success'):
        create_perms = result.get('create_permissions', {})
        can_create = create_perms.get('can_create', False)
        
        if can_create:
            print("✅ TUDO OK - Token tem permissões adequadas")
            print("   Você pode enviar páginas para o BookStack")
        else:
            print("❌ PROBLEMA IDENTIFICADO - Token sem permissões de criação")
            print(f"   Status: {create_perms.get('status', 'Desconhecido')}")
            print("\n🔧 PRÓXIMOS PASSOS:")
            print("   1. Acesse o BookStack como administrador")
            print("   2. Vá em: Configurações > Usuários")
            print("   3. Encontre o usuário do token atual")
            print("   4. Edite o usuário e verifique as roles")
            print("   5. Certifique-se que tem uma role com 'API Access'")
            print("   6. Se necessário, crie nova role com permissões adequadas")
    else:
        print("❌ PROBLEMA CRÍTICO - Conexão básica falhou")
        print("   Resolva problemas de conexão antes de testar permissões")
    
    print("\n🏁 Diagnóstico concluído!")

if __name__ == "__main__":
    test_bookstack_permissions()
