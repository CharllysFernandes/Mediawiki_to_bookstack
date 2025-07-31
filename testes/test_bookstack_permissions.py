#!/usr/bin/env python3
"""
Teste das correções de permissão da API BookStack
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bookstack_client import BookStackClient

def test_bookstack_permissions():
    """Testa o tratamento de erros de permissão"""
    print("🔧 Testando tratamento de erros de permissão BookStack...")
    
    # Usar dados da configuração real (que sabemos que falha)
    client = BookStackClient(
        base_url="xx",
        token_id="xx", 
        token_secret="xx",
        verify_ssl=False  # Desabilitar SSL para teste
    )
    
    print(f"\n🌐 URL: {client.base_url}")
    print(f"🔑 Token ID: {client.token_id[:10]}...")
    
    print("\n1️⃣ Testando conexão...")
    result = client.test_connection()
    
    if result.get('success'):
        print("✅ Conexão bem-sucedida!")
        print(f"   Usuário: {result.get('user_info', {}).get('name', 'N/A')}")
    else:
        print("❌ Falha na conexão:")
        print(f"   {result.get('message', 'Erro desconhecido')}")
        
        # Mostrar erro completo para debug
        if 'error' in result:
            print(f"\n🔍 Erro completo:")
            print(f"   {result['error']}")
        
        if 'solution' in result:
            print("\n💡 Solução:")
            for line in result['solution'].split('\n'):
                if line.strip():
                    print(f"   {line}")
    
    print("\n2️⃣ Testando criação de página (deve falhar)...")
    try:
        page_data = {
            'name': 'Teste de Permissão API',
            'html': '<p>Esta é uma página de teste</p>',
            'book_id': 5
        }
        
        result = client.create_page(page_data)
        print("✅ Página criada com sucesso!")
        print(f"   ID: {result.get('id', 'N/A')}")
        
    except Exception as e:
        print("❌ Falha esperada na criação:")
        error_lines = str(e).split('\n')
        for line in error_lines:
            if line.strip():
                print(f"   {line}")
    
    print("\n🏁 Teste concluído!")

if __name__ == "__main__":
    test_bookstack_permissions()
