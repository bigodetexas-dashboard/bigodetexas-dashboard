# Variáveis de Ambiente - BigodeTexas Dashboard

## ⚠️ CONFIDENCIAL - NÃO COMPARTILHAR

Estas são as variáveis de ambiente necessárias para o serviço no Render:

```env
# Discord Bot
DISCORD_TOKEN=REDACTED_FOR_SECURITY
DISCORD_CLIENT_ID=REDACTED_FOR_SECURITY
DISCORD_CLIENT_SECRET=REDACTED_FOR_SECURITY
DISCORD_REDIRECT_URI=https://bigodetexas-dashboard.onrender.com/callback

# Database (Supabase)
DATABASE_URL=REDACTED_FOR_SECURITY

# FTP (Nitrado)
FTP_HOST=brsp012.gamedata.io
FTP_USER=REDACTED_FOR_SECURITY
FTP_PASS=REDACTED_FOR_SECURITY

# Nitrado API
NITRADO_TOKEN=REDACTED_FOR_SECURITY
SERVICE_ID=3622181

# Security
SECRET_KEY=REDACTED_FOR_SECURITY
ADMIN_PASSWORD=REDACTED_FOR_SECURITY
```

## 📋 Checklist para Novo Serviço

Ao criar um novo serviço no Render, adicione TODAS estas variáveis na seção "Environment Variables".

### Variáveis Obrigatórias (serviço não funciona sem)

- ✅ `DISCORD_TOKEN`
- ✅ `DATABASE_URL`
- ✅ `SECRET_KEY`
- ✅ `DISCORD_CLIENT_ID`
- ✅ `DISCORD_CLIENT_SECRET`
- ✅ `DISCORD_REDIRECT_URI`

### Variáveis Opcionais (funcionalidades específicas)

- `FTP_HOST`, `FTP_USER`, `FTP_PASS` (para upload de arquivos no servidor)
- `NITRADO_TOKEN`, `SERVICE_ID` (para API do Nitrado)
- `ADMIN_PASSWORD` (para acesso admin)

## 🔄 Como Usar ao Recriar Serviço

1. No Render, ao criar novo serviço, vá em "Environment Variables"
2. Clique em "Add Environment Variable"
3. Copie e cole cada par Key/Value desta lista
4. Salve e crie o serviço

---

**Data de backup:** 2025-11-26
**Serviço:** bigodetexas-dashboard
**Plataforma:** Render.com
