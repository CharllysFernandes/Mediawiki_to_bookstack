# Correção de Erro 403 - BookStack API Permissions

## Problema Identificado

O usuário está recebendo o erro:
```
"O proprietário do código de API utilizado não tem permissão para fazer requisições de API"
```

Este é um erro específico do BookStack indicando que o **usuário associado ao token não tem as permissões necessárias** para usar a API.

## 🔍 Diagnóstico Rápido

Execute o script de diagnóstico para identificar exatamente qual permissão está faltando:

```bash
python test_bookstack_permissions.py
```

## 🛠️ Soluções por Ordem de Prioridade

### 1. **VERIFICAR ROLE "API ACCESS"** (Mais Comum)

1. **Acesse o BookStack como administrador**
2. **Vá em:** `Configurações` → `Usuários`
3. **Encontre o usuário** que criou o token de API
4. **Clique em "Editar"** no usuário
5. **Na seção "Roles"**, verifique se tem uma role com permissão "API Access"
6. **Se não tiver:** 
   - Atribua uma role existente com "API Access", OU
   - Crie uma nova role com as permissões necessárias

### 2. **CRIAR NOVA ROLE COM PERMISSÕES ADEQUADAS**

Se não existe uma role adequada:

1. **Vá em:** `Configurações` → `Roles & Permissions`
2. **Clique em "Create Role"**
3. **Configure a role:**
   - **Nome:** `API User` ou similar
   - **Descrição:** `Usuário com acesso à API`
   - **Marque as permissões:**
     - ✅ **API Access** (essencial)
     - ✅ **Create Pages** (para criar páginas)
     - ✅ **View Books** (para listar livros)
     - ✅ **View Chapters** (se usar capítulos)
4. **Salve a role**
5. **Volte ao usuário** e atribua esta nova role

### 3. **USAR TOKEN DE ADMINISTRADOR** (Solução Rápida)

Se as opções acima são complicadas:

1. **Faça login no BookStack** com uma conta administrador
2. **Vá em:** `Configurações` → `API Tokens`
3. **Crie um novo token** com a conta de administrador
4. **Use este token** no aplicativo

### 4. **VERIFICAR PERMISSÕES ESPECÍFICAS POR LIVRO**

Mesmo com "API Access", podem existir restrições por livro:

1. **Vá ao livro específico** onde quer criar páginas
2. **Clique no ícone de configurações** do livro
3. **Vá em "Permissions"**
4. **Verifique se o usuário** (ou sua role) tem permissão "Create"
5. **Se não tiver,** adicione a permissão ou mude para "Inherit"

## 🧪 Testes de Validação

### Teste 1: Conexão Básica
```bash
# Execute o script de diagnóstico
python test_bookstack_permissions.py
```

### Teste 2: Via Interface Gráfica
1. **Abra o aplicativo**
2. **Vá na aba "Configurações"**
3. **Configure suas credenciais BookStack**
4. **Clique em "Testar Conexão"**
5. **Verifique os logs** - agora deve mostrar permissões de criação

### Teste 3: Envio de Página de Teste
1. **Se os testes acima passaram,** tente enviar uma página simples
2. **Monitore os logs** para verificar se funcionou

## 📋 Checklist de Verificação

- [ ] Token ID e Secret estão corretos
- [ ] URL do BookStack está correta
- [ ] Usuário do token existe no BookStack
- [ ] Usuário tem uma role atribuída
- [ ] Role tem permissão "API Access"
- [ ] Role tem permissão "Create Pages"
- [ ] Livro de destino permite criação pelo usuário
- [ ] Teste de conexão passa sem erros

## 🔧 Configuração Recomendada

### Role Ideal para API:
```
Nome: "API Integration User"
Permissões:
✅ API Access
✅ View Books  
✅ View Chapters
✅ Create Pages
✅ Update Own Pages (opcional)
❌ Delete Pages (não recomendado)
❌ Manage Users (não necessário)
```

### Permissões por Livro:
```
Para livros onde vai importar:
✅ View: Sim
✅ Create: Sim  
✅ Update: Sim (se quiser atualizar)
❌ Delete: Não (por segurança)
```

## 🚨 Erros Conhecidos e Soluções

### "O proprietário do código de API utilizado não tem permissão"
- **Causa:** Usuário sem role "API Access"
- **Solução:** Atribuir role com "API Access"

### "403 Forbidden" em livros específicos
- **Causa:** Permissões insuficientes no livro
- **Solução:** Configurar permissões do livro

### "500 Server Error" no endpoint `/users/me`
- **Causa:** Bug conhecido em algumas versões
- **Solução:** O aplicativo já tem fallback automático

### Token aparentemente correto mas não funciona
- **Causa:** Token pode ter expirado
- **Solução:** Gerar novo token

## 📞 Suporte Adicional

Se mesmo seguindo estas instruções o problema persistir:

1. **Execute:** `python test_bookstack_permissions.py`
2. **Copie a saída completa** do diagnóstico
3. **Verifique os logs** do servidor BookStack (se tiver acesso)
4. **Confirme a versão** do BookStack em uso

## 🎯 Resultado Esperado

Após aplicar as correções, você deve ver:

```
✅ Teste de conexão BookStack: SUCESSO
   👤 Usuário: [Seu Nome]
   ✅ Permissões: Permissões OK
   🆔 ID: [ID do usuário]
```

E o envio de páginas deve funcionar sem erros 403.
