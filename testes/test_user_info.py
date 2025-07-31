#!/usr/bin/env python3
"""
Teste das melhorias de informações de usuário BookStack
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bookstack_client import BookStackClient

def test_user_info_improvements():
    """Testa as melhorias de obtenção de informações do usuário"""
    print("🔧 Testando melhorias de informações do usuário BookStack...")
    
    # NOTA: Para testar, você precisa fornecer credenciais válidas
    print("\n⚠️  CONFIGURAÇÃO NECESSÁRIA:")
    print("   Para testar, edite este arquivo e adicione:")
    print("   - base_url: URL do seu BookStack")
    print("   - token_id: Seu Token ID")
    print("   - token_secret: Seu Token Secret")
    print("\n" + "="*50)
    
    # Configurações de teste (EDITE AQUI COM SUAS CREDENCIAIS)
    base_url = "https://seu-bookstack.com"  # ← EDITE AQUI
    token_id = "seu_token_id"               # ← EDITE AQUI  
    token_secret = "seu_token_secret"       # ← EDITE AQUI
    
    # Verificar se credenciais foram configuradas
    if base_url == "https://seu-bookstack.com" or token_id == "seu_token_id":
        print("❌ Credenciais não configuradas!")
        print("   Edite o arquivo test_user_info.py e configure suas credenciais.")
        return
    
    client = BookStackClient(
        base_url=base_url,
        token_id=token_id,
        token_secret=token_secret,
        verify_ssl=False  # Ajustar conforme necessário
    )
    
    print(f"\n🌐 URL: {client.base_url}")
    print(f"🔑 Token ID: {client.token_id[:10]}...")
    
    print("\n1️⃣ Testando conexão e obtenção de informações do usuário...")
    result = client.test_connection()
    
    if result.get('success'):
        print("✅ Conexão bem-sucedida!")
        user_info = result.get('user_info', {})
        
        print("\n📋 Informações do usuário:")
        for key, value in user_info.items():
            if value:  # Só mostrar campos não vazios
                print(f"   {key.capitalize()}: {value}")
                
        # Verificar se obteve nome real do usuário
        user_name = user_info.get('name', '')
        if user_name and user_name not in ['Usuário', 'Usuário do Token', 'Usuário não identificado']:
            print(f"\n✅ Nome real do usuário obtido: '{user_name}'")
        else:
            print(f"\n⚠️  Nome genérico detectado: '{user_name}'")
            print("   Isso pode indicar que o endpoint /users/me está indisponível")
            
    else:
        print("❌ Falha na conexão:")
        print(f"   {result.get('message', 'Erro desconhecido')}")
        
        if 'error' in result:
            print(f"\n🔍 Erro completo:")
            print(f"   {result['error']}")
        
        if 'solution' in result:
            print("\n💡 Solução:")
            for line in result['solution'].split('\n'):
                if line.strip():
                    print(f"   {line}")
    
    print("\n2️⃣ Testando método alternativo de informações do usuário...")
    try:
        alt_user_info = client._get_user_info_alternative()
        print("📋 Informações via método alternativo:")
        for key, value in alt_user_info.items():
            if value:
                print(f"   {key.capitalize()}: {value}")
    except Exception as e:
        print(f"❌ Método alternativo falhou: {e}")
    
    print("\n🏁 Teste concluído!")
    print("\n💡 Dica: Compare os resultados antes e depois das melhorias.")

if __name__ == "__main__":
    test_user_info_improvements()
