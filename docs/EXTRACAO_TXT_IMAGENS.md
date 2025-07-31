# 🖼️ Nova Funcionalidade: Extração TXT + Imagens

**Data:** 31 de julho de 2025  
**Status:** ✅ Implementado

## 🎯 Funcionalidade Adicionada

### **Botão "Extrair TXT + Imagens"**
- ✅ **Novo botão** roxo na interface principal
- ✅ **Extração completa** de texto + download de imagens
- ✅ **Processamento automático** de procedimentos com imagens
- ✅ **Relatórios detalhados** de todo o processo

---

## 🚀 Como Funciona

### **Interface:**
```
[Extrair Pendentes] [Extrair Markdown] [Extrair TXT] [Extrair TXT + Imagens]
```

### **Processo de Extração Completa:**
1. **Validação:** Verifica conexão e páginas selecionadas
2. **Fase 1:** Extrai conteúdo de texto (wikitext)
3. **Fase 2:** Identifica imagens nas páginas
4. **Fase 3:** Baixa todas as imagens encontradas
5. **Salvamento:** Organiza arquivos TXT + imagens em pastas
6. **Relatório:** Gera relatórios detalhados

---

## 🔧 Implementação Técnica

### **Componentes Principais:**

#### **1. `MediaWikiImageDownloader`** (novo módulo)
- **Propósito:** Sistema completo de download de imagens
- **Formatos:** JPG, PNG, GIF, BMP, WebP, SVG, TIFF, PDF
- **Fonte:** Extrai de wikitext e HTML renderizado
- **Cache:** Evita downloads duplicados

#### **2. `extract_txt_with_images()`**
- **Propósito:** Função principal da nova funcionalidade
- **Thread:** Executa em background
- **Progress:** Barra de progresso em tempo real
- **Auto-save:** Salva arquivos e relatórios automaticamente

#### **3. Detecção Inteligente de Imagens**
- **Wikitext:** `[[Arquivo:nome.jpg]]`, `[[File:imagem.png]]`
- **HTML:** `<img src="...">`, links para imagens
- **API:** Informações detalhadas via `imageinfo`
- **URLs:** Normalização automática de URLs

---

## 📁 Estrutura dos Arquivos Gerados

### **Diretório Principal:**
```
extracted_txt_images_20250731_143052/
├── RELATORIO_COMPLETO.txt     ← Relatório detalhado
├── INDICE.txt                 ← Índice dos arquivos TXT
├── pagina_exemplo.txt         ← Conteúdo da página
├── procedimento_x.txt         ← Outro procedimento
└── images/                    ← Todas as imagens
    ├── pagina_exemplo/
    │   ├── screenshot01.png
    │   ├── diagrama.jpg
    │   └── manual.pdf
    └── procedimento_x/
        ├── passo1.jpeg
        ├── passo2.jpeg
        └── resultado.png
```

### **RELATORIO_COMPLETO.txt:**
```
RELATÓRIO COMPLETO - EXTRAÇÃO TXT + IMAGENS
===============================================

Data de extração: 31/07/2025 14:30:52
Diretório: extracted_txt_images_20250731_143052
Total de páginas: 15

RESUMO DE IMAGENS:
------------------------------
Imagens encontradas: 47
Imagens baixadas: 43
Imagens que falharam: 4
Taxa de sucesso: 91.5%

DETALHES POR PÁGINA:
==============================

  1. AGU - Procedimento XnView
     Arquivo TXT: AGU_Procedimento_XnView.txt
     Imagens encontradas: 3
     Imagens baixadas: 3
     Arquivos: screenshot01.png, manual.pdf, resultado.jpg

...
```

---

## 🎯 Tipos de Imagens Processadas

### **Formatos Suportados:**
- **Imagens:** JPG, JPEG, PNG, GIF, BMP, WebP, SVG, TIFF
- **Documentos:** PDF (quando referenciado como imagem)
- **Ícones:** ICO

