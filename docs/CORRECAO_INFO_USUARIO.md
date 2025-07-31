# Correção de Informações de Usuário BookStack

## Problema Identificado

O usuário relatou que nos logs aparecia "Usuário: Usuário" em vez do nome real do usuário, indicando que o sistema estava usando informações genéricas quando deveria mostrar o nome do usuário que fez login no MediaWiki.

## Melhorias Implementadas

### 1. Melhor Integração MediaWiki ↔ BookStack

**Arquivo:** `main.py` - Método `test_bookstack_connection()`
- **Funcionalidade:** Quando o BookStack não consegue fornecer o nome real do usuário, o sistema agora tenta usar o nome do usuário logado no MediaWiki
- **Lógica:** Se `user_name` está vazio ou genérico, busca `mediawiki_username` e exibe como "Nome (via MediaWiki)"

```python
# Tentar usar o nome do usuário MediaWiki se BookStack não fornecer um nome específico
if user_name in ['Usuário não identificado', 'Usuário do Token de API', 'Usuário (informações limitadas)']:
    # Obter nome do usuário logado no MediaWiki se disponível
    try:
        if hasattr(self, 'mediawiki_client') and self.mediawiki_client:
            mediawiki_username = getattr(self.mediawiki_client, 'username', None)
            if mediawiki_username:
                user_name = f"{mediawiki_username} (via MediaWiki)"
                user_note = f"Nome obtido do MediaWiki. {user_note}".strip()
    except:
        pass  # Se falhar, manter o nome original
```

### 2. Melhor Nomenclatura de Fallbacks

**Arquivo:** `src/bookstack_client.py` - Método `_get_user_info_alternative()`
- **Antes:** "Usuário (informações limitadas)"
- **Depois:** "Token de API Válido"
- **Motivo:** Mais claro e informativo sobre o status real

### 3. Logs Mais Informativos

**Arquivo:** `main.py` - Método `test_bookstack_connection()`
- **Adicionados emojis** para melhor visualização:
  - `👤 Usuário:` em vez de apenas `Usuário:`
  - `ℹ️ Info:` para informações adicionais
  - `🆔 ID:` para ID do usuário
  - `📧 Email:` para email do usuário

### 4. Metadados em Páginas Importadas

**Arquivo:** `main.py` - Método `convert_wikitext_to_html()`
- **Funcionalidade:** Páginas importadas agora incluem o nome do usuário MediaWiki nos metadados
- **Formato:** "Importado do MediaWiki em DD/MM/YYYY HH:MM | Usuário do MediaWiki: nome_usuario"

```python
# Adicionar informação do usuário se disponível
try:
    if hasattr(self, 'mediawiki_client') and self.mediawiki_client:
        mediawiki_username = getattr(self.mediawiki_client, 'username', None)
        if mediawiki_username:
            metadata_parts.append(f'Usuário do MediaWiki: {mediawiki_username}')
except:
    pass  # Se falhar, apenas continuar sem adicionar info do usuário
```

## Fluxo de Informações do Usuário

### Cenário 1: BookStack /users/me Funciona
```
BookStack API → Nome real do usuário → Exibido diretamente
```

### Cenário 2: BookStack /users/me Falha (500 Error)
```
BookStack fallback → Nome genérico → MediaWiki username → "João (via MediaWiki)"
```

### Cenário 3: Ambos Falham
```
Token válido → "Token de API Válido" (mais claro que "Usuário")
```

## Benefícios das Melhorias

1. **Clareza:** Usuário vê seu nome real em vez de "Usuário: Usuário"
2. **Rastreabilidade:** Páginas incluem quem as importou
3. **Transparência:** Logs mostram de onde veio a informação do usuário
4. **Robustez:** Sistema funciona mesmo quando BookStack tem limitações

## Como Testar

1. **Execute o teste:** 
   ```bash
   python test_user_info.py
   ```

2. **Conecte com MediaWiki** primeiro, depois teste BookStack

3. **Verifique os logs** para ver as informações melhoradas

4. **Importe uma página** e verifique os metadados no final

## Casos de Uso Resolvidos

- ✅ "Usuário: Usuário" → "👤 Usuário: João (via MediaWiki)"
- ✅ Informações genéricas → Nomes específicos quando possível
- ✅ Falta de rastreabilidade → Metadados com autor em cada página
- ✅ Logs confusos → Logs com emojis e informações claras

## Compatibilidade

- ✅ Funciona com BookStack que tem endpoint /users/me
- ✅ Funciona com BookStack que tem bug no endpoint /users/me  
- ✅ Funciona mesmo sem MediaWiki conectado
- ✅ Mantém funcionalidade existente

Esta solução garante que o usuário sempre veja informações significativas sobre quem está realizando as operações, melhorando a experiência e a confiabilidade do sistema.
