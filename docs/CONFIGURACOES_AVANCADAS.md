# Configurações Avançadas - MediaWiki to BookStack

## 🎯 Nova Funcionalidade: Janela de Configurações

Foi adicionado um novo botão **"Configurações"** na interface principal que abre uma janela dedicada para configurações avançadas do sistema.

### 📍 Localização

O botão "Configurações" está localizado na barra de botões principal, ao lado dos botões "Conectar", "Salvar Config" e "Carregar Config".

## ⚙️ Configurações Disponíveis

### 🔗 Configurações de Conexão

- **Timeout de conexão**: Define o tempo limite em segundos para operações de rede (padrão: 30s)
- **Número de tentativas**: Quantas vezes tentar reconectar em caso de falha (padrão: 3)

### 📄 Configurações de Extração

- **Tamanho do lote**: Quantas páginas processar por vez (padrão: 10)
- **Delay entre lotes**: Tempo de espera em segundos entre cada lote (padrão: 1s)
- **Limpar wikitext automaticamente**: Remove automaticamente elementos indesejados (padrão: ativado)
- **Incluir metadados**: Adiciona informações extra nas exportações (padrão: ativado)
- **Log detalhado (debug)**: Ativa logs mais verbosos para diagnóstico (padrão: desativado)

### 💾 Configurações de Cache

- **Auto-salvar cache**: Salva automaticamente o cache após atualizações (padrão: ativado)
- **Backup do cache**: Cria backup antes de atualizar o cache (padrão: desativado)

### 🎨 Configurações de Interface

- **Tema da interface**: Escolha entre Dark, Light ou System (padrão: Dark)
- **Máximo de páginas para exibir**: Limita quantas páginas mostrar na lista (padrão: 500)

## 🚀 Como Usar

1. **Abrir Configurações**: Clique no botão "Configurações" na tela principal
2. **Modificar Valores**: Ajuste as configurações conforme necessário
3. **Salvar**: Clique em "Salvar Configurações" para aplicar
4. **Restaurar Padrões**: Use "Restaurar Padrões" para voltar aos valores originais

## 💡 Funcionalidades Especiais

### 🔄 Aplicação Automática

- **Tema**: Aplicado imediatamente ao ser alterado
- **Cache e Interface**: Aplicados na próxima operação
- **Conexão**: Aplicados na próxima conexão

### 💾 Persistência

Todas as configurações são salvas automaticamente no arquivo `config/settings.json` e carregadas na próxima execução do programa.

### 🔒 Validação

O sistema valida automaticamente os valores inseridos:
- Números devem ser válidos
- Timeouts não podem ser negativos
- Lotes devem ter pelo menos 1 página

## 🎯 Benefícios

### ⚡ Performance
- **Lotes menores**: Reduzem uso de memória
- **Delays maiores**: Evitam sobrecarga no servidor
- **Cache otimizado**: Melhora velocidade de acesso

### 🛡️ Estabilidade
- **Timeouts adequados**: Evitam travamentos
- **Tentativas múltiplas**: Recuperação automática de falhas
- **Logs detalhados**: Facilitam diagnóstico

### 👥 Usabilidade
- **Temas**: Personalização visual
- **Limites de exibição**: Interface mais responsiva
- **Metadados**: Informações mais completas

## 🔧 Configurações Recomendadas

### 🏢 Para Wikis Corporativas (Servidores Lentos)
```
- Timeout: 60 segundos
- Tentativas: 5
- Lote: 5 páginas
- Delay: 3 segundos
```

### 🌐 Para Wikis Públicas (Servidores Rápidos)
```
- Timeout: 15 segundos
- Tentativas: 3
- Lote: 20 páginas
- Delay: 0.5 segundos
```

### 🔍 Para Debugging/Diagnóstico
```
- Log detalhado: Ativado
- Backup cache: Ativado
- Metadados: Ativado
- Lote: 1 página (para teste)
```

## 📝 Notas Importantes

⚠️ **Atenção**: 
- Valores muito baixos de timeout podem causar falhas
- Lotes muito grandes podem sobrecarregar a memória
- Delays muito pequenos podem ser bloqueados pelo servidor

✅ **Recomendação**: 
- Teste com configurações conservadoras primeiro
- Aumente gradualmente conforme necessário
- Use logs detalhados para identificar problemas

---

*Documentação gerada para o MediaWiki to BookStack Exporter v2.0*
