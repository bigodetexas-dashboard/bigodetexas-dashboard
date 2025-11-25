# 🔧 Guia Rápido de Configuração - Push Notifications & OAuth

## Passo 1: Criar Webhook no Discord

### 1.1 Acesse seu Servidor Discord

1. Abra o Discord
2. Vá para o servidor BigodeTexas
3. Clique com botão direito no canal onde quer receber notificações
4. Selecione "Editar Canal"

### 1.2 Criar Webhook

1. Vá em "Integrações" → "Webhooks"
2. Clique em "Novo Webhook"
3. Dê um nome: "BigodeTexas Notifications"
4. Escolha o canal (ex: #notificacoes ou #alerts)
5. Clique em "Copiar URL do Webhook"
6. **GUARDE ESTA URL** - você vai precisar dela!

Exemplo de URL:

```
https://discord.com/api/webhooks/1234567890/AbCdEfGhIjKlMnOpQrStUvWxYz
```

---

## Passo 2: Criar Aplicação OAuth no Discord

### 2.1 Acesse o Portal de Desenvolvedores

1. Vá para: <https://discord.com/developers/applications>
2. Faça login com sua conta Discord
3. Clique em "New Application"
4. Nome: "BigodeTexas Dashboard"
5. Aceite os termos e clique em "Create"

### 2.2 Configurar OAuth2

1. No menu lateral, clique em "OAuth2" → "General"
2. **Copie o CLIENT ID** - guarde!
3. Clique em "Reset Secret" → **Copie o CLIENT SECRET** - guarde!

### 2.3 Adicionar Redirect URI

1. Ainda em OAuth2 → "General"
2. Em "Redirects", clique em "Add Redirect"
3. Cole: `http://localhost:5000/callback`
4. Clique em "Save Changes"

**Para produção**, adicione também:

```
https://seu-dominio.com/callback
```

---

## Passo 2.5: Habilitar Privileged Intents (CRÍTICO)

Para que o bot funcione corretamente e leia mensagens, você **PRECISA** ativar as permissões privilegiadas:

1. No Portal de Desenvolvedores, menu lateral, clique em **Bot**.
2. Role para baixo até a seção **Privileged Gateway Intents**.
3. Ative as seguintes opções:
    - [x] **PRESENCE INTENT**
    - [x] **SERVER MEMBERS INTENT**
    - [x] **MESSAGE CONTENT INTENT**
4. Clique em **Save Changes**.

> [!IMPORTANT]
> Se você não ativar essas opções, o bot dará erro ao iniciar: `Shard ID None is requesting privileged intents`.

---

## Passo 3: Atualizar .env

Abra o arquivo `.env` e preencha:

```env
# Discord Bot (já deve estar preenchido)
DISCORD_TOKEN=seu_token_aqui

# Push Notifications
NOTIFICATION_WEBHOOK_URL=https://discord.com/api/webhooks/SEU_WEBHOOK_AQUI

# Discord OAuth
DISCORD_CLIENT_ID=seu_client_id_aqui
DISCORD_CLIENT_SECRET=seu_client_secret_aqui
DISCORD_REDIRECT_URI=http://localhost:5000/callback
SECRET_KEY=gere_uma_chave_aleatoria_aqui

# Resto das configurações...
```

### Gerar Secret Key

Execute no terminal:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copie o resultado e cole em `SECRET_KEY`

---

## Passo 4: Testar Push Notifications

Execute:

```bash
python push_notifications.py
```

**O que deve acontecer:**

- Script envia 3 notificações de teste
- Você deve ver as mensagens no canal Discord configurado

**Se não funcionar:**

- Verifique se a URL do webhook está correta
- Verifique se o canal ainda existe
- Veja se há erros no console

---

## Passo 5: Testar OAuth

Execute:

```bash
python discord_oauth.py
```

Acesse: <http://localhost:5000>

**O que deve acontecer:**

1. Página mostra "Login com Discord"
2. Clique no link
3. Discord pede autorização
4. Após autorizar, volta para o site logado

---

## ✅ Checklist

- [ ] Webhook criado no Discord
- [ ] URL do webhook copiada
- [ ] Aplicação OAuth criada
- [ ] Client ID copiado
- [ ] Client Secret copiado
- [ ] Redirect URI configurado
- [ ] `.env` atualizado
- [ ] Secret Key gerada
- [ ] Teste de notificações executado
- [ ] Teste de OAuth executado

---

## 🆘 Problemas Comuns

**Webhook não funciona:**

- URL incorreta ou expirada
- Canal foi deletado
- Permissões insuficientes

**OAuth não funciona:**

- Client ID/Secret incorretos
- Redirect URI não configurado
- Porta 5000 já em uso

---

*Após completar todos os passos, você terá notificações push e login funcionando!*
