#!/usr/bin/env python3
"""
Script de exemplo demonstrando as capacidades do parser avançado de wikitext
"""

import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.wikitext_parser import WikitextParser

def test_advanced_parsing():
    """Demonstra parsing avançado com mwparserfromhell"""
    
    parser = WikitextParser()
    
    # Exemplo 1: Página com templates complexos
    wikitext1 = """
== Introdução ==

Esta é uma página de exemplo com {{note|Esta é uma nota importante}} sobre o assunto.

=== Infobox ===

{{infobox pessoa
|nome = João Silva  
|idade = 30
|profissão = Desenvolvedor
|localização = São Paulo
}}

=== Código de Exemplo ===

{{code|lang=python|
def hello_world():
    print("Hello, World!")
}}

=== Citações ===

{{quote|A programação é uma arte|author=Algum Programador}}

== Links e Referências ==

Veja também [[Programação]] e [[Python]].

Link externo: [https://python.org Python Official Site]

=== Tabela ===

{| class="wikitable"
! Nome !! Idade !! Cidade
|-
| João || 30 || São Paulo  
|-
| Maria || 25 || Rio de Janeiro
|}

=== Formatação ===

Texto '''negrito''' e ''itálico''.

<code>código inline</code>

<pre>
bloco de código
múltiplas linhas
</pre>

== Categorias ==

[[Category:Programação]]
[[Category:Python]]
"""

    print("=== EXEMPLO 1: Parsing Avançado ===")
    result1 = parser.parse_wikitext(wikitext1, "Página de Exemplo", ["Programação", "Python"])
    print("Dados extraídos:")
    print(f"- Título: {result1['title']}")
    print(f"- Categorias: {result1['categories']}")
    print(f"- Templates encontrados: {len(result1['templates'])}")
    print(f"- Links encontrados: {len(result1['links'])}")
    print(f"- Seções encontradas: {len(result1['sections'])}")
    
    if result1['templates']:
        print("\nTemplates:")
        for template in result1['templates']:
            print(f"  - {template['name']}: {list(template['params'].keys())}")
    
    if result1['sections']:
        print("\nSeções:")
        for section in result1['sections']:
            print(f"  - H{section['level']}: {section['title']}")
    
    print("\n" + "="*50)
    print("\n" + "="*60 + "\n")
    
    # Exemplo 2: Página com estrutura complexa
    wikitext2 = """
= Procedimento de Instalação =

{{warning|Sempre faça backup antes de prosseguir}}

== Pré-requisitos ==

* Sistema operacional suportado
* [[Python]] versão 3.8 ou superior  
* Acesso administrativo

=== Verificação do Sistema ===

Execute o comando:

{{code|lang=bash|python --version}}

== Instalação ==

1. Baixe o arquivo de instalação
2. Execute como administrador
3. Siga as instruções na tela

{{infobox software
|nome = MeuSoftware
|versão = 2.1.0
|licença = MIT
|desenvolvedor = Equipe Dev
}}

== Solução de Problemas ==

{{note|Em caso de erro, consulte os logs em /var/log/}}

=== Erros Comuns ===

* '''Erro 404''': Arquivo não encontrado
* '''Erro 500''': Problema no servidor

== Ver Também ==

* [[Documentação]]
* [[FAQ]]

[[Category:Instalação]]
[[Category:Software]]
"""

    print("=== EXEMPLO 2: Procedimento Técnico ===")
    result2 = parser.parse_wikitext(wikitext2, "Procedimento de Instalação", ["Instalação", "Software"])
    print("Dados extraídos:")
    print(f"- Título: {result2['title']}")
    print(f"- Categorias: {result2['categories']}")
    print(f"- Templates encontrados: {len(result2['templates'])}")
    print(f"- Links encontrados: {len(result2['links'])}")
    print(f"- Seções encontradas: {len(result2['sections'])}")
    print("\n" + "="*60 + "\n")

def test_fallback():
    """Testa o sistema de fallback"""
    
    # Simular texto problemático que pode causar erro no parser
    problematic_wikitext = """
== Título ==

{{template_inexistente|param1|param2={{nested|value}}}}

Texto normal aqui.

[[Link quebrado|
"""
    
    parser = WikitextParser()
    print("=== EXEMPLO 3: Teste de Fallback ===")
    
    try:
        result = parser.parse_wikitext(problematic_wikitext, "Teste de Fallback")
        print("Parsing realizado com sucesso!")
        print(f"- Erro no parsing: {result.get('parse_error', 'Nenhum')}")
        print(f"- Templates encontrados: {len(result['templates'])}")
        print(f"- Conteúdo preservado: {len(result['content'])} caracteres")
    except Exception as e:
        print(f"Erro: {e}")

def compare_methods():
    """Compara método básico vs avançado"""
    
    test_wikitext = """
== Título ==

{{note|Nota importante}}

Texto com '''negrito''' e ''itálico''.

[[Link interno]] e [https://example.com link externo].

{| class="wikitable"
! Coluna 1 !! Coluna 2
|-
| Dados 1 || Dados 2
|}

{{code|lang=python|print("Hello")}}
"""
    
    parser = WikitextParser()
    
    print("=== COMPARAÇÃO: Parser Avançado vs Básico ===")
    print("\n--- Parser Avançado ---")
    advanced_result = parser.parse_wikitext(test_wikitext, "Teste de Comparação")
    print(f"Templates encontrados: {len(advanced_result['templates'])}")
    print(f"Links encontrados: {len(advanced_result['links'])}")
    print(f"Seções encontradas: {len(advanced_result['sections'])}")
    
    print("\n--- Limpeza Básica ---") 
    basic_result = parser.clean_wikitext(test_wikitext)
    print(f"Texto limpo ({len(basic_result)} caracteres)")
    print(basic_result[:200] + "..." if len(basic_result) > 200 else basic_result)

if __name__ == "__main__":
    print("🔍 Demonstração do Parser de Wikitext\n")
    
    try:
        import mwparserfromhell
        print("✅ mwparserfromhell disponível - testando parser\n")
        
        test_advanced_parsing()
        test_fallback()
        compare_methods()
        
    except ImportError:
        print("❌ mwparserfromhell não instalado")
        print("Para instalar: pip install mwparserfromhell")
        print("Executando apenas teste básico...\n")
        
        converter = WikitextToMarkdownConverter()
        basic_text = "== Título ==\nTexto '''negrito''' aqui."
        result = converter._basic_regex_conversion(basic_text)
        print("Conversão básica:", result)
