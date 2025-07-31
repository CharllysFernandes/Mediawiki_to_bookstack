#!/usr/bin/env python3
"""
Script de teste para demonstrar estratégias de bypass de restrições
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mediawiki_client import MediaWikiClient

def test_bypass_strategies():
    """Demonstra as estratégias de bypass implementadas"""
    
    print("🔓 Demonstração de Estratégias de Bypass de Restrições\n")
    
    # Exemplo de configuração (substitua pelas suas credenciais reais)
    API_URL = "https://example.wiki.com/api.php"
    USERNAME = "seu_usuario"
    PASSWORD = "sua_senha"
    
    print("📋 Estratégias Implementadas:")
    print("1. ✅ Login com múltiplas estratégias:")
    print("   - Login padrão com tokens")
    print("   - Login com flag de bot")
    print("   - Obtenção de tokens CSRF e edição")
    print("   - Headers de bypass configurados")
    
    print("\n2. ✅ Requisições com estratégias múltiplas:")
    print("   - Requisição padrão")
    print("   - Requisição com token CSRF")
    print("   - Requisição com header Referer")
    print("   - Requisição como form-data")
    
    print("\n3. ✅ Métodos alternativos para obter wikitext:")
    print("   - Método padrão (query/revisions)")
    print("   - Via revisões históricas")
    print("   - Via Special:Export")
    print("   - Via action=parse")
    print("   - Via URL raw direta")
    
    print("\n4. ✅ Headers de bypass configurados:")
    headers_list = [
        "Accept: application/json, text/plain, */*",
        "Accept-Language: pt-BR,pt;q=0.9,en;q=0.8",
        "X-Requested-With: XMLHttpRequest",
        "Sec-Fetch-Mode: cors",
        "Cache-Control: no-cache",
        "User-Agent dinâmico (padrão/bot)"
    ]
    for header in headers_list:
        print(f"   - {header}")
    
    print("\n📝 Como Usar:")
    print("1. Na interface gráfica:")
    print("   ✓ Marque 'Contornar restrições de permissão'")
    print("   ✓ Para contas com privilégios: marque 'Usar modo bot'")
    print("   ✓ Configure suas credenciais normalmente")
    
    print("\n2. Programaticamente:")
    print("```python")
    print("client = MediaWikiClient(api_url, username, password)")
    print("client.bypass_restrictions = True  # Ativar bypass")
    print("client.bot_mode = True  # Para contas com privilégios")
    print("```")
    
    print("\n🔍 O que Acontece nos Bastidores:")
    print("- Quando um erro 403 (Forbidden) é detectado:")
    print("  1. Sistema tenta métodos alternativos automaticamente")
    print("  2. Usa diferentes headers e configurações")
    print("  3. Tenta acessar via revisões históricas")
    print("  4. Fallback para export e parse")
    print("  5. Último recurso: acesso raw direto")
    
    print("\n⚡ Benefícios:")
    print("✅ Maior taxa de sucesso na extração")
    print("✅ Contorna restrições de permissão comuns")
    print("✅ Funciona com diferentes configurações de MediaWiki")
    print("✅ Fallback automático se métodos falharem")
    print("✅ Preserva logs detalhados de tentativas")
    
    print("\n⚠️ Considerações:")
    print("- Use apenas em wikis onde você tem permissão legítima")
    print("- Respeite os termos de uso da wiki")
    print("- O bypass pode ser mais lento devido às múltiplas tentativas")
    print("- Algumas estratégias podem não funcionar em todos os MediaWiki")

def test_specific_scenario():
    """Testa cenário específico com bypass"""
    print("\n" + "="*60)
    print("🧪 TESTE ESPECÍFICO DE BYPASS")
    print("="*60)
    
    # Este é um exemplo - você precisa configurar com dados reais
    print("Para testar com dados reais:")
    print("1. Substitua as credenciais no código")
    print("2. Execute: python test_bypass.py")
    print("3. Observe os logs de tentativas de bypass")
    
    print("\nExemplo de uso programático:")
    code_example = '''
# Configurar cliente com bypass
client = MediaWikiClient(
    api_url="https://sua-wiki.com/api.php",
    username="seu_usuario", 
    password="sua_senha",
    verify_ssl=False  # Se necessário
)

# Ativar recursos de bypass
client.bypass_restrictions = True
client.bot_mode = True  # Se tiver privilégios

# Login com estratégias múltiplas
if client.login():
    print("Login bem-sucedido!")
    
    # Tentar extrair página com bypass
    try:
        content = client.get_page_content_wikitext("Nome_da_Página")
        print(f"Página extraída: {len(content['wikitext'])} caracteres")
    except Exception as e:
        print(f"Erro: {e}")
else:
    print("Falha no login")
'''
    print(code_example)

if __name__ == "__main__":
    test_bypass_strategies()
    test_specific_scenario()
    
    print("\n" + "="*60)
    print("🎯 CONCLUSÃO")
    print("="*60)
    print("O sistema de bypass implementado oferece múltiplas estratégias")
    print("para contornar restrições de permissão comum em MediaWiki.")
    print("Execute sua aplicação principal e ative as opções de bypass")
    print("para ver os resultados em ação!")
    print("="*60)
