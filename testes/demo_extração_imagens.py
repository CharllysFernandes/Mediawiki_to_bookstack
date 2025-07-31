#!/usr/bin/env python3
"""
Script de Demonstração - Extração TXT + Imagens
Demonstra como usar o novo sistema de download de imagens
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.mediawiki_client import MediaWikiClient
from src.image_downloader import MediaWikiImageDownloader

def demo_image_extraction():
    """Demonstração da funcionalidade de extração de imagens"""
    
    print("🎯 DEMONSTRAÇÃO: Extração TXT + Imagens")
    print("=" * 50)
    
    # Configuração de exemplo (substitua pelos dados reais)
    demo_config = {
        'api_url': 'https://sua-wiki.com.br/api.php',
        'username': 'seu_usuario',
        'password': 'sua_senha',
        'verify_ssl': False,
        'timeout': 30
    }
    
    print(f"📋 Configuração carregada")
    print(f"   🌐 API: {demo_config['api_url']}")
    print(f"   👤 Usuário: {demo_config['username']}")
    print(f"   🔒 SSL: {'Verificado' if demo_config['verify_ssl'] else 'Desabilitado'}")
    
    # Exemplo de conteúdo de página com imagens
    exemplo_wikitext = """
{| class="wikitable"
|-
! colspan="2"|PROCEDIMENTO EXEMPLO
|-
||Tipo
||Instalação de Software
|}

==Procedimento==
'''Passo 1''': Procure por alguma foto com extensão .JPEG e clique com o botão direito:

[[Arquivo:screenshot_passo1.jpeg]]

'''Passo 2''': Selecione "Abrir com" no menu:

[[File:menu_contexto.png]]

'''Passo 3''': Escolha o aplicativo desejado:

[[Arquivo:selecao_app.gif]]

'''Resultado Final:'''

[[File:resultado_final.jpg|thumb|Aplicativo funcionando]]

==Documentação==
Para mais informações, consulte o manual:

[[Arquivo:manual_completo.pdf]]
"""
    
    exemplo_html = """
<div class="procedure">
    <h2>Procedimento Visual</h2>
    <p>Veja as imagens do processo:</p>
    <img src="/upload/thumb/screenshot.png/300px-screenshot.png" alt="Screenshot" />
    <img src="https://wiki.exemplo.com/images/diagrama.svg" alt="Diagrama" />
    <a href="/images/anexo.pdf">Manual em PDF</a>
</div>
"""
    
    # Demonstração de extração de imagens
    print("\n🔍 FASE 1: Análise de Conteúdo")
    print("-" * 30)
    
    # Simular cliente (sem conexão real)
    print("⚙️ Inicializando sistema de imagens...")
    
    # Mock do cliente para demonstração
    class MockClient:
        def __init__(self):
            self.api_url = demo_config['api_url']
            self.session = None
    
    mock_client = MockClient()
    downloader = MediaWikiImageDownloader(mock_client)
    
    # Extrair imagens do wikitext
    print("\n📝 Extraindo imagens do wikitext...")
    wikitext_images = downloader.extract_images_from_wikitext(exemplo_wikitext)
    print(f"   ✅ Encontradas {len(wikitext_images)} imagens no wikitext:")
    for i, img in enumerate(wikitext_images, 1):
        print(f"      {i}. {img}")
    
    # Extrair imagens do HTML
    print("\n🌐 Extraindo imagens do HTML...")
    html_images = downloader.extract_images_from_html(exemplo_html)
    print(f"   ✅ Encontradas {len(html_images)} imagens no HTML:")
    for i, img in enumerate(html_images, 1):
        print(f"      {i}. {img}")
    
    # Demonstrar processamento de nomes
    print("\n🔧 FASE 2: Processamento de Nomes")
    print("-" * 30)
    
    test_filenames = [
        "Arquivo:screenshot_passo1.jpeg",
        "File:menu contexto com espaços.png",
        "imagem<>com|chars/inválidos.gif",
        "nome_muito_longo_que_precisa_ser_truncado_para_nao_causar_problemas_no_filesystem.jpg"
    ]
    
    for filename in test_filenames:
        sanitized = downloader._sanitize_filename(filename)
        print(f"   📝 '{filename}' → '{sanitized}'")
    
    # Demonstrar estrutura de saída
    print("\n📁 FASE 3: Estrutura de Saída")
    print("-" * 30)
    
    output_example = """
