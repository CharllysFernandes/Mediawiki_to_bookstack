# 📤 Funcionalidade "Enviar Páginas" - Guia Completo

## 🎯 Visão Geral

A nova funcionalidade **"Enviar Páginas"** permite enviar páginas extraídas do MediaWiki diretamente para o BookStack, mantendo a organização hierárquica e preservando o conteúdo com formatação adequada.

## ✨ Características Implementadas

### 🖥️ Interface Intuitiva
- **Navegação lateral**: Novo botão "📤 Enviar Páginas" na barra lateral
- **Layout dividido**: Painel esquerdo (páginas) + painel direito (BookStack)
- **Interface responsiva**: Scrollable frames para grandes volumes de dados

### 📄 Gestão de Páginas
- **Lista completa**: Todas as páginas em cache são exibidas
- **Cores por status**:
  - 🔵 **Azul**: Páginas apenas em cache (status 1)
  - 🟢 **Verde**: Páginas já enviadas ao BookStack (status 2)
- **Filtros avançados**:
  - Por status: "Todos", "Apenas em Cache", "Enviadas"
  - Por busca: Campo de texto para localizar páginas específicas
- **Seleção em massa**: Botões "Selecionar Todas" e "Deselecionar Todas"

### 📚 Navegação Hierárquica BookStack
- **Estrutura completa**: Livros → Capítulos → Páginas
- **Navegação breadcrumb**: Mostra caminho atual
- **Botões de navegação**: Voltar entre níveis
- **Opções de destino**:
  - **Livro**: Criar páginas diretamente no livro
  - **Capítulo**: Criar páginas dentro de um capítulo específico
  - **Página existente**: Substituir conteúdo de página existente

### 🔄 Sincronização Inteligente
- **Conversão automática**: Wikitext → HTML para BookStack
- **Preservação de formatação**: Cabeçalhos, listas, links, negrito/itálico
- **Metadados**: Adiciona timestamp de importação
- **Atualização de status**: Páginas enviadas ficam marcadas como "enviadas"

## 🚀 Como Usar

### 1. **Pré-requisitos**
```bash
✅ MediaWiki configurado e conectado
✅ BookStack configurado (URL + tokens API)
✅ Páginas extraídas em cache
```

### 2. **Acessar a Funcionalidade**
1. Faça login no MediaWiki
2. Clique em **"📤 Enviar Páginas"** na barra lateral
3. A tela será dividida em dois painéis

### 3. **Selecionar Páginas**
- **Painel Esquerdo**: Lista de páginas em cache
- **Filtrar por status**: Escolha entre "Todos", "Apenas em Cache", "Enviadas"
- **Buscar**: Digite parte do título para filtrar
- **Selecionar**: Marque checkboxes das páginas desejadas
- **Seleção rápida**: Use "Selecionar Todas" ou "Deselecionar Todas"

### 4. **Escolher Destino no BookStack**
- **Painel Direito**: Estrutura hierárquica do BookStack
- **Navegar**: Clique nos livros para ver capítulos
- **Selecionar destino**:
  - 📖 **Livro**: Páginas serão criadas diretamente no livro
  - 📑 **Capítulo**: Páginas serão criadas dentro do capítulo
  - 📄 **Página**: Substituirá o conteúdo da página existente

### 5. **Enviar Páginas**
- **Verificar seleção**: Painel inferior mostra resumo da operação
- **Clicar em "📤 Enviar para BookStack"**
- **Acompanhar progresso**: Barra de progresso mostra andamento
- **Ver resultados**: Log mostra sucessos e falhas

## 🔧 Funcionalidades Técnicas

### ⚡ Performance
- **Cache otimizado**: Índices por ID e status para acesso O(1)
- **Processamento em thread**: Não trava interface durante envio
- **Progresso em tempo real**: Atualização visual do andamento

### 🔒 Segurança
- **Validação de dados**: Verificação antes do envio
- **Tratamento de erros**: Captura e exibe erros específicos
- **Fallback gracioso**: Continua processamento mesmo com falhas pontuais

### 🔄 Conversão de Conteúdo
- **Wikitext para HTML**: Conversão automática preservando estrutura
- **Suporte a elementos**:
  - Cabeçalhos (==, ===, ====, =====)
  - Formatação ('''negrito''', ''itálico'')
  - Links ([[internos]], [externos])
  - Listas (* item, # numerada)
  - Parágrafos e quebras de linha

## 📊 Status e Indicadores

### 🎨 Códigos de Cor
| Cor | Status | Significado |
|-----|--------|-------------|
| 🔵 Azul | Cache (1) | Página extraída, não enviada |
| 🟢 Verde | Enviada (2) | Página já enviada ao BookStack |

### 📡 Status de Conexão
- ✅ **Verde**: Conectado ao BookStack
- ❌ **Vermelho**: Erro de conexão
- 🔄 **Laranja**: Verificando conexão

### 📈 Progresso de Envio
- **Contador**: "Enviando... 3/10 (30%)"
- **Log detalhado**: Sucessos e falhas por página
- **Resultado final**: Resumo da operação

## ⚠️ Resolução de Problemas

### Problemas Comuns

**❌ "BookStack não configurado"**
- **Solução**: Configure URL, Token ID e Token Secret nas Configurações

**❌ "Nenhuma página em cache"**
- **Solução**: Use a aba "Páginas" para extrair conteúdo primeiro

**❌ "Erro ao carregar livros"**
- **Solução**: Verifique conectividade e permissões do token

**❌ "Falha ao enviar página"**
- **Solução**: Verifique se o destino existe e se há permissões adequadas

### Logs de Debug
- **Localização**: Aba principal mostra logs em tempo real
- **Arquivo**: `logs/app.log` para análise detalhada
- **Níveis**: INFO (normal), ERROR (problemas)

## 🔮 Roadmap Futuro

### Em Desenvolvimento
- 🖼️ **Upload de imagens**: Envio automático de imagens vinculadas
- 📁 **Criação de estrutura**: Auto-criar livros/capítulos conforme necessário
- 🔄 **Sincronização bidirecional**: Atualizar MediaWiki com mudanças do BookStack
- 📋 **Templates**: Modelos de conversão personalizáveis

### Melhorias Planejadas
- **Preview**: Visualizar como ficará no BookStack antes de enviar
- **Agendamento**: Envio automático em horários específicos
- **Backup**: Backup automático antes de substituir páginas
- **Relatórios**: Relatórios detalhados de importação

## 💡 Dicas de Uso

### 🎯 Melhores Práticas
1. **Teste primeiro**: Use páginas de teste antes de importação em massa
2. **Organize estrutura**: Crie livros/capítulos no BookStack antes de importar
3. **Verifique permissões**: Certifique-se que o token tem permissões adequadas
4. **Monitore logs**: Acompanhe logs para identificar problemas rapidamente

### 🚀 Otimização
- **Lotes pequenos**: Importe em pequenos lotes para melhor controle
- **Conexão estável**: Use rede estável para evitar interrupções
- **Backup regular**: Faça backup do BookStack antes de grandes importações

---

**Versão:** 2.0  
**Data:** Julho 2025  
**Compatibilidade:** MediaWiki + BookStack API v1+  
**Status:** ✅ Funcional e Pronto para Produção
