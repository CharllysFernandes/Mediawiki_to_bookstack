📚 Guia Rápido - Configuração BookStack
=========================================

🔧 CORREÇÕES APLICADAS:
- ✅ Erro "unexpected keyword argument 'count'" corrigido
- ✅ Erro "no attribute 'after'" corrigido  
- ✅ Janela de configurações ajustada para 600x800px
- ✅ Frame scrollable implementado para visualizar todas as opções

🚀 COMO TESTAR AS CONFIGURAÇÕES BOOKSTACK:

1. ABRIR CONFIGURAÇÕES:
   - Execute: python main.py
   - Clique no ícone de engrenagem (⚙️) "Configurações"
   - A janela de configurações deve abrir com altura maior (800px)

2. LOCALIZAR SEÇÃO BOOKSTACK:
   - Role para baixo na janela de configurações
   - Procure pela seção "📚 Configurações BookStack"
   - Deve estar entre "Cache" e "Interface"

3. PREENCHER CAMPOS:
   - URL Base: https://sua-instancia.bookstack.com
   - Token ID: (obtenha no BookStack > Configurações > API Tokens)
   - Token Secret: (será mascarado com asteriscos)
   - ☑️ Verificar SSL (marque para produção)

4. TESTAR CONEXÃO:
   - Clique em "🔗 Testar Conexão BookStack"
   - Aguarde o resultado:
     * ✅ Verde = Sucesso
     * ❌ Vermelho = Erro (verifique credenciais)

5. SALVAR:
   - Clique em "Salvar Configurações"
   - As configurações ficam em config/settings.json

🧪 TESTES ALTERNATIVOS:

1. TESTE ISOLADO:
   python test_bookstack_config.py
   (Interface só com BookStack)

2. DEMONSTRAÇÃO:
   python demo_bookstack.py
   (Após configurar credenciais)

🔍 VERIFICAÇÃO RÁPIDA:
- Se não vê a seção BookStack: janela pode estar pequena
- Use scroll ou redimensione a janela
- Todos os erros anteriores foram corrigidos

✅ STATUS: PRONTO PARA USO!
