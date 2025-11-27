"""
Discord OAuth Integration for BigodeTexas Dashboard
Sistema de autenticação segura via Discord
MODO DE DESENVOLVIMENTO: Se DISCORD_CLIENT_ID estiver vazio, permite acesso sem login
"""

from flask import Flask, redirect, request, session, url_for, jsonify
import requests
import os
from functools import wraps
from datetime import datetime, timedelta, timezone

# Configurações OAuth
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID', '')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET', '')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI', 'http://localhost:3000/callback')
DISCORD_API_BASE = 'https://discord.com/api/v10'

# Modo de desenvolvimento (sem OAuth)
DEV_MODE = not DISCORD_CLIENT_ID or DISCORD_CLIENT_ID == ''

def login_required(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # MODO DE DESENVOLVIMENTO: Permite acesso sem login
        if DEV_MODE:
            if 'discord_user_id' not in session:
                session['discord_user_id'] = '123456789'
                session['discord_username'] = 'DevUser'
                session['user'] = {
                    'id': '123456789',
                    'username': 'DevUser',
                    'discriminator': '0000'
                }
            return f(*args, **kwargs)
        
        # Modo normal: verifica autenticação
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def init_oauth(app: Flask):
    """Inicializa OAuth no Flask app"""
    
    @app.route('/login')
    def login():
        # Modo de desenvolvimento
        if DEV_MODE:
            session['discord_user_id'] = '123456789'
            session['discord_username'] = 'DevUser'
            session['user'] = {
                'id': '123456789',
                'username': 'DevUser',
                'discriminator': '0000'
            }
            return redirect('/')
        
        # Modo normal: redireciona para Discord
        oauth_url = (
            f"{DISCORD_API_BASE}/oauth2/authorize?"
            f"client_id={DISCORD_CLIENT_ID}&"
            f"redirect_uri={DISCORD_REDIRECT_URI}&"
            f"response_type=code&"
            f"scope=identify%20email%20guilds"
        )
        return redirect(oauth_url)
    
    @app.route('/callback')
    def callback():
        """Callback do Discord OAuth"""
        if DEV_MODE:
            return redirect('/')
        
        code = request.args.get('code')
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        # Trocar código por token
        token_data = exchange_code(code)
        if not token_data:
            return jsonify({'error': 'Failed to get token'}), 400
        
        # Obter informações do usuário
        user_info = get_user_info(token_data['access_token'])
        if not user_info:
            return jsonify({'error': 'Failed to get user info'}), 400
        
        # Salvar na sessão
        session['user'] = {
            'id': user_info['id'],
            'username': user_info['username'],
            'discriminator': user_info.get('discriminator', '0'),
            'avatar': user_info.get('avatar'),
            'email': user_info.get('email'),
            'access_token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_at': datetime.now(timezone.utc) + timedelta(seconds=token_data['expires_in'])
        }
        session['discord_user_id'] = user_info['id']
        session['discord_username'] = user_info['username']
        
        return redirect('/')
    
    @app.route('/logout')
    def logout():
        """Logout do usuário"""
        session.clear()
        return redirect('/')

def exchange_code(code: str):
    """Troca código por access token"""
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI
    }
    
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        response = requests.post(f"{DISCORD_API_BASE}/oauth2/token", data=data, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[ERROR] OAuth exchange failed: {e}")
    
    return None

def get_user_info(access_token: str):
    """Obtém informações do usuário"""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(f"{DISCORD_API_BASE}/users/@me", headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to get user info: {e}\"")
    
    return None