extracted_txt_images_20250731_143052/
├── RELATORIO_COMPLETO.txt
├── INDICE.txt
├── Procedimento_Exemplo.txt
└── images/
    └── Procedimento_Exemplo/
        ├── screenshot_passo1.jpeg
        ├── menu_contexto.png
        ├── selecao_app.gif
        ├── resultado_final.jpg
        └── manual_completo.pdf
"""
    
    print(f"   📂 Estrutura gerada:")
    print(output_example)
    
    # Demonstrar relatório
    print("\n📊 FASE 4: Relatório de Exemplo")
    print("-" * 30)
    
    relatorio_exemplo = f"""
RELATÓRIO COMPLETO - EXTRAÇÃO TXT + IMAGENS
===============================================

Data de extração: 31/07/2025 14:30:52
Total de páginas: 1

RESUMO DE IMAGENS:
------------------------------
Imagens encontradas: 5
Imagens baixadas: 5
Taxa de sucesso: 100.0%

DETALHES POR PÁGINA:
==============================

  1. Procedimento Exemplo
     Arquivo TXT: Procedimento_Exemplo.txt
     Imagens encontradas: 5
     Imagens baixadas: 5
     Arquivos: screenshot_passo1.jpeg, menu_contexto.png, selecao_app.gif
"""
    
    print(relatorio_exemplo)
    
    # Vantagens da funcionalidade
    print("\n💡 VANTAGENS DA NOVA FUNCIONALIDADE")
    print("-" * 30)
    
    vantagens = [
        "✅ Extração completa: texto + imagens em um só processo",
        "✅ Organização automática: estrutura clara de diretórios", 
        "✅ Múltiplas fontes: wikitext + HTML para máxima cobertura",
        "✅ Relatórios detalhados: estatísticas completas",
        "✅ Error handling: continua mesmo com falhas",
        "✅ Cache inteligente: evita downloads duplicados",
        "✅ Nomes seguros: sanitização automática",
        "✅ Progress tracking: acompanhamento em tempo real"
    ]
    
    for vantagem in vantagens:
        print(f"   {vantagem}")
    
    # Como usar na aplicação
    print("\n🚀 COMO USAR NA APLICAÇÃO")
    print("-" * 30)
    
    instrucoes = [
        "1. Execute: python main.py",
        "2. Configure conexão com sua wiki",
        "3. Vá para aba 'Páginas'",
        "4. Clique 'Carregar Cache' ou 'Atualizar da API'",
        "5. Selecione páginas com procedimentos",
        "6. Clique 'Extrair TXT + Imagens' (botão roxo)",
        "7. Aguarde processamento completo",
        "8. Verifique arquivos na pasta gerada"
    ]
    
    for i, instrucao in enumerate(instrucoes, 1):
        print(f"   {instrucao}")
    
    print(f"\n🎯 RESULTADO FINAL")
    print("-" * 30)
    print("   📄 Arquivos TXT com procedimentos completos")
    print("   🖼️ Imagens organizadas por procedimento") 
    print("   📋 Relatórios detalhados de todo processo")
    print("   ✅ Pronto para usar em BookStack ou outras plataformas")
    
    print(f"\n✨ Demonstração concluída!")
    print(f"💡 A nova funcionalidade resolve completamente a necessidade")
    print(f"   de extrair procedimentos com imagens do MediaWiki!")

if __name__ == "__main__":
    try:
        demo_image_extraction()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {str(e)}")
        import traceback
        traceback.print_exc()
