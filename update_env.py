"""
Script para atualizar o arquivo .env automaticamente
"""

import os
import shutil
from datetime import datetime

def update_env_file():
    """Atualiza o arquivo .env com as novas configurações OAuth"""
    
    # Fazer backup do .env atual
    if os.path.exists('.env'):
        backup_name = f'.env.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        shutil.copy('.env', backup_name)
        print(f"[OK] Backup criado: {backup_name}")
    
    # Ler o .env atual para preservar valores existentes
    existing_values = {}
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing_values[key.strip()] = value.strip()
    
    # Configurações OAuth (já configuradas)
    oauth_config = {
        'DISCORD_CLIENT_ID': '1442959269141020892',
        'DISCORD_CLIENT_SECRET': 'iw9RzpjUTvU5R0_cmzBiVzYPnldCNOJS',
        'DISCORD_REDIRECT_URI': 'http://localhost:5000/callback',
        'SECRET_KEY': '4ba0cf9c9cbfe18a82202b546f497c7d4d449d6e73b3fdf45503ebb8d1d5547e'
    }
    
    # Mesclar com valores existentes (OAuth sobrescreve)
    final_config = {**existing_values, **oauth_config}
    
    # Escrever novo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write("# BigodeTexas Bot - Environment Configuration\n")
        f.write(f"# Atualizado automaticamente em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Discord Bot
        f.write("# ===== DISCORD BOT =====\n")
        f.write(f"DISCORD_TOKEN={final_config.get('DISCORD_TOKEN', 'seu_token_do_bot_aqui')}\n")
        f.write(f"ADMIN_PASSWORD={final_config.get('ADMIN_PASSWORD', 'sua_senha_admin_segura')}\n\n")
        
        # Discord OAuth
        f.write("# ===== DISCORD OAUTH (Dashboard) =====\n")
        f.write(f"DISCORD_CLIENT_ID={oauth_config['DISCORD_CLIENT_ID']}\n")
        f.write(f"DISCORD_CLIENT_SECRET={oauth_config['DISCORD_CLIENT_SECRET']}\n")
        f.write(f"DISCORD_REDIRECT_URI={oauth_config['DISCORD_REDIRECT_URI']}\n")
        f.write(f"SECRET_KEY={oauth_config['SECRET_KEY']}\n\n")
        
        # Push Notifications
        f.write("# ===== PUSH NOTIFICATIONS =====\n")
        f.write(f"NOTIFICATION_WEBHOOK_URL={final_config.get('NOTIFICATION_WEBHOOK_URL', 'seu_webhook_url_aqui')}\n\n")
        
        # FTP Nitrado
        f.write("# ===== FTP NITRADO =====\n")
        f.write(f"FTP_HOST={final_config.get('FTP_HOST', 'seu_host.nitrado.net')}\n")
        f.write(f"FTP_PORT={final_config.get('FTP_PORT', '21')}\n")
        f.write(f"FTP_USER={final_config.get('FTP_USER', 'seu_usuario_ftp')}\n")
        f.write(f"FTP_PASS={final_config.get('FTP_PASS', 'sua_senha_ftp')}\n\n")
        
        # Nitrado API
        f.write("# ===== NITRADO API =====\n")
        f.write(f"NITRADO_TOKEN={final_config.get('NITRADO_TOKEN', 'seu_token_nitrado_api')}\n")
        f.write(f"SERVER_ID={final_config.get('SERVER_ID', 'seu_server_id')}\n\n")
        
        # Dashboard
        f.write("# ===== DASHBOARD =====\n")
        f.write(f"DASHBOARD_PORT={final_config.get('DASHBOARD_PORT', '5000')}\n")
        f.write(f"DASHBOARD_HOST={final_config.get('DASHBOARD_HOST', '0.0.0.0')}\n\n")
        
        # Segurança
        f.write("# ===== SEGURANCA =====\n")
        f.write(f"ADMIN_WHITELIST={final_config.get('ADMIN_WHITELIST', '123456789,987654321')}\n")
        f.write(f"RATE_LIMIT_ENABLED={final_config.get('RATE_LIMIT_ENABLED', 'true')}\n\n")
        
        # Opcionais
        f.write("# ===== CONFIGURACOES OPCIONAIS =====\n")
        f.write(f"DEBUG_MODE={final_config.get('DEBUG_MODE', 'false')}\n")
        f.write(f"LOG_LEVEL={final_config.get('LOG_LEVEL', 'INFO')}\n")
    
    print("\n[OK] Arquivo .env atualizado com sucesso!")
    print("\nConfiguracoes OAuth adicionadas:")
    print(f"  - DISCORD_CLIENT_ID: {oauth_config['DISCORD_CLIENT_ID']}")
    print(f"  - DISCORD_CLIENT_SECRET: {oauth_config['DISCORD_CLIENT_SECRET'][:20]}...")
    print(f"  - DISCORD_REDIRECT_URI: {oauth_config['DISCORD_REDIRECT_URI']}")
    print(f"  - SECRET_KEY: Configurada")
    
    print("\nAinda precisa configurar:")
    if final_config.get('DISCORD_TOKEN', '').startswith('seu_'):
        print("  - DISCORD_TOKEN (token do bot)")
    if final_config.get('NOTIFICATION_WEBHOOK_URL', '').startswith('seu_'):
        print("  - NOTIFICATION_WEBHOOK_URL (webhook para notificacoes)")
    
    print("\nProximo passo: Edite o .env e adicione as credenciais faltantes")

if __name__ == "__main__":
    print("="*60)
    print("ATUALIZADOR DE .ENV - BigodeTexas Bot")
    print("="*60)
    print()
    
    try:
        update_env_file()
        print("\n" + "="*60)
        print("CONCLUIDO!")
        print("="*60)
    except Exception as e:
        print(f"\n[ERRO] Falha ao atualizar .env: {e}")
