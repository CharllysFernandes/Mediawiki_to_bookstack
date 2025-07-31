# 📚 MediaWiki to BookStack - Conversor Avançado

Um conversor robusto e completo para extrair conteúdo do MediaWiki e prepará-lo para BookStack ou outras plataformas de documentação.

## 🎯 Funcionalidades Principais

### **✅ Extração de Conteúdo**
- **Wikitext** - Formato original para reimportação
- **Markdown** - Formato universal para documentação
- **TXT** - Formato simples e compatível
- **🆕 TXT + Imagens** - Extração completa com download de imagens

### **✅ Sistema de Imagens (NOVO!)**
- **Download automático** de todas as imagens referenciadas
- **Organização inteligente** em diretórios por página
- **Múltiplos formatos**: JPG, PNG, GIF, BMP, WebP, SVG, TIFF, PDF
- **Relatórios detalhados** de todo o processo

### **✅ Interface Avançada**
- **Interface gráfica** moderna com CustomTkinter
- **Sistema de paginação** para wikis grandes
- **Cache inteligente** para melhor performance
- **Progress bars** e feedback em tempo real

### **✅ Recursos Profissionais**
- **Bypass de restrições** com múltiplas estratégias
- **Expansão de templates** para conteúdo completo
- **Processamento em lotes** otimizado
- **Sistema de logs** detalhado

---

## 🖼️ Nova Funcionalidade: Extração TXT + Imagens

### **Como Usar:**
1. Execute `python main.py`
2. Configure conexão com sua wiki
3. Vá para aba **"Páginas"**
4. Carregue o cache de páginas
5. Selecione procedimentos com imagens
6. Clique **"Extrair TXT + Imagens"** (botão roxo)
7. Aguarde o processamento completo

### **Resultado:**
```
extracted_txt_images_20250731_143052/
├── RELATORIO_COMPLETO.txt     ← Relatório detalhado
├── INDICE.txt                 ← Índice dos arquivos
├── procedimento_1.txt         ← Conteúdo do procedimento
├── procedimento_2.txt         ← Outro procedimento
└── images/                    ← Todas as imagens organizadas
    ├── procedimento_1/
    │   ├── passo1.png
    │   ├── passo2.jpg
    │   └── resultado.gif
    └── procedimento_2/
        ├── screenshot.png
        └── manual.pdf
```

### **Vantagens:**
- 🎯 **Extração completa** - texto + imagens em um processo
- 📁 **Organização automática** - estrutura clara de diretórios
- 📊 **Relatórios detalhados** - estatísticas de todo o processo
- 🔄 **Error handling** - continua mesmo com falhas
- ⚡ **Performance** - cache e otimizações inteligentes

---

## 🚀 Instalação e Configuração

### **Requisitos:**
- Python 3.7+
- Dependências do `requirements.txt`

### **Instalação:**
```bash
# Clonar o repositório
git clone https://github.com/CharllysFernandes/Mediawiki_to_bookstack.git
cd Mediawiki_to_bookstack

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
python main.py
```

### **Configuração Inicial:**
1. **URL da API**: `https://sua-wiki.com/api.php`
2. **Credenciais**: Usuário e senha da wiki
3. **Configurações SSL**: Ajustar conforme necessário
4. **Configurações avançadas**: Via botão "Configurações"

---

## 📋 Guia de Uso

### **1. Conectar à Wiki**
- Digite URL da API, usuário e senha
- Clique "Conectar" para testar conexão
- Use "Salvar Config" para persistir configurações

### **2. Gerenciar Páginas**
- **"Carregar Cache"**: Usar cache local existente
- **"Atualizar da API"**: Buscar páginas mais recentes
- **Filtros**: Buscar por nome, status ou ID
- **Paginação**: Navegar por wikis grandes

### **3. Extrair Conteúdo**

#### **Wikitext (Original)**
```
[Extrair Pendentes] → [Salvar Wikitext]
```
- Para reimportação no MediaWiki
- Preserva formatação original
- Ideal para migração entre wikis

#### **Markdown (Universal)**
```
[Extrair Markdown]
```
- Formato universal
- Ideal para GitHub, GitLab, Obsidian
- Compatível com geradores de sites estáticos

#### **TXT (Simples)**
```
[Extrair TXT]
```
- Formato simples e limpo
- Compatível com qualquer sistema
- Remoção automática de marcações wiki

#### **🆕 TXT + Imagens (Completo)**
```
[Extrair TXT + Imagens]
```
- Texto + download de todas as imagens
- Organização automática em diretórios
- Relatórios detalhados do processo
- **Ideal para procedimentos e tutoriais**

### **4. Configurações Avançadas**
- **Expandir templates**: Conteúdo completo
- **Tamanho de lote**: Páginas por requisição
- **Delay**: Tempo entre requisições
- **Cache**: Configurações de persistência

