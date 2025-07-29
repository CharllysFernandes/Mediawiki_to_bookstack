# Integração com mwparserfromhell

## Por que mwparserfromhell é útil?

A biblioteca `mwparserfromhell` oferece significativas melhorias na qualidade da conversão de wikitext para markdown em comparação com métodos baseados apenas em regex.

### Problemas com Regex Simples

O método anterior usava regex básico com limitações:

```python
# Método antigo - limitado
markdown = re.sub(r"'''(.*?)'''", r'**\1**', markdown)
markdown = re.sub(r'{{.*?}}', '', markdown)  # Remove todos os templates
```

### Vantagens do mwparserfromhell

#### 1. **Parsing Estruturado**
- Compreende a hierarquia do wikitext
- Identifica corretamente elementos aninhados
- Preserva contexto e relacionamentos

#### 2. **Processamento Inteligente de Templates**

**Antes:**
```
{{note|Informação importante}} → [removido]
```

**Depois:**
```
{{note|Informação importante}} → > **Nota:** Informação importante
```

#### 3. **Conversão Contextual**

Templates específicos agora são convertidos apropriadamente:

- **Infoboxes** → Tabelas markdown estruturadas
- **Citações** → Blockquotes com autor  
- **Código** → Blocos de código com sintaxe highlighting
- **Avisos** → Blockquotes com emoji

#### 4. **Melhor Tratamento de Links**

**Links internos:**
```
[[Programação|desenvolvimento]] → **desenvolvimento**
```

**Links externos:**  
```
[https://example.com Site] → [Site](https://example.com)
```

#### 5. **Tabelas Robustas**

Converte tabelas wiki complexas mantendo estrutura:

```wiki
{| class="wikitable"
! Nome !! Idade !! Cidade  
|-
| João || 30 || São Paulo
|}
```

Vira:
```markdown
| Nome | Idade | Cidade |
|------|-------|--------|  
| João | 30 | São Paulo |
```

### Sistema de Fallback

O código inclui fallback automático:

1. **Tenta parser avançado** (mwparserfromhell)
2. **Se falhar**, usa conversão básica com regex
3. **Logs de erro** para debugging

### Tipos de Templates Suportados

| Template | Conversão |
|----------|-----------|
| `{{note\|texto}}` | `> **Nota:** texto` |
| `{{warning\|texto}}` | `> ⚠️ **Aviso:** texto` |
| `{{code\|lang=python\|código}}` | ` ```python\ncódigo\n``` ` |
| `{{quote\|texto\|author=autor}}` | `> texto\n> — *autor*` |
| `{{infobox pessoa\|...}}` | Tabela markdown estruturada |

### Melhorias na Qualidade

**Extração mais limpa:**
- Preserva formatação importante
- Remove elementos não essenciais de forma inteligente
- Mantém metadados relevantes

**Melhor estrutura:**
- Cabeçalhos preservados corretamente
- Listas e numeração mantidas
- Blocos de código identificados

**Conteúdo mais útil:**
- Templates informativos convertidos (não removidos)
- Links preservados quando possível
- Estrutura semântica mantida

### Configuração

A integração é automática:

1. **Instalar dependência:**
   ```bash
   pip install mwparserfromhell
   ```

2. **O código detecta automaticamente** se está disponível

3. **Fallback transparente** se não estiver instalado

### Resultado Final

Páginas MediaWiki complexas agora são convertidas para markdown rico e estruturado, mantendo:

- ✅ Informações de templates importantes
- ✅ Estrutura hierárquica
- ✅ Formatação apropriada  
- ✅ Metadados e contexto
- ✅ Compatibilidade com BookStack

A migração fica muito mais eficiente e o conteúdo resultante requer menos edição manual.

## Próximos Passos

1. **Personalizar templates específicos** da sua wiki
2. **Ajustar conversões** conforme necessário
3. **Adicionar novos tipos** de template no `wikitext_parser.py`
4. **Configurar mapeamentos** específicos para seu caso de uso

A biblioteca `mwparserfromhell` transforma o projeto de uma conversão básica para uma migração inteligente e preservativa de conteúdo.
