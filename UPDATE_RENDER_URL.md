# Atualizar DATABASE_URL no Render

## Passo 1: Acessar Environment Variables

1. Acesse: <https://dashboard.render.com/web/srv-d4j3nh6uk2gs73bc1q20>
2. Menu lateral → **"Environment"**

## Passo 2: Atualizar DATABASE_URL

Procure pela variável `DATABASE_URL` e **SUBSTITUA** o valor por:

```
postgresql://postgres:Lissy%402000@db.uvyhpedcgmroddvkngdl.supabase.co:5432/postgres
```

## Passo 3: Salvar

Clique em **"Save Changes"**

O Render vai fazer redeploy automático (~2 minutos).

## Passo 4: Verificar Logs

Depois do redeploy, vá em:

- Menu lateral → **"Logs"**
- Procure por erros de conexão com o banco

Se não houver erros, significa que o Render conseguiu conectar ao Supabase!