### **Fontes de Extração:**
- **Wikitext:** `[[Arquivo:nome.ext]]`, `[[File:imagem.ext]]`
- **HTML renderizado:** `<img>` tags, links para imagens
- **Templates expandidos:** Imagens dentro de templates
- **URLs diretas:** Links HTTP/HTTPS para imagens

---

## 💡 Vantagens da Nova Funcionalidade

### **1. Extração Completa**
- ✅ **Texto + Imagens:** Procedimentos completos
- ✅ **Organização:** Estrutura clara de diretórios
- ✅ **Metadados:** Informações detalhadas
- ✅ **Relatórios:** Estatísticas de todo o processo

### **2. Robustez**
- ✅ **Multiple Sources:** Wikitext + HTML
- ✅ **Error Handling:** Continua mesmo com falhas
- ✅ **Retry Logic:** Tenta novamente downloads falhados
- ✅ **Cache System:** Evita downloads duplicados

### **3. Facilidade de Uso**
- ✅ **Um clique:** Todo o processo automatizado
- ✅ **Progress:** Acompanhamento em tempo real
- ✅ **Logs:** Informações detalhadas no console
- ✅ **Resultados:** Arquivos prontos para uso

---

## 🎨 Design e UX

### **Visual:**
- 🟣 **Cor roxa diferenciada** para o botão
- 📊 **Progress bar** específica "Extraindo: X/Y"
- 📋 **Status detalhado** "TXT+IMG: Xp/Yi | Cache: Z%"

### **Comportamento:**
- 🔒 **Botão desabilitado** durante extração
- 🔄 **Interface responsiva** durante processamento
- 📝 **Log detalhado** de todo o processo
- 🎯 **Cache atualizado** automaticamente

---

## 📊 Exemplo de Uso

### **Cenário:** Extrair procedimentos da AGU
1. **Conectar** à wiki da AGU
2. **Carregar Cache** de páginas
3. **Filtrar** páginas com procedimentos
4. **Selecionar** as páginas desejadas
5. **Clicar "Extrair TXT + Imagens"** 🟣
6. **Aguardar processamento** (texto + imagens)
7. **Verificar resultados** no relatório
8. **Usar arquivos** em documentação externa

### **Resultado:**
- 📄 **Arquivos TXT** com procedimentos completos
- 🖼️ **Imagens organizadas** por procedimento
- 📋 **Relatórios detalhados** de todo o processo
- ✅ **Pronto para uso** em sistemas externos

---

## 🔧 Configurações e Opções

### **Parâmetros do Image Downloader:**
- **Timeout:** 30 segundos por imagem
- **Max Retries:** 3 tentativas por imagem
- **Delay:** 0.5s entre downloads
- **Extensões:** .jpg, .png, .gif, .bmp, .webp, .svg, .tiff, .pdf

### **Otimizações:**
- **Cache de URLs:** Evita processamento duplicado
- **Sanitização:** Nomes de arquivo seguros
- **Progress Tracking:** Acompanhamento detalhado
- **Error Recovery:** Continua mesmo com falhas

---

## 📋 Status de Implementação

- ✅ **Módulo MediaWikiImageDownloader** criado
- ✅ **Função extract_txt_with_images()** implementada
- ✅ **Worker thread** para background processing
- ✅ **Progress feedback** em tempo real
- ✅ **Auto-save** de arquivos TXT e imagens
- ✅ **Relatórios detalhados** gerados
- ✅ **Error handling** completo
- ✅ **Cache integration** funcionando
- ✅ **Sanitização** de nomes de arquivos
- ✅ **Organização** em diretórios estruturados

---

**Status Final:** ✅ **Nova funcionalidade "Extrair TXT + Imagens" completamente implementada e funcional!** 🖼️🚀

Agora os usuários podem extrair procedimentos completos incluindo todas as imagens, criando pacotes prontos para uso em documentação externa ou sistemas como BookStack.
