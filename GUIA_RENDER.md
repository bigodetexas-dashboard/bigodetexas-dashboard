# 🎯 Guia Passo-a-Passo: Corrigindo Deploy no Render

## Passo 1: Acessar o Dashboard do Render

1. Abra seu navegador
2. Acesse: **<https://dashboard.render.com>**
3. Faça login com suas credenciais

## Passo 2: Localizar o Serviço

1. Na página inicial, procure pelo serviço: **`bigodetexas-dashboard`**
2. Clique no nome do serviço para abrir os detalhes

## Passo 3: Verificar Status do Último Deploy

1. Na página do serviço, procure pela aba **"Events"** ou **"Deploys"**
2. Verifique o status do último deploy (commit `84b21a3`)
3. **Anote aqui o status**: ________________

### Possíveis Status

- ✅ **Live**: Deploy bem-sucedido (mas template não atualizou)
- ⏳ **Building**: Ainda está fazendo deploy
- ❌ **Failed**: Deploy falhou (veja os logs de erro)

## Passo 4: Limpar Build Cache

1. Clique na aba **"Settings"** (Configurações)
2. Role a página até encontrar a seção de **Build & Deploy**
3. Procure pelo botão **"Clear Build Cache"** ou **"Invalidate Cache"**
4. Clique no botão
5. Confirme a ação quando solicitado

## Passo 5: Forçar Redeploy Manual

### Opção A: Deploy do Último Commit

1. Volte para a aba principal do serviço
2. Procure pelo botão **"Manual Deploy"** no canto superior direito
3. Clique em **"Deploy latest commit"**
4. Aguarde o processo de build (2-5 minutos)

### Opção B: Redeploy com Clear Cache

1. Se houver opção **"Clear build cache & deploy"**, use esta
2. Isso fará ambas as ações de uma vez

## Passo 6: Monitorar o Deploy

1. Enquanto o deploy está acontecendo, clique em **"View Logs"**
2. Observe os logs em tempo real
3. Procure por mensagens de erro (linhas em vermelho)
4. **Anote qualquer erro que aparecer**: ________________

### O que procurar nos logs

- ✅ `Installing dependencies...`
- ✅ `Building...`
- ✅ `Deploy successful`
- ❌ Qualquer linha com `ERROR` ou `FAILED`

## Passo 7: Aguardar Conclusão

1. Aguarde até ver a mensagem **"Deploy successful"** ou **"Live"**
2. Isso pode levar de 2 a 5 minutos
3. **NÃO** feche a janela durante o processo

## Passo 8: Verificar se Funcionou

Após o deploy completar, vamos testar:

1. Abra uma **nova aba anônima** (Ctrl + Shift + N no Chrome)
2. Acesse: **<https://bigodetexas-dashboard.onrender.com/loja>**
3. Aguarde a página carregar
4. Verifique se os itens da loja aparecem (não deve ficar em "Carregando...")

### Se os itens aparecerem: ✅ SUCESSO

### Se ainda mostrar "Carregando...": Continue para o Passo 9

## Passo 9: Verificação Adicional (se necessário)

Se ainda não funcionar, vamos verificar as variáveis de ambiente:

1. No dashboard do Render, vá em **"Environment"**
2. Procure por estas variáveis:
   - `FLASK_ENV`
   - `FLASK_CACHING`
   - `TEMPLATES_AUTO_RELOAD`

3. **Anote os valores**: ________________

## Passo 10: Restart do Serviço

Como último recurso:

1. Vá em **"Settings"**
2. Role até o final da página
3. Procure por **"Restart Service"** ou **"Suspend Service"**
4. Clique em **"Restart Service"**
5. Aguarde o serviço reiniciar (1-2 minutos)

---

## 📝 Checklist de Ações

- [ ] Acessei o dashboard do Render
- [ ] Localizei o serviço `bigodetexas-dashboard`
- [ ] Verifiquei o status do último deploy
- [ ] Limpei o build cache
- [ ] Forcei um redeploy manual
- [ ] Monitorei os logs (sem erros)
- [ ] Aguardei deploy completar
- [ ] Testei em aba anônima
- [ ] ✅ Loja funcionando!

---

## 🆘 Se Precisar de Ajuda

**Me avise em qual passo você está e o que está vendo na tela!**

Exemplos:

- "Estou no Passo 3, o status mostra 'Failed'"
- "Estou no Passo 6, vejo um erro nos logs: [copie o erro aqui]"
- "Completei todos os passos mas ainda não funciona"
