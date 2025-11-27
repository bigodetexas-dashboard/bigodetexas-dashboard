# 🗄️ Guia: Configurar PostgreSQL no Render

## Passo 1: Criar Database PostgreSQL

1. Acesse: <https://dashboard.render.com>
2. Clique em **"New +"** → **"PostgreSQL"**
3. Preencha:
   - **Name:** `bigodetexas-db`
   - **Database:** `bigodetexas`
   - **User:** `bigodetexas_user` (ou deixe o padrão)
   - **Region:** `Ohio (US East)` (mesma do Web Service)
   - **PostgreSQL Version:** `16` (ou mais recente)
   - **Instance Type:** **Free**
4. Clique em **"Create Database"**

Aguarde ~2 minutos para o database ser criado.

---

## Passo 2: Copiar URL de Conexão

1. Após criado, clique no database **"bigodetexas-db"**
2. Na página do database, procure por **"Internal Database URL"**
3. Clique em **"Copy"** para copiar a URL completa

A URL terá este formato:

```
postgres://usuario:senha@host/database
```

---

## Passo 3: Adicionar DATABASE_URL ao Web Service

1. Volte para: <https://dashboard.render.com/web/srv-d4j3nh6uk2gs73bc1q20>
2. No menu lateral, clique em **"Environment"**
3. Clique em **"Add Environment Variable"**
4. Preencha:
   - **Key:** `DATABASE_URL`
   - **Value:** (cole a URL que você copiou no Passo 2)
5. Clique em **"Save Changes"**

O Render vai fazer um **redeploy automático** (~2 minutos).

---

## Passo 4: Inicializar Tabelas

Depois que o redeploy terminar, você precisa criar as tabelas no banco.

**Opção A: Via Script Python (Recomendado)**

Execute no seu PC:

```powershell
python -c "import database; database.init_database()"
```

**Opção B: Manualmente no Render**

1. No painel do database, clique em **"Connect"** → **"External Connection"**
2. Use um cliente SQL (como DBeaver ou pgAdmin)
3. Execute o script SQL que está em `database.py` (função `init_database`)

---

## Passo 5: Migrar Dados JSON → PostgreSQL

Execute no seu PC para migrar os dados existentes:

```powershell
python migrate_to_postgres.py
```

(Vou criar esse script agora)

---

## ✅ Verificação

Depois de tudo configurado, teste:

1. Acesse: <https://bigodetexas-dashboard.onrender.com/leaderboard>
2. Deve mostrar dados em tempo real do PostgreSQL
3. No Discord, use `!link SeuGamertag`
4. Verifique se aparece no painel imediatamente

---

## 🔧 Troubleshooting

**Erro: "could not connect to server"**

- Verifique se a `DATABASE_URL` está correta
- Certifique-se de usar a **Internal Database URL** (não a External)

**Tabelas não foram criadas:**

- Execute `python -c "import database; database.init_database()"`
- Verifique os logs do Render

**Dados não aparecem:**

- Execute o script de migração
- Verifique se o bot está usando `database.py` em vez de JSON
