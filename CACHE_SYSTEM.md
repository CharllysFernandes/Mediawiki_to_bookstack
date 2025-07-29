# Sistema de Cache de Páginas - MediaWiki to BookStack

## 🚀 Nova Funcionalidade: Cache Inteligente de Páginas

Para resolver o problema de demora ao carregar mais de 7 mil páginas, implementamos um sistema de cache que:

### ✨ Benefícios

- **Performance**: Carregamento instantâneo de páginas já conhecidas
- **Controle de Progresso**: Rastreamento do status de cada página
- **Retomada de Trabalho**: Continue de onde parou
- **Eficiência**: Processa apenas páginas pendentes

### 📁 Arquivos Criados

- `src/pages_cache.py` - Classe principal do sistema de cache
- `config/pages_cache.json` - Arquivo de cache (ignorado pelo Git)
- `config/.gitignore` - Atualizado para incluir o cache

### 🎯 Como Usar

#### 1. **Primeira Vez - Criar Cache Inicial**
   - Conecte-se à wiki
   - Clique em **"Atualizar da API"** para buscar todas as páginas
   - Aguarde o carregamento completo (só precisa fazer uma vez)
   - O cache será salvo automaticamente

#### 2. **Carregamento Rápido**
   - Clique em **"Carregar Cache"** para carregamento instantâneo
   - Clique em **"Mostrar Páginas"** para ver páginas pendentes

#### 3. **Extração Inteligente**
   - Selecione páginas pendentes
   - Clique em **"Extrair Pendentes"**
   - Páginas processadas são marcadas automaticamente
   - Continue de onde parou a qualquer momento

#### 4. **Gerenciamento**
   - **"Reset Status"**: Marca todas as páginas como pendentes novamente
   - **"Atualizar da API"**: Sincroniza com mudanças na wiki (preserva status)

### 📊 Estrutura do JSON

```json
{
  "pageid": 123,
  "title": "Nome da Página", 
  "link": "index.php?curid=123",
  "status": 0,  // 0 = pendente, 1 = processada
  "last_processed": "2025-07-29T12:00:00",
  "error_message": null
}
```

### 🎮 Interface Atualizada

**Novos Botões:**
- **Carregar Cache**: Carrega páginas do cache local (rápido)
- **Atualizar da API**: Busca páginas da wiki e atualiza cache
- **Mostrar Páginas**: Exibe páginas pendentes para seleção
- **Extrair Pendentes**: Processa apenas páginas selecionadas
- **Reset Status**: Reinicia status de todas as páginas

### ⚡ Workflow Recomendado

1. **Setup Inicial** (uma vez):
   ```
   Conectar → Atualizar da API → Aguardar conclusão
   ```

2. **Uso Diário**:
   ```
   Conectar → Carregar Cache → Mostrar Páginas → Selecionar → Extrair Pendentes
   ```

3. **Para Continuar Trabalho**:
   ```
   Conectar → Carregar Cache → Extrair Pendentes
   ```

### 🔧 Funcionalidades Técnicas

- **Preservação de Status**: Ao atualizar da API, mantém páginas já processadas
- **Detecção de Páginas Removidas**: Remove do cache páginas que não existem mais
- **Busca Rápida**: Método para buscar páginas por título
- **Estatísticas em Tempo Real**: Progresso, pendentes, processadas
- **Tratamento de Erros**: Salva erros específicos por página

### 🎯 Para Wikis Grandes (7000+ páginas)

1. **Primeira execução**: ~5-10 minutos para criar cache
2. **Execuções seguintes**: ~5 segundos para carregar cache
3. **Extração**: Apenas páginas selecionadas, não todas
4. **Progresso**: Continue de onde parou, mesmo dias depois

### 🛡️ Segurança

- Cache é ignorado pelo Git (`.gitignore`)
- Não contém credenciais, apenas metadados públicos das páginas
- Pode ser deletado e recriado a qualquer momento

---

**🎉 Resultado**: De 7+ minutos para carregar páginas → 5 segundos!**
