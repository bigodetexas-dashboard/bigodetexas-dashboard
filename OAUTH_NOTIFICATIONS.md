# 🔔 Push Notifications & 🔐 Discord OAuth - Guia de Configuração

## 📋 Visão Geral

Este guia explica como configurar e usar as novas funcionalidades:

- **Push Notifications** - Notificações em tempo real via Discord
- **Discord OAuth** - Autenticação segura no dashboard

---

## 🔔 Push Notifications

### Configuração

1. **Criar Webhook no Discord:**
   - Vá para as configurações do seu servidor Discord
   - Integrações → Webhooks → Novo Webhook
   - Copie a URL do webhook

2. **Configurar no `.env`:**

```env
NOTIFICATION_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

3. **Usar no código:**

```python
from push_notifications import PushNotificationManager

# Inicializar
notifier = PushNotificationManager(webhook_url=os.getenv('NOTIFICATION_WEBHOOK_URL'))

# Enviar notificação
notifier.notify_player_kill("Player1", "Player2", "M4A1", 350)
```

### Tipos de Notificações Disponíveis

- `notify_player_kill()` - Kill importante
- `notify_war_update()` - Atualização de guerra
- `notify_mission_complete()` - Missão completa
- `notify_server_restart()` - Reinício do servidor
- `notify_achievement()` - Conquista desbloqueada
- `notify_clan_war_started()` - Guerra iniciada
- `notify_leaderboard_change()` - Mudança no ranking

---

## 🔐 Discord OAuth

### Configuração

1. **Criar Aplicação no Discord:**
   - Acesse: <https://discord.com/developers/applications>
   - Crie uma nova aplicação
   - Vá em OAuth2 → General

2. **Configurar Redirects:**
   - Adicione: `http://localhost:5000/callback`
   - Para produção: `https://seu-dominio.com/callback`

3. **Copiar Credenciais:**
   - Client ID
   - Client Secret

4. **Configurar no `.env`:**

```env
DISCORD_CLIENT_ID=seu_client_id
DISCORD_CLIENT_SECRET=seu_client_secret
DISCORD_REDIRECT_URI=http://localhost:5000/callback
SECRET_KEY=uma_chave_secreta_aleatoria
```

### Usar no Dashboard

O OAuth já está integrado no `web_dashboard.py`. Rotas disponíveis:

- `/login` - Inicia login com Discord
- `/callback` - Callback do OAuth
- `/logout` - Logout
- `/api/user` - Info do usuário logado

### Proteger Rotas

```python
from discord_oauth import require_auth

@app.route('/admin')
@require_auth
def admin_page():
    return "Área administrativa"
```

### Frontend - Botão de Login

Adicione ao seu HTML:

```html
<div id="user-info">
    <a href="/login" class="btn">Login com Discord</a>
</div>

<script>
fetch('/api/user')
    .then(r => r.json())
    .then(data => {
        if (data.authenticated) {
            document.getElementById('user-info').innerHTML = `
                <img src="${data.avatar_url}" width="32" height="32">
                ${data.username}#${data.discriminator}
                <a href="/logout">Logout</a>
            `;
        }
    });
</script>
```

---

## 🧪 Testar

### Push Notifications

```bash
python push_notifications.py
```

### Discord OAuth

```bash
python discord_oauth.py
```

Acesse: <http://localhost:5000>

---

## 🔒 Segurança

### Produção

1. **Use HTTPS:**

```env
DISCORD_REDIRECT_URI=https://seu-dominio.com/callback
```

2. **Secret Key Forte:**

```python
import secrets
print(secrets.token_hex(32))
```

3. **Proteja Endpoints Sensíveis:**

```python
@app.route('/api/admin/data')
@require_auth
def admin_data():
    # Verificar se é admin
    if session['user']['id'] not in ADMIN_IDS:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(data)
```

---

## 📊 Integração com Bot

### Enviar Notificações do Bot

Adicione ao `bot_main.py`:

```python
from push_notifications import PushNotificationManager

# Inicializar
notifier = PushNotificationManager(
    webhook_url=os.getenv('NOTIFICATION_WEBHOOK_URL')
)

# Usar em eventos
@bot.event
async def on_player_kill(killer, victim, weapon, distance):
    notifier.notify_player_kill(killer, victim, weapon, distance)
```

---

## 🎯 Casos de Uso

### 1. Notificar Kills Importantes

```python
if distance > 500:  # Tiro longo
    notifier.notify_player_kill(killer, victim, weapon, distance)
```

### 2. Alertas de Guerra

```python
if war_score_updated:
    notifier.notify_war_update(clan1, clan2, score1, score2)
```

### 3. Dashboard Personalizado

```python
@app.route('/profile')
@require_auth
def my_profile():
    user_id = session['user']['id']
    # Mostrar dados específicos do usuário
    return render_template('profile.html', user_data=data)
```

---

*BigodeTexas Bot - Advanced Features! 🚀*
