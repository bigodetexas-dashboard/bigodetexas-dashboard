# 🤠 BigodeTexas Bot

Sistema completo de gerenciamento para servidor DayZ Xbox com Discord Bot e Dashboard Web.

## 📋 Características

- 🤖 **Bot Discord** com economia, clãs, missões e muito mais
- 🌐 **Dashboard Web** premium com design moderno
- 📊 **Gráficos Interativos** para análise de dados
- 👤 **Perfis de Jogador** individualizados
- ⚔️ **Sistema de Guerras** entre clãs
- 🗺️ **Heatmap de PvP** visual
- 🎯 **Missões Diárias** com recompensas
- 📈 **Analytics** e exportação de dados

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.10+
- Conta Discord Bot
- Servidor Nitrado (DayZ Xbox)
- Acesso FTP ao servidor

### Instalação

1. Clone o repositório
2. Instale as dependências:

```bash
pip install discord.py aiohttp ftplib flask matplotlib pillow chart.js
```

3. Configure o arquivo `.env`:

```env
DISCORD_TOKEN=seu_token_aqui
FTP_HOST=seu_host_ftp
FTP_USER=seu_usuario
FTP_PASS=sua_senha
NITRADO_TOKEN=seu_token_nitrado
```

4. Inicie o bot:

```bash
run_bot.bat
```

5. Inicie o dashboard:

```bash
run_dashboard.bat
```

## 📖 Comandos do Bot

### Economia

- `!saldo` - Ver seu saldo
- `!comprar <código>` - Comprar item
- `!loja` - Ver catálogo
- `!transferir <@user> <valor>` - Transferir coins

### Clãs

- `!clan criar <tag> <nome>` - Criar clã
- `!clan entrar <tag>` - Entrar em clã
- `!clan info` - Informações do clã
- `!guerra declarar <tag>` - Declarar guerra
- `!guerra aceitar <tag>` - Aceitar guerra
- `!guerra status` - Ver guerras ativas

### Missões e Reputação

- `!missoes` - Ver missões diárias
- `!reputacao [@user]` - Ver reputação

### Mapas e Stats

- `!mapadecalor` - Gerar heatmap de PvP
- `!stats [@user]` - Ver estatísticas

### Admin

- `!restart` - Reiniciar servidor
- `!gameplay edit` - Editar configurações
- `!ban <player>` - Banir jogador

## 🌐 Dashboard Web

Acesse: `http://localhost:5000`

### Páginas Disponíveis

- **Início** - Overview geral
- **Estatísticas** - Gráficos e métricas
- **Rankings** - Top players
- **Loja** - Catálogo de itens
- **Heatmap** - Mapa de calor PvP
- **Perfil** - Perfil individual (clique no nome)

### API Endpoints

- `GET /api/stats` - Estatísticas gerais
- `GET /api/players` - Lista de jogadores
- `GET /api/leaderboard` - Rankings
- `GET /api/player/<name>` - Perfil do jogador
- `GET /api/export/players` - Exportar jogadores (JSON)
- `GET /api/export/report` - Relatório completo

## 📁 Estrutura do Projeto

```
BigodeBot/
├── bot_main.py              # Bot Discord principal
├── web_dashboard.py         # Dashboard Flask
├── analytics.py             # Analytics e exports
├── generate_heatmap.py      # Gerador de heatmap
├── security.py              # Segurança e rate limiting
├── killfeed.py              # Parser de killfeed
├── missions.json            # Configuração de missões
├── templates/               # Templates HTML
│   ├── index.html
│   ├── stats.html
│   ├── leaderboard.html
│   ├── shop.html
│   ├── heatmap.html
│   └── profile.html
└── static/                  # Assets estáticos
    ├── css/style.css
    └── js/
        ├── main.js
        └── charts.js
```

## 🎨 Tecnologias Utilizadas

- **Backend:** Python, Flask, Discord.py
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Gráficos:** Chart.js
- **Banco de Dados:** JSON files
- **APIs:** Nitrado API, Discord API
- **Protocolos:** FTP

## 🔒 Segurança

- Rate limiting em comandos
- Validação de inputs
- Whitelist de admins
- Logs de ações administrativas
- Backups automáticos

## 🚀 Deploy to Render.com

1. **Create a GitHub repository** (if you haven't already) and push the project:

   ```bash
   git init
   git add .
   git commit -m "Initial commit with OAuth dashboard"
   git branch -M main
   git remote add origin <YOUR_GITHUB_REPO_URL>
   git push -u origin main
   ```

2. **Create a Render.com account** and click **New Web Service**.
3. **Connect** the service to your GitHub repository.
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `python dashboard_with_oauth.py`
6. **Add Environment Variables** (Settings → Environment):
   - `DISCORD_CLIENT_ID`
   - `DISCORD_CLIENT_SECRET`
   - `DISCORD_REDIRECT_URI` (e.g., `https://<your-app>.onrender.com/callback`)
   - `SECRET_KEY`
   - `NOTIFICATION_WEBHOOK_URL`
7. Click **Create Web Service** – Render will build and deploy automatically.

After deployment, open the provided URL, test the Discord login flow, and verify that all pages and API endpoints work.

## 📊 Analytics

Execute `analytics.py` para:

- Exportar dados em CSV
- Gerar relatórios semanais
- Análise de estatísticas

```bash
python analytics.py
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é privado e proprietário.

## 👥 Autor

Desenvolvido para BigodeTexas Server

## 🆘 Suporte

Para suporte, entre em contato via Discord.

---

**BigodeTexas** - O melhor servidor DayZ Xbox! 🤠
