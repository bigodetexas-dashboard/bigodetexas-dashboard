"""
Script de Integração: Nitrado FTP → Heatmap Database
Lê logs RPT do servidor Nitrado e envia para a API /api/parse_log
"""

import os
import time
import requests
from ftplib import FTP
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configurações
NITRADO_FTP_HOST = os.getenv('NITRADO_FTP_HOST', 'ftp.nitrado.net')
NITRADO_FTP_USER = os.getenv('NITRADO_FTP_USER')
NITRADO_FTP_PASS = os.getenv('NITRADO_FTP_PASS')
NITRADO_LOG_PATH = '/games/ni123456_1/noftp/dayzxb/config-1/profiles/'  # Ajustar conforme seu servidor

API_URL = 'http://localhost:5001/api/parse_log'
CHECK_INTERVAL = 60  # Verificar a cada 60 segundos

# Arquivo para rastrear última linha lida
LAST_POSITION_FILE = 'last_log_position.txt'

def get_last_position():
    """Retorna a última posição lida do arquivo de log"""
    if os.path.exists(LAST_POSITION_FILE):
        with open(LAST_POSITION_FILE, 'r') as f:
            return int(f.read().strip())
    return 0

def save_last_position(position):
    """Salva a última posição lida"""
    with open(LAST_POSITION_FILE, 'w') as f:
        f.write(str(position))

def download_latest_rpt(ftp):
    """
    Baixa o arquivo RPT mais recente do servidor Nitrado
    Retorna o conteúdo do arquivo
    """
    try:
        # Listar arquivos .rpt no diretório
        ftp.cwd(NITRADO_LOG_PATH)
        files = []
        ftp.retrlines('LIST', files.append)
        
        # Filtrar apenas .rpt
        rpt_files = [f for f in files if '.rpt' in f.lower()]
        
        if not rpt_files:
            print("Nenhum arquivo RPT encontrado.")
            return None
        
        # Pegar o mais recente (último da lista geralmente)
        latest_file = rpt_files[-1].split()[-1]
        print(f"Baixando arquivo: {latest_file}")
        
        # Baixar conteúdo
        content = []
        ftp.retrlines(f'RETR {latest_file}', content.append)
        
        return '\n'.join(content)
        
    except Exception as e:
        print(f"Erro ao baixar RPT: {e}")
        return None

def send_to_api(log_text):
    """
    Envia o texto do log para a API /api/parse_log
    """
    try:
        response = requests.post(API_URL, json={
            'text': log_text,
            'source': 'nitrado_ftp'
        }, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Sucesso: {result['events_saved']} eventos salvos de {result['events_parsed']} parseados")
            return True
        else:
            print(f"❌ Erro na API: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar para API: {e}")
        return False

def process_new_lines(full_content):
    """
    Processa apenas as novas linhas desde a última verificação
    """
    last_pos = get_last_position()
    lines = full_content.splitlines()
    
    if last_pos >= len(lines):
        print("Nenhuma linha nova encontrada.")
        return None
    
    # Pegar apenas linhas novas
    new_lines = lines[last_pos:]
    new_content = '\n'.join(new_lines)
    
    # Atualizar posição
    save_last_position(len(lines))
    
    return new_content

def main():
    """
    Loop principal: conecta ao FTP, baixa logs, envia para API
    """
    print("🚀 Iniciando integração Nitrado → Heatmap")
    print(f"FTP: {NITRADO_FTP_HOST}")
    print(f"API: {API_URL}")
    print(f"Intervalo: {CHECK_INTERVAL}s\n")
    
    if not NITRADO_FTP_USER or not NITRADO_FTP_PASS:
        print("❌ ERRO: Credenciais FTP não configuradas no .env")
        print("Configure NITRADO_FTP_USER e NITRADO_FTP_PASS")
        return
    
    while True:
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Verificando logs...")
            
            # Conectar ao FTP
            ftp = FTP(NITRADO_FTP_HOST)
            ftp.login(NITRADO_FTP_USER, NITRADO_FTP_PASS)
            
            # Baixar RPT
            full_content = download_latest_rpt(ftp)
            ftp.quit()
            
            if full_content:
                # Processar apenas linhas novas
                new_content = process_new_lines(full_content)
                
                if new_content:
                    print(f"📝 {len(new_content.splitlines())} novas linhas encontradas")
                    # Enviar para API
                    send_to_api(new_content)
                    
            print(f"⏳ Aguardando {CHECK_INTERVAL}s...\n")
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n👋 Encerrando...")
            break
        except Exception as e:
            print(f"❌ Erro no loop principal: {e}")
            print(f"⏳ Tentando novamente em {CHECK_INTERVAL}s...\n")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