---

## 🔧 Arquitetura Técnica

### **Módulos Principais:**

#### **`src/mediawiki_client.py`**
- Cliente robusto para API MediaWiki
- Múltiplas estratégias de bypass
- Tratamento avançado de erros

#### **`src/image_downloader.py` (NOVO)**
- Sistema completo de download de imagens
- Extração de wikitext e HTML
- Cache e otimizações inteligentes

#### **`src/pages_cache.py`**
- Cache persistente de páginas
- Sistema de status e progresso
- Otimizações de performance

#### **`src/config_manager.py`**
- Gerenciamento de configurações
- Persistência de credenciais
- Configurações avançadas

### **Estratégias de Bypass:**
1. **Requisição padrão**
2. **Com token CSRF**
3. **Com header Referer**
4. **Como form data**
5. **Multiple fallbacks**

---

## 📊 Casos de Uso

### **1. Migração de Wiki**
```
MediaWiki → [Extrair Wikitext] → BookStack/Outro MediaWiki
```

### **2. Documentação Técnica**
```
MediaWiki → [Extrair Markdown] → GitHub/GitLab/Hugo
```

### **3. Procedimentos com Imagens**
```
MediaWiki → [Extrair TXT + Imagens] → Sistema Externo
```

### **4. Backup e Arquivo**
```
MediaWiki → [Extrair TXT] → Arquivo/Backup
```

---

## 🎯 Exemplo Prático: AGU

### **Cenário:**
Extrair procedimentos de TI da wiki da AGU, incluindo screenshots e manuais.

### **Processo:**
1. **Conectar** à wiki da AGU
2. **Filtrar** páginas com "Procedimento" no nome
3. **Selecionar** procedimentos relevantes
4. **Extrair TXT + Imagens**
5. **Verificar** relatório de extração

### **Resultado:**
- 📄 **50 procedimentos** em arquivos TXT
- 🖼️ **200+ imagens** organizadas por procedimento
- 📋 **Relatório completo** com estatísticas
- ✅ **Pronto para** importar no BookStack

---

## 🛡️ Tratamento de Erros

### **Estratégias Implementadas:**
- **Multiple retries** para requisições
- **Fallback methods** para páginas restritas
- **Graceful degradation** em caso de falhas
- **Logs detalhados** para troubleshooting

### **Tipos de Erro Tratados:**
- **403 Forbidden**: Bypass com métodos alternativos
- **SSL Errors**: Opção de desabilitar verificação
- **Timeout**: Configurável por requisição
- **Network Issues**: Retry automático

---

## 📚 Documentação Adicional

### **Arquivos de Documentação:**
- [`docs/EXTRACAO_TXT_IMAGENS.md`](docs/EXTRACAO_TXT_IMAGENS.md) - Nova funcionalidade
- [`docs/CONFIGURACOES_AVANCADAS.md`](docs/CONFIGURACOES_AVANCADAS.md) - Configurações
- [`docs/TEMPLATE_EXPANSION_GUIDE.md`](docs/TEMPLATE_EXPANSION_GUIDE.md) - Templates
- [`docs/SISTEMA_PAGINACAO.md`](docs/SISTEMA_PAGINACAO.md) - Paginação

### **Scripts de Demonstração:**
- [`demo_extração_imagens.py`](demo_extração_imagens.py) - Demo da nova funcionalidade
- [`MediaWiki_TXT_Extraction_Demo.ipynb`](MediaWiki_TXT_Extraction_Demo.ipynb) - Jupyter demo

---

## 🤝 Contribuição

### **Como Contribuir:**
1. Fork o repositório
2. Crie uma branch para sua feature
3. Faça as modificações
4. Teste com diferentes wikis
5. Crie um Pull Request

### **Áreas de Melhoria:**
- Novos formatos de exportação
- Otimizações de performance
- Suporte a mais tipos de arquivo
- Interface mobile

---

## 📞 Suporte

### **Problemas Conhecidos:**
- Wikis com autenticação complexa
- Templates muito aninhados
- Imagens com URLs especiais

### **Logs e Debug:**
- Logs disponíveis em `logs/app.log`
- Use configurações de debug para mais detalhes
- Verifique conectividade e permissões

---

## 🏆 Status do Projeto

### **✅ Implementado:**
- Extração Wikitext, Markdown e TXT
- **Sistema completo de imagens**
- Interface gráfica avançada
- Cache e paginação
- Bypass de restrições
- Expansão de templates

### **🔜 Próximas Funcionalidades:**
- Suporte a mais formatos de arquivo
- Integração direta com BookStack API
- Processamento paralelo de imagens
- Interface web opcional

---

**MediaWiki to BookStack** - Seu conversor completo para migração e extração de conteúdo wiki! 🚀
