"""
Discord OAuth Integration for BigodeTexas Dashboard
Sistema de autenticação segura via Discord
"""

from flask import Flask, redirect, request, session, url_for, jsonify
import requests
import os
from functools import wraps
from datetime import datetime, timedelta

# Configurações OAuth
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', '')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:5000/callback')
DISCORD_API_BASE = 'https://discord.com/api/v10'

class DiscordOAuth:
    """Gerenciador de autenticação Discord OAuth"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
        
        # Configurar rotas
        self.setup_routes()
    
    def setup_routes(self):
        """Configura rotas de autenticação"""
        
        @self.app.route('/login')
        def login():
            """Redireciona para Discord OAuth"""
            oauth_url = (
                f"{DISCORD_API_BASE}/oauth2/authorize?"
                f"client_id={DISCORD_CLIENT_ID}&"
                f"redirect_uri={DISCORD_REDIRECT_URI}&"
                f"response_type=code&"
                f"scope=identify%20email%20guilds"
            )
            return redirect(oauth_url)
        
        @self.app.route('/callback')
        def callback():
            """Callback do Discord OAuth"""
            code = request.args.get('code')
            
            if not code:
                return jsonify({'error': 'No code provided'}), 400
            
            # Trocar código por token
            token_data = self.exchange_code(code)
            
            if not token_data:
                return jsonify({'error': 'Failed to get token'}), 400
            
            # Obter informações do usuário
            user_info = self.get_user_info(token_data['access_token'])
            
            if not user_info:
                return jsonify({'error': 'Failed to get user info'}), 400
            
            # Salvar na sessão
            session['user'] = {
                'id': user_info['id'],
                'username': user_info['username'],
                'discriminator': user_info['discriminator'],
                'avatar': user_info['avatar'],
                'email': user_info.get('email'),
                'access_token': token_data['access_token'],
                'refresh_token': token_data['refresh_token'],
                'expires_at': datetime.now() + timedelta(seconds=token_data['expires_in'])
            }
            
            return redirect('/')
        
        @self.app.route('/logout')
        def logout():
            """Logout do usuário"""
            session.pop('user', None)
            return redirect('/')
        
        @self.app.route('/api/user')
        def api_user():
            """Retorna informações do usuário logado"""
            if 'user' not in session:
                return jsonify({'authenticated': False}), 401
            
            user = session['user']
            return jsonify({
                'authenticated': True,
                'id': user['id'],
                'username': user['username'],
                'discriminator': user['discriminator'],
                'avatar_url': self.get_avatar_url(user['id'], user['avatar'])
            })
    
    def exchange_code(self, code: str):
        """Troca código por access token"""
        data = {
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': DISCORD_REDIRECT_URI
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(
                f"{DISCORD_API_BASE}/oauth2/token",
                data=data,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[ERROR] OAuth exchange failed: {e}")
        
        return None
    
    def get_user_info(self, access_token: str):
        """Obtém informações do usuário"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        try:
            response = requests.get(
                f"{DISCORD_API_BASE}/users/@me",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get user info: {e}")
        
        return None
    
    def get_avatar_url(self, user_id: str, avatar_hash: str):
        """Gera URL do avatar do usuário"""
        if not avatar_hash:
            return f"https://cdn.discordapp.com/embed/avatars/{int(user_id) % 5}.png"
        
        return f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.png"
    
    def refresh_token(self, refresh_token: str):
        """Atualiza access token"""
        data = {
            'client_id': DISCORD_CLIENT_ID,
            'client_secret': DISCORD_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        try:
            response = requests.post(
                f"{DISCORD_API_BASE}/oauth2/token",
                data=data
            )
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"[ERROR] Token refresh failed: {e}")
        
        return None

def require_auth(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        
        # Verificar se token expirou
        if datetime.now() >= session['user']['expires_at']:
            # Tentar renovar
            new_token = oauth.refresh_token(session['user']['refresh_token'])
            if new_token:
                session['user']['access_token'] = new_token['access_token']
                session['user']['expires_at'] = datetime.now() + timedelta(seconds=new_token['expires_in'])
            else:
                session.pop('user', None)
                return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

# Exemplo de uso
login_required = require_auth
# Exemplo de uso removido. Agora o módulo pode ser importado.

def init_oauth(app: Flask):
    """Inicializa o OAuth no app Flask passado.
    Cria a instância DiscordOAuth e a armazena em módulo para uso posterior.
    """
    global oauth
    oauth = DiscordOAuth(app)
    return oauth

# Se o módulo for executado diretamente (para testes rápidos),
# podemos iniciar um app de demonstração.
if __name__ == "__main__":
    demo_app = Flask(__name__)
    demo_app.secret_key = os.getenv('SECRET_KEY', 'demo-secret')
    init_oauth(demo_app)
    @demo_app.route('/')
    def index():
        if 'user' in session:
            return f"Olá, {session['user']['username']}! <a href='/logout'>Logout</a>"
        return "<a href='/login'>Login com Discord</a>"
    demo_app.run(debug=True, port=5000)
