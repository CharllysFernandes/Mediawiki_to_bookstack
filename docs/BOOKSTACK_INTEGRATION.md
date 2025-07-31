# Integração BookStack - Guia de Configuração

## 📚 Sobre a Integração

A integração com BookStack permite importar automaticamente o conteúdo extraído do MediaWiki diretamente para sua instância do BookStack, mantendo a organização em livros, capítulos e páginas.

## ⚙️ Configuração Inicial

### 1. Obter Credenciais da API do BookStack

1. Acesse sua instância do BookStack
2. Vá em **Configurações** → **API Tokens**
3. Clique em **Create Token**
4. Dê um nome para o token (ex: "MediaWiki Import")
5. Anote o **Token ID** e **Token Secret** gerados

### 2. Configurar na Aplicação

1. Execute a aplicação: `python main.py`
2. Clique em **Configurações** (ícone de engrenagem)
3. Na seção **📚 Configurações BookStack**:
   - **URL Base do BookStack**: Digite a URL da sua instância (ex: `https://bookstack.empresa.com`)
   - **Token ID da API**: Cole o Token ID obtido no passo 1
   - **Token Secret da API**: Cole o Token Secret obtido no passo 1
   - **Verificar certificados SSL**: Mantenha marcado para ambientes de produção
4. Clique em **🔗 Testar Conexão BookStack** para validar
5. Se o teste passar, clique em **Salvar Configurações**

## 🚀 Funcionalidades Disponíveis

### ✅ Implementado

- **Configuração de credenciais**: Interface gráfica para configurar acesso ao BookStack
- **Teste de conexão**: Validação automática das credenciais
- **Cliente BookStack completo**: API client com todas as operações CRUD
- **Persistência de configurações**: Configurações salvas automaticamente

### 🔄 Em Desenvolvimento

- **Importação automática**: Botão para importar páginas extraídas
- **Mapeamento de estruturas**: Conversão automática de namespaces para livros/capítulos
- **Upload de imagens**: Integração com o sistema de download de imagens
- **Preservação de formatação**: Conversão de wikitext para HTML do BookStack

## 🛠️ API BookStack Suportada

O cliente implementado suporta as seguintes operações:

### Livros (Books)
- ✅ Listar livros
- ✅ Criar livro
- ✅ Atualizar livro
- ✅ Deletar livro
- ✅ Exportar livro

### Capítulos (Chapters)
- ✅ Listar capítulos
- ✅ Criar capítulo
- ✅ Atualizar capítulo
- ✅ Deletar capítulo

### Páginas (Pages)
- ✅ Listar páginas
- ✅ Criar página
- ✅ Atualizar página
- ✅ Deletar página
- ✅ Exportar página

### Imagens e Anexos
- ✅ Upload de imagens
- ✅ Upload de anexos
- ✅ Gestão de gallery

## 🧪 Testando a Integração

Execute o script de demonstração:

```bash
python demo_bookstack.py
```

Este script irá:
1. Conectar ao BookStack usando suas configurações
2. Criar um livro de demonstração
3. Criar um capítulo de exemplo
4. Criar uma página de teste
5. Mostrar a URL para acessar o resultado

## 🔒 Segurança

### Certificados SSL
- Por padrão, a verificação SSL está habilitada
- Para ambientes de desenvolvimento com certificados auto-assinados, você pode desabilitar a verificação
- **NUNCA desabilite em produção**

### Armazenamento de Credenciais
- As credenciais são armazenadas localmente no arquivo `config/settings.json`
- O Token Secret é armazenado em texto plano - mantenha o arquivo seguro
- Considere usar variáveis de ambiente para ambientes de produção

## 🐛 Solução de Problemas

### Erro: "Conexão recusada"
- Verifique se a URL está correta
- Confirme se o BookStack está acessível pela rede
- Teste o acesso manual no navegador

### Erro: "Token inválido"
- Verifique se o Token ID e Secret estão corretos
- Confirme se o token não expirou
- Recrie o token se necessário

### Erro: "Certificado SSL"
- Para ambientes de desenvolvimento, desmarque "Verificar certificados SSL"
- Para produção, corrija o certificado SSL do BookStack

### Erro: "Permissões insuficientes"
- Verifique se o usuário associado ao token tem permissões adequadas
- O usuário precisa de permissões para criar livros, capítulos e páginas

## 📋 Próximos Passos

1. **Configure o MediaWiki** na aplicação principal
2. **Extraia páginas** usando a funcionalidade existente
3. **Aguarde a implementação** da importação automática (próxima versão)
4. **Teste em ambiente controlado** antes de usar em produção

## 🔗 Recursos Adicionais

- [Documentação da API BookStack](https://demo.bookstackapp.com/api/docs)
- [Configuração de Tokens BookStack](https://www.bookstackapp.com/docs/admin/hacking-bookstack/#api-authentication)
- [Repositório do projeto](https://github.com/BookStackApp/BookStack)

---

**Versão:** 1.0  
**Data:** Dezembro 2024  
**Compatibilidade:** BookStack v21.12+
