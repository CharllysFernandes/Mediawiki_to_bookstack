# 📄 Nova Funcionalidade: Extração em Markdown

**Data:** 30 de julho de 2025  
**Status:** ✅ Implementado

## 🎯 Nova Funcionalidade Adicionada

### **Botão "Extrair Markdown"**
- ✅ **Novo botão** adicionado ao lado de "Extrair Pendentes"
- ✅ **Cor diferenciada** (azul mais escuro) para distinção visual
- ✅ **Funcionalidade completa** de extração em formato Markdown

---

## 🚀 Como Funciona

### **Interface:**
```
[Extrair Pendentes] [Extrair Markdown] [Salvar Wikitext]
```

### **Processo de Extração Markdown:**
1. **Validação:** Verifica conexão e páginas selecionadas
2. **Extração:** Busca conteúdo em formato Markdown da API
3. **Processamento:** Converte e organiza o conteúdo
4. **Salvamento:** Salva automaticamente arquivos .md
5. **Relatório:** Exibe estatísticas de sucesso/falhas

---

## 🔧 Implementação Técnica

### **Funções Adicionadas:**

#### **1. `extract_markdown_content()`**
- **Propósito:** Função principal para iniciar extração Markdown
- **Validações:** Conexão + páginas selecionadas
- **Thread:** Executa em background para não travar UI

#### **2. `_extract_markdown_worker()`**
- **Propósito:** Worker thread para processamento
- **API Call:** `format_type='markdown'` ao invés de 'wikitext'
- **Progress:** Callback de progresso em tempo real
- **Auto-save:** Salva arquivos automaticamente após extração

#### **3. `_save_markdown_files()`**
- **Propósito:** Salva arquivos .md automaticamente
- **Estrutura:** Diretório timestampado `extracted_markdown_YYYYMMDD_HHMMSS`
- **Formato:** Cada página = 1 arquivo .md com cabeçalho

#### **4. `_create_markdown_index()`**
- **Propósito:** Cria README.md com índice de arquivos
- **Conteúdo:** Lista de sucessos + erros + metadados

---

## 📁 Estrutura dos Arquivos Gerados

### **Diretório de Saída:**
```
extracted_markdown_20250730_143052/
├── README.md                    # Índice geral
├── Página_Principal.md          # Página convertida
├── Ajuda_Edição.md             # Página convertida
├── MediaWiki_Sintaxe.md        # Página convertida
└── ...
```

### **Formato de Cada Arquivo .md:**
```markdown
# Título da Página

**Fonte:** MediaWiki  
**Data de extração:** 30/07/2025 14:30:52  
**Formato:** Markdown

---

[Conteúdo da página em Markdown...]
```

### **README.md (Índice):**
```markdown
# 📚 Índice de Páginas Extraídas - Markdown

**Data de extração:** 30/07/2025 14:30:52  
**Formato:** Markdown  
**Total de páginas:** 15

---

## ✅ Páginas Extraídas com Sucesso

1. **[Página Principal](./Página_Principal.md)**
2. **[Ajuda](./Ajuda_Edição.md)**
...

## ❌ Páginas com Erro

1. **Página Restrita** - *Acesso negado*
...
```

---

## 🎯 Diferenças entre Extração Wikitext vs Markdown

| Aspecto | Wikitext | Markdown |
|---------|----------|----------|
| **Formato** | Código MediaWiki bruto | Markdown padronizado |
| **Compatibilidade** | Apenas MediaWiki | Universal (GitHub, GitLab, etc.) |
| **Legibilidade** | Técnico | Fácil leitura |
| **Templates** | Preserva sintaxe {{}} | Expandido/convertido |
| **Links** | [[Página]] | [Página](link) |
| **Uso** | Importação MediaWiki | Documentação geral |
| **Processamento** | Menor | Maior (conversão) |

---

## 🚀 Fluxo de Trabalho Atualizado

### **Para Extração Markdown:**
1. **Conectar** à wiki
2. **Carregar Cache** de páginas
3. **Navegar** e **selecionar páginas**
4. **Clicar "Extrair Markdown"** 📄
5. **Aguardar processamento** (barra de progresso)
6. **Verificar resultados** no relatório
7. **Localizar arquivos** na pasta gerada

### **Para Extração Wikitext (Original):**
1. **Conectar** à wiki
2. **Carregar Cache** de páginas  
3. **Navegar** e **selecionar páginas**
4. **Clicar "Extrair Pendentes"** ⚙️
5. **Aguardar processamento**
6. **Clicar "Salvar Wikitext"** para salvar

---

## 📊 Relatório de Extração

### **Exemplo de Saída:**
```
=== EXTRAÇÃO MARKDOWN CONCLUÍDA ===
Páginas selecionadas: 10
Extraídas com sucesso: 8
Falharam: 2

=== PROGRESSO GERAL ===
Total no cache: 1,250 páginas
Processadas: 856 páginas
Pendentes: 394 páginas
Progresso: 68.5%

=== PÁGINAS COM ERRO ===
❌ Página Administrativa: Acesso negado
❌ Template Complexo: Erro de conversão

✅ Páginas processadas foram marcadas como concluídas no cache
📄 8 arquivos Markdown prontos para download
```

---

## 💡 Vantagens da Extração Markdown

### **1. Compatibilidade Universal**
- ✅ **GitHub/GitLab:** Documentação de projetos
- ✅ **Obsidian/Notion:** Bases de conhecimento
- ✅ **Hugo/Jekyll:** Sites estáticos
- ✅ **Editores:** VS Code, Typora, etc.

### **2. Facilidade de Uso**
- ✅ **Leitura direta** sem processamento
- ✅ **Edição simples** em qualquer editor
- ✅ **Versionamento** com Git
- ✅ **Busca de texto** nativa

### **3. Processamento Otimizado**
- ✅ **Auto-save:** Salva automaticamente
- ✅ **Organização:** Índice + estrutura clara
- ✅ **Metadados:** Data, fonte, formato
- ✅ **Sanitização:** Nomes de arquivo seguros

---

## 🎨 Design e UX

### **Visual:**
- 🔵 **Cor azul diferenciada** para o botão Markdown
- 📊 **Progress bar** específica "Extraindo Markdown: X/Y"
- ✅ **Status** atualizado "Markdown: X/Y | Cache: Z%"

### **Comportamento:**
- 🔒 **Botão desabilitado** durante extração
- 🔄 **Interface responsiva** durante processamento
- 📝 **Log detalhado** de todo o processo
- 🎯 **Cache atualizado** automaticamente

---

## 📋 Status de Implementação

- ✅ **Botão adicionado** à interface
- ✅ **Função principal** implementada
- ✅ **Worker thread** para background
- ✅ **Auto-save** de arquivos Markdown
- ✅ **Índice README.md** gerado
- ✅ **Progress feedback** em tempo real
- ✅ **Error handling** completo
- ✅ **Cache integration** funcionando
- ✅ **Sanitização** de nomes de arquivos
- ✅ **Metadados** em cada arquivo

---

**Status Final:** ✅ **Nova funcionalidade de extração Markdown completamente implementada e funcional!** 📄🚀

Agora os usuários podem extrair páginas tanto em **Wikitext** (para reimportação) quanto em **Markdown** (para documentação e uso geral).
