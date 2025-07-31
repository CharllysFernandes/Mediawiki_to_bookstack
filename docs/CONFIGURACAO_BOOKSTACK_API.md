# 🔧 Configuração de API do BookStack

## ❌ **PROBLEMA COMUM: "Proprietário do código de API não tem permissão"**

### 🚨 **Erro Específico:**
```
O proprietário do código de API utilizado não tem permissão para fazer requisições de API
```

---

## ✅ **SOLUÇÃO COMPLETA:**

### **1. Verificar Permissões do Usuário**

#### **Passo 1: Acessar BookStack como Administrador**
- Faça login no BookStack com uma conta **administrador**
- Acesse: **Configurações** (ícone ⚙️) → **Usuários**

#### **Passo 2: Localizar o Usuário do Token**
- Encontre o usuário que criou o token de API
- Clique em **"Editar"** no usuário

#### **Passo 3: Verificar Roles (Funções)**
- Na seção **"Roles"**, verifique se o usuário tem uma role com:
  - ✅ **"API Access"** - Permissão para usar API
  - ✅ **"Content Create"** - Permissão para criar páginas
  - ✅ **"Content Edit"** - Permissão para editar páginas

### **2. Criar Role Personalizada (Se Necessário)**

#### **Passo 1: Criar Nova Role**
- Vá em: **Configurações** → **Roles** → **Criar Nova Role**
- Nome: `API User` ou `MediaWiki Integration`

#### **Passo 2: Definir Permissões**
```
✅ System Permissions:
   - API Access

✅ Content Permissions:
   - Create (criar conteúdo)
   - Edit (editar conteúdo)  
   - View (visualizar conteúdo)
```

#### **Passo 3: Atribuir Role ao Usuário**
- Volte em **Usuários** → **[Usuário do Token]** → **Editar**
- Adicione a nova role `API User`
- **Salvar**

### **3. Verificar Token de API**

#### **Passo 1: Validar Token**
- Vá em: **Configurações** → **API Tokens**
- Verifique se o token existe e não está expirado
- Anote corretamente:
  - **Token ID**: `xRG4IgbQ3yyrQI3XxDLjuuEbi5PMqF1Y`
  - **Token Secret**: `NJoVEMhCbUhP880Nc6g7ExG5gOX2nBpb`

#### **Passo 2: Testar Token (Opcional)**
- Use o botão **"🔗 Testar Conexão BookStack"** na aplicação
- Deve mostrar: ✅ **"Conectado como: [Nome do Usuário]"**

---

## 🎯 **CONFIGURAÇÃO RÁPIDA**

### **Para Administradores:**
1. **Usuário Administrador** → Já tem todas as permissões
2. **Criar token** para o admin → **Usar diretamente**

### **Para Usuários Normais:**
1. **Admin cria role** `API User` com permissões:
   - API Access ✅
   - Content Create ✅
   - Content Edit ✅
2. **Admin atribui role** ao usuário
3. **Usuário cria token** → **Pronto para usar**

---

## 📋 **CHECKLIST DE VERIFICAÇÃO**

### ✅ **Antes de Usar a API:**
- [ ] Usuário tem role com **"API Access"**
- [ ] Usuário tem role com **"Content Create"**
- [ ] Token ID e Secret estão corretos
- [ ] URL do BookStack está correta
- [ ] Token não está expirado

### ✅ **Teste de Conexão:**
- [ ] Botão "Testar Conexão" mostra sucesso
- [ ] Log mostra nome do usuário conectado
- [ ] Não há erros 403 no log

---

## 🚨 **OUTROS ERROS COMUNS:**

### **"403 Forbidden" ao Criar Páginas:**
```
Token válido mas sem permissão para criar páginas
```
**Solução:** Adicionar permissão **"Content Create"** na role do usuário

### **"Token inválido ou expirado":**
```
401 Unauthorized
```
**Solução:** Gerar novo token ou verificar Token ID/Secret

### **"Não foi possível conectar":**
```
Connection refused / Network error
```
**Solução:** Verificar URL, SSL, firewall

---

## 📖 **DOCUMENTAÇÃO OFICIAL:**

- [BookStack API Documentation](https://www.bookstackapp.com/docs/admin/api/)
- [User Roles & Permissions](https://www.bookstackapp.com/docs/admin/user-roles/)

---

## ✅ **RESULTADO ESPERADO:**

Após configurar corretamente:
```
✅ Teste de conexão BookStack: SUCESSO
   Usuário: Seu Nome
✅ Conexão com BookStack estabelecida com sucesso
✅ Páginas enviadas para BookStack com sucesso
```

🎉 **Agora você pode enviar páginas do MediaWiki para o BookStack!**
