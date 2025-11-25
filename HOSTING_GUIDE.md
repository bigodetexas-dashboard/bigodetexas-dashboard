# 🌐 Guia de Hospedagem Online (Render.com)

Este guia vai te ensinar a colocar seu painel online gratuitamente usando o Render.com.

## ✅ Pré-requisitos (Já realizados)

- [x] Git instalado
- [x] Repositório criado
- [x] Código preparado (`Procfile`, `requirements.txt`)

---

## 📦 Passo 1: GitHub

1. Acesse [github.com](https://github.com) e faça login.
2. Clique no **+** (canto superior direito) → **New repository**.
3. Nome do repositório: `bigodetexas-dashboard`.
4. Deixe como **Public** ou **Private** (sua escolha).
5. **NÃO** marque "Add a README file" ou .gitignore (já temos).
6. Clique em **Create repository**.

### Conectar e Enviar Código

Abra o PowerShell na pasta do bot (`d:\dayz xbox\BigodeBot`) e execute:

```powershell
& "C:\Program Files\Git\cmd\git.exe" remote add origin https://github.com/SEU_USUARIO/bigodetexas-dashboard.git
& "C:\Program Files\Git\cmd\git.exe" branch -M main
& "C:\Program Files\Git\cmd\git.exe" push -u origin main
```

*(Substitua `SEU_USUARIO` pelo seu nome de usuário do GitHub)*

---

## 🚀 Passo 2: Render.com

1. Acesse [render.com](https://render.com) e crie uma conta (pode usar o login do GitHub).
2. Clique em **New +** → **Web Service**.
3. Selecione **Build and deploy from a Git repository**.
4. Conecte sua conta do GitHub e selecione o repositório `bigodetexas-dashboard`.

### Configurações do Serviço

- **Name:** `bigodetexas-dashboard`
- **Region:** Escolha a mais próxima (ex: Ohio ou Frankfurt)
- **Branch:** `main`
- **Root Directory:** (Deixe em branco)
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn dashboard_with_oauth:app`
- **Instance Type:** `Free`

### 🔐 Variáveis de Ambiente

Role para baixo até **Environment Variables** e adicione:

| Key | Value |
|-----|-------|
| `DISCORD_CLIENT_ID` | (Seu Client ID do Discord) |
| `DISCORD_CLIENT_SECRET` | (Seu Client Secret) |
| `DISCORD_REDIRECT_URI` | `https://bigodetexas-dashboard.onrender.com/callback` |
| `SECRET_KEY` | (Sua chave secreta do .env) |

> [!IMPORTANT]
> Depois de criar o serviço, o Render vai gerar uma URL (ex: `https://bigodetexas-dashboard.onrender.com`).
> **Volte no Portal de Desenvolvedores do Discord** e adicione essa URL + `/callback` nos Redirects!

---

## ✨ Passo 3: Finalizar

Clique em **Create Web Service**. O Render vai começar a construir seu site. Acompanhe os logs. Quando aparecer "Your service is live", seu painel estará online! 🎉
