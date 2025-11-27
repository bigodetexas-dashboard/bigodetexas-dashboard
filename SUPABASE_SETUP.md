# 🗄️ Guia: Configurar PostgreSQL com Supabase (GRATUITO)

## Por que Supabase?

- ✅ **500MB gratuito** (suficiente para milhares de jogadores)
- ✅ **PostgreSQL real** (compatível com nosso código)
- ✅ **Dashboard visual** para ver os dados
- ✅ **Sempre online** (não dorme)

---

## Passo 1: Criar Conta no Supabase

1. Acesse: <https://supabase.com>
2. Clique em **"Start your project"**
3. Faça login com **GitHub** (mais rápido)

---

## Passo 2: Criar Projeto

1. Clique em **"New Project"**
2. Preencha:
   - **Name:** `bigodetexas`
   - **Database Password:** (crie uma senha forte e **GUARDE!**)
   - **Region:** `West US (Oregon)` (mesma do Render)
   - **Pricing Plan:** **Free** (já selecionado)
3. Clique em **"Create new project"**

Aguarde ~2 minutos para o projeto ser criado.

---

## Passo 3: Copiar URL de Conexão

1. No menu lateral, clique em **"Project Settings"** (ícone de engrenagem)
2. Clique em **"Database"**
3. Role até **"Connection string"**
4. Selecione **"URI"** (não Session mode)
5. Clique em **"Copy"**

A URL terá este formato:

```
postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
```

⚠️ **Importante:** Substitua `[YOUR-PASSWORD]` pela senha que você criou no Passo 2!

---

## Passo 4: Adicionar DATABASE_URL ao Render

1. Acesse: <https://dashboard.render.com/web/srv-d4j3nh6uk2gs73bc1q20>
2. No menu lateral, clique em **"Environment"**
3. Clique em **"Add Environment Variable"**
4. Preencha:
   - **Key:** `DATABASE_URL`
   - **Value:** (cole a URL do Supabase com a senha substituída)
5. Clique em **"Save Changes"**

O Render vai fazer um **redeploy automático** (~2 minutos).

---

## Passo 5: Criar Tabelas no Supabase

Volte ao Supabase e:

1. No menu lateral, clique em **"SQL Editor"**
2. Clique em **"New query"**
3. Cole este SQL:

```sql
-- Tabela de jogadores
CREATE TABLE IF NOT EXISTS players (
    gamertag VARCHAR(255) PRIMARY KEY,
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    best_killstreak INTEGER DEFAULT 0,
    longest_shot INTEGER DEFAULT 0,
    weapons_stats JSONB DEFAULT '{}',
    first_seen BIGINT,
    last_seen BIGINT
);

-- Tabela de economia
CREATE TABLE IF NOT EXISTS economy (
    discord_id VARCHAR(255) PRIMARY KEY,
    gamertag VARCHAR(255),
    balance INTEGER DEFAULT 0,
    last_daily TIMESTAMP,
    inventory JSONB DEFAULT '{}',
    transactions JSONB DEFAULT '[]',
    favorites JSONB DEFAULT '[]',
    achievements JSONB DEFAULT '{}'
);

-- Tabela de clãs
CREATE TABLE IF NOT EXISTS clans (
    clan_name VARCHAR(255) PRIMARY KEY,
    leader VARCHAR(255),
    members JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    total_kills INTEGER DEFAULT 0,
    total_deaths INTEGER DEFAULT 0
);

-- Tabela de links Discord-Gamertag
CREATE TABLE IF NOT EXISTS links (
    discord_id VARCHAR(255) PRIMARY KEY,
    gamertag VARCHAR(255) UNIQUE,
    linked_at TIMESTAMP DEFAULT NOW()
);
```

4. Clique em **"Run"** (ou pressione Ctrl+Enter)
5. Deve aparecer "Success. No rows returned"

---

## Passo 6: Adicionar DATABASE_URL ao .env Local

Para o bot local funcionar, adicione ao arquivo `.env`:

```env
DATABASE_URL=postgresql://postgres:SUA_SENHA@db.xxx.supabase.co:5432/postgres
```

(Use a mesma URL do Passo 3)

---

## Passo 7: Migrar Dados

Execute no seu PC:

```powershell
python migrate_to_postgres.py
```

Isso vai migrar todos os dados dos JSONs para o Supabase!

---

## ✅ Verificação

1. No Supabase, vá em **"Table Editor"**
2. Você deve ver as 4 tabelas: `players`, `economy`, `clans`, `links`
3. Clique em cada uma para ver os dados migrados

No painel web:

1. Acesse: <https://bigodetexas-dashboard.onrender.com/leaderboard>
2. Deve mostrar dados em tempo real!

---

## 🎉 Pronto

Agora você tem:

- ✅ PostgreSQL gratuito (500MB)
- ✅ Dados sincronizados em tempo real
- ✅ Bot e painel compartilhando mesmos dados
- ✅ Dashboard visual no Supabase

---

## 💡 Dicas

**Ver dados no Supabase:**

- Menu lateral → **"Table Editor"**
- Clique em qualquer tabela para ver/editar dados

**Monitorar uso:**

- Menu lateral → **"Project Settings"** → **"Usage"**
- Veja quanto espaço está usando (limite: 500MB)

**Backup automático:**

- Supabase faz backup automático diário
- Seus JSONs locais continuam como backup extra
