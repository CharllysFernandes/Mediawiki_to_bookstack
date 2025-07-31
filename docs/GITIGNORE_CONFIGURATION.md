# 📋 Configuração do .gitignore

## Arquivos e Pastas Ignoradas

Este projeto utiliza um arquivo `.gitignore` abrangente para evitar que arquivos temporários, gerados automaticamente ou sensíveis sejam incluídos no controle de versão.

### 🗂️ Pastas de Extração

Todas as pastas geradas pela funcionalidade de extração são ignoradas:

```
extracted_markdown_*/    # Páginas extraídas em formato Markdown
extracted_txt_*/         # Páginas extraídas em formato TXT
exported_markdown_*/     # Páginas exportadas via "Salvar Wikitext"
demo_txt_extraction/     # Demonstrações do notebook
```

**Padrão de nomenclatura:** `extracted_[formato]_YYYYMMDD_HHMMSS/`

### 📄 Logs

Todos os arquivos de log são ignorados:

```
logs/                    # Diretório de logs
*.log                    # Qualquer arquivo .log
app.log                  # Log principal da aplicação
```

### 🐍 Cache Python

Arquivos de bytecode Python são ignorados:

```
__pycache__/             # Diretórios de cache
*.py[cod]               # Arquivos compilados Python
*$py.class              # Arquivos de classe Python
*.so                    # Bibliotecas compartilhadas
```

### 🔐 Configurações Sensíveis

Arquivos com dados sensíveis são protegidos:

```
config/settings.json     # Configurações com credenciais
config/pages_cache.json  # Cache de páginas (pode ser grande)
```

### 🗃️ Arquivos Temporários

Diversos tipos de arquivos temporários:

```
*.tmp                    # Arquivos temporários
*.temp                   # Arquivos temporários
*.bak                    # Backups
*.backup                 # Backups
.DS_Store               # Metadados do macOS
Thumbs.db               # Cache de thumbnails do Windows
```

### 🧪 Ambiente de Desenvolvimento

Diretórios e arquivos de desenvolvimento:

```
venv/                    # Ambiente virtual Python
.venv/                   # Ambiente virtual alternativo
.env                     # Variáveis de ambiente
.ipynb_checkpoints/      # Checkpoints do Jupyter
.vscode/settings.json    # Configurações pessoais do VS Code
.idea/                   # Configurações do PyCharm/IntelliJ
```

## 📊 Benefícios

### ✅ Repositório Limpo
- Apenas código fonte e documentação relevante
- Sem arquivos temporários ou gerados
- Histórico de commits focado em mudanças reais

### 🔒 Segurança
- Credenciais protegidas contra commit acidental
- Dados sensíveis não expostos no repositório
- Configurações pessoais mantidas locais

### 📈 Performance
- Clones mais rápidos (menos arquivos)
- Operações Git mais eficientes
- Menos conflitos de merge

### 🤝 Colaboração
- Cada desenvolvedor mantém suas configurações
- Arquivos gerados não causam conflitos
- Foco nas mudanças de código

## 🚀 Uso Prático

### Verificar Arquivos Ignorados
```bash
git status --ignored
```

### Forçar Adição de Arquivo Ignorado
```bash
git add -f arquivo_ignorado.log
```

### Limpar Cache Git
```bash
git rm -r --cached .
git add .
git commit -m "Aplicar .gitignore"
```

## 📋 Manutenção

### Quando Adicionar Novos Padrões

1. **Nova funcionalidade de extração** → Adicionar padrão da pasta gerada
2. **Novos tipos de log** → Incluir extensões específicas
3. **Ferramentas de desenvolvimento** → Ignorar configurações específicas
4. **Arquivos temporários** → Adicionar novas extensões

### Exemplo de Atualização

Se criar uma nova funcionalidade que gera pastas `converted_html_*`:

```diff
# ===== PASTAS DE EXTRAÇÃO =====
extracted_markdown_*/
extracted_txt_*/
exported_markdown_*/
+converted_html_*/
demo_txt_extraction/
```

## 🎯 Resultado

Com esta configuração, o repositório mantém apenas:
- ✅ Código fonte Python
- ✅ Documentação
- ✅ Configurações estruturais
- ✅ Notebooks demonstrativos
- ✅ Arquivos README

E ignora automaticamente:
- ❌ Pastas de extração temporárias
- ❌ Logs de execução
- ❌ Cache Python
- ❌ Configurações pessoais
- ❌ Dados sensíveis

O resultado é um repositório limpo, seguro e eficiente para desenvolvimento colaborativo.
