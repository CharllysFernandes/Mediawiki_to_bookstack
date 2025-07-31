# Sistema de Expansão de Templates do MediaWiki

## 🎯 Problema Solucionado

Antes, templates do MediaWiki apareciam como `[Template: Nome_do_Template]` no markdown exportado, perdendo todo o conteúdo útil. Agora, o sistema **extrai e expande o conteúdo real** dos templates.

---

## 🔧 Funcionalidade Implementada

### **Antes da Expansão:**
```markdown
[Template: Servidor_de_Arquivos]
[Template: Ao_Telefone]
[Template: Acao_do_Chamado_Procedimento]
```

### **Depois da Expansão:**
```markdown
> **Procedimento:** Configuração de Servidor de Arquivos
> 
> **Categoria:** Infraestrutura
> **Responsável:** TI

📞 **Atendimento Telefônico**
- Horário: 8h às 18h
- Ramal: 1234

### Ação do Chamado
**Tipo:** Procedimento  
**Status:** Em Andamento  
**Prioridade:** Alta
```

---

## 🚀 Como Usar

### **Na Interface Gráfica:**

1. **Execute a aplicação:**
   ```bash
   python main.py
   ```

2. **Configure suas opções:**
   - ✅ **"Expandir templates (conteúdo completo)"** (já ativado por padrão)
   - ✅ Configure URL, usuário e senha normalmente
   - ✅ Ative outras opções conforme necessário

3. **Execute a extração:**
   - Liste páginas → Selecione → Extrair Markdown
   - Os templates serão expandidos automaticamente

### **Programaticamente:**

```python
from src.mediawiki_client import MediaWikiClient
from src.template_extractor import create_advanced_converter

# Criar cliente
client = MediaWikiClient(api_url, username, password)
client.login()

# Criar conversor avançado
converter = create_advanced_converter(client)

# Extrair com templates expandidos
result = converter.get_page_content_markdown_with_templates("Página_Com_Templates")

# Verificar se templates foram expandidos
if result.get('templates_expanded'):
    print("✅ Templates expandidos com sucesso!")
else:
    print("⚠️ Fallback para método padrão")
```

---

## 🔍 Como Funciona

### **Processo de Expansão:**

```
Página MediaWiki
       ↓
1. Parse do wikitext com mwparserfromhell
       ↓
2. Identificar todos os templates
       ↓
3. Para cada template:
   ├─ Tentar API expandtemplates
   ├─ Obter wikitext do Template:Nome
   ├─ Tentar variações do nome
   └─ Cache para evitar repetições
       ↓
4. Aplicar parâmetros aos templates
       ↓
5. Substituir no wikitext original
       ↓
6. Converter para markdown
```

### **Estratégias de Expansão:**

| Método | Descrição |
|--------|-----------|
| **API expandtemplates** | Usa API nativa do MediaWiki |
| **Template direto** | Busca `Template:Nome_do_Template` |
| **Variações de nome** | Tenta maiúscula, espaços, etc. |
| **Cache inteligente** | Evita requisições repetidas |
| **Fallback automático** | Volta ao método padrão se falhar |

---

## 📊 Benefícios

### **📈 Qualidade do Conteúdo:**
- ✅ **Conteúdo real dos templates** em vez de placeholders
- ✅ **Parâmetros expandidos** adequadamente
- ✅ **Estrutura preservada** do template original
- ✅ **Menos edição manual** necessária

### **🎯 Casos de Uso Melhorados:**
- **Procedimentos:** Templates de procedimentos expandidos completamente
- **Infoboxes:** Informações estruturadas preservadas
- **Avisos/Notas:** Conteúdo real em vez de referências
- **Documentação:** Templates técnicos com conteúdo útil

### **⚡ Performance:**
- **Cache inteligente** evita requisições repetidas
- **Processamento paralelo** quando possível
- **Fallback rápido** se expansão falhar
- **Logs detalhados** para debugging

---

## 🔧 Configurações Avançadas

### **Controle Via Interface:**

```
☑️ Expandir templates (conteúdo completo)
☑️ Contornar restrições de permissão  
☑️ Usar modo bot (para contas privilegiadas)
☑️ Verificar certificado SSL
```

### **Parâmetros Programáticos:**

```python
# Controle fino da expansão
client.get_page_content_markdown(
    page_title="Minha_Página",
    expand_templates=True  # True/False
)

# Processamento em lote
client.get_page_content_batch(
    page_titles=["Página1", "Página2"],
    format_type='markdown',
    expand_templates=True
)
```

---

## ⚠️ Considerações

### **💡 Requisitos:**
- **Permissões:** Acesso às páginas de template
- **Performance:** Processo pode ser mais lento
- **Conectividade:** Múltiplas requisições para templates

### **🔧 Troubleshooting:**

| Problema | Solução |
|----------|---------|
| Templates não expandem | Verificar permissões de acesso |
| Processo lento | Normal - cache melhora nas próximas |
| Alguns templates falham | Fallback automático ativo |
| Erro de conexão | Verificar configurações de rede |

### **📝 Logs Úteis:**
```
📋 Encontrados 5 templates na página 'Exemplo'
✅ Template expandido: Servidor_de_Arquivos
⚠️ Template não expandido: Template_Inexistente
❌ Erro ao expandir template Custom: Permission denied
🎯 Templates expandidos com sucesso!
```

---

## 🧪 Teste da Funcionalidade

### **Teste Rápido:**
```bash
# Executar demonstração
python test_templates.py

# Testar aplicação
python main.py
```

### **Verificação:**
1. Execute a aplicação
2. Marque "Expandir templates"
3. Extraia uma página com templates
4. Compare resultado com versão anterior
5. Observe logs de expansão

---

## 🏆 Resultado Final

### **Antes:**
- ❌ `[Template: Servidor_de_Arquivos]`
- ❌ Informação perdida
- ❌ Edição manual necessária

### **Depois:**
- ✅ Conteúdo completo do template
- ✅ Parâmetros aplicados corretamente  
- ✅ Markdown rico e estruturado
- ✅ Pronto para BookStack

**A expansão de templates transforma uma migração básica em uma migração completa e preservativa do conteúdo!** 🚀

---

## 📚 Arquivos Relacionados

- `src/template_extractor.py` - Motor de expansão de templates
- `src/wikitext_parser.py` - Parser avançado de wikitext  
- `test_templates.py` - Testes e demonstrações
- Interface atualizada em `main.py`

**Sua migração MediaWiki → BookStack agora preserva TODO o conteúdo dos templates!** 🎯
