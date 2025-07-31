# Sistema de Navegação Lateral

## Visão Geral

O projeto MediaWiki to BookStack agora conta com um sistema de navegação lateral moderno, implementado com CustomTkinter, que oferece uma experiência de usuário mais intuitiva e organizada.

## Funcionalidades

### 🎯 Barra de Navegação Lateral

- **Design Fixo**: Barra lateral de 200px de largura sempre visível
- **Logo/Título**: "MediaWiki to BookStack" no topo da barra
- **Status de Conexão**: Indicador visual do estado da conexão (●)
- **Navegação por Botões**: Três botões principais com ícones

### 📱 Rotas de Navegação

#### 1. 🔐 Login
- **Função**: Tela de autenticação e configuração da conexão
- **Componentes**:
  - Campos de URL da API, usuário e senha
  - Checkboxes para configurações (SSL, bypass, bot mode, etc.)
  - Botões para conectar, salvar e carregar configurações
  - Status da conexão

#### 2. 📄 Páginas
- **Estado**: Desabilitado até fazer login
- **Função**: Gerenciamento e extração de páginas da wiki
- **Componentes**:
  - Informações da conexão estabelecida
  - Botões para testes e listagem de prefixos
  - Gerenciamento de cache de páginas
  - Seleção e extração de conteúdo
  - Salvamento em formato wikitext

#### 3. ⚙️ Configurações
- **Função**: Acesso às configurações avançadas
- **Componentes**:
  - Botão para abrir janela de configurações detalhadas
  - Informações sobre categorias disponíveis
  - Documentação das funcionalidades

## Características Técnicas

### 🔧 Implementação

```python
# Estrutura principal do navigation rail
nav_rail = ctk.CTkFrame(main_container, width=200, corner_radius=0)
nav_rail.pack(side="left", fill="y")
nav_rail.pack_propagate(False)

# Sistema de navegação
def navigate_to(self, view_name):
    # Atualiza estado dos botões
    # Esconde view atual
    # Mostra nova view
    # Atualiza título
```

### 🎨 Design System

- **Cor do Tema**: Azul (blue theme)
- **Modo de Aparência**: Escuro (dark mode)
- **Tipografia**: CTkFont com variações de tamanho e peso
- **Ícones**: Emojis para identificação visual dos botões

### 🔄 Estados dos Botões

- **Login**: Sempre disponível
- **Páginas**: Desabilitado até autenticação bem-sucedida
- **Configurações**: Sempre disponível
- **Estado Ativo**: Botão desabilitado quando view está ativa

## Fluxo de Uso

### 1. Inicialização
- App abre na view de **Login**
- Botão "Páginas" desabilitado
- Status mostra "● Desconectado" em vermelho

### 2. Autenticação
- Usuário preenche dados e clica "Conectar"
- Sistema valida credenciais em thread separada
- Sucesso: navega automaticamente para "Páginas"
- Status atualiza para "● Conectado" em verde

### 3. Navegação
- Usuário pode alternar entre views clicando nos botões
- View atual sempre destacada (botão desabilitado)
- Informações persistem entre navegações

### 4. Logout
- Botão "Sair" na view de Páginas
- Retorna automaticamente para Login
- Desabilita acesso às Páginas

## Vantagens da Nova Interface

### ✅ Melhorias de UX
- **Navegação Intuitiva**: Menu lateral sempre visível
- **Status Visual**: Indicadores claros do estado da aplicação
- **Organização**: Separação clara de funcionalidades
- **Responsividade**: Interface adaptável e fluida

### ✅ Melhorias Técnicas
- **Código Modular**: Views separadas e organizadas
- **Gerenciamento de Estado**: Estado da aplicação centralizado
- **Threading**: Operações não bloqueantes da interface
- **Manutenibilidade**: Estrutura mais fácil de expandir

## Configurações Avançadas

O sistema mantém compatibilidade total com a janela de configurações avançadas, agora acessível através da view "Configurações". As categorias incluem:

- **🔌 Conexão**: URLs, credenciais, SSL
- **📤 Extração**: Templates, parsing, formato
- **💾 Cache**: Gerenciamento de cache
- **🎨 Interface**: Personalização da UI

## Migração de Funcionalidades

Todas as funcionalidades existentes foram preservadas e reorganizadas:

- ✅ Sistema de login/logout mantido
- ✅ Extração de páginas preservada
- ✅ Cache de páginas funcional
- ✅ Configurações avançadas acessíveis
- ✅ Logs e status mantidos
- ✅ Threading para operações pesadas

## Próximos Passos

O sistema de navegação lateral oferece uma base sólida para futuras expansões:

- 📊 Dashboard com estatísticas
- 🔍 Sistema de busca integrado
- 📈 Métricas de extração
- 🎯 Filtros avançados de páginas
- 📝 Editor de templates
