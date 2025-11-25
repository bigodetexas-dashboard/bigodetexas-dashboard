"""
Script de Diagnostico do Killfeed
Verifica conectividade FTP, logs disponiveis e ultima atividade
"""
import ftplib
import os
from dotenv import load_dotenv
from datetime import datetime
import sys
import codecs

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

print("=" * 60)
print("DIAGNOSTICO DO KILLFEED - BigodeTexas Bot")
print("=" * 60)
print(f"\nData/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. Verificar credenciais
print("1. VERIFICANDO CREDENCIAIS FTP...")
if not all([FTP_HOST, FTP_USER, FTP_PASS]):
    print("   [ERRO] Credenciais FTP incompletas no .env!")
    print(f"   - FTP_HOST: {'OK' if FTP_HOST else 'FALTANDO'}")
    print(f"   - FTP_USER: {'OK' if FTP_USER else 'FALTANDO'}")
    print(f"   - FTP_PASS: {'OK' if FTP_PASS else 'FALTANDO'}")
    exit(1)
else:
    print(f"   [OK] Host: {FTP_HOST}:{FTP_PORT}")
    print(f"   [OK] User: {FTP_USER}")

# 2. Testar conexao FTP
print("\n2. TESTANDO CONEXAO FTP...")
try:
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
    ftp.login(FTP_USER, FTP_PASS)
    print("   [OK] Conexao estabelecida com sucesso!")
except Exception as e:
    print(f"   [ERRO] ERRO DE CONEXAO: {e}")
    exit(1)

# 3. Buscar arquivos de log
print("\n3. BUSCANDO ARQUIVOS DE LOG (.ADM, .RPT)...")
found_logs = []

def scan_directory(path="/"):
    try:
        ftp.cwd(path)
        items = []
        try:
            for name, facts in ftp.mlsd():
                items.append((name, facts))
        except:
            for name in ftp.nlst():
                items.append((name, {'type': 'unknown'}))
        
        for name, facts in items:
            if name in [".", ".."]:
                continue
            
            full_path = f"{path}/{name}" if path != "/" else f"/{name}"
            lower_name = name.lower()
            
            # Arquivos de log
            if lower_name.endswith((".adm", ".rpt", ".log")):
                if "crash" not in lower_name:
                    try:
                        # Pega tamanho e data de modificacao
                        size = facts.get('size', 'N/A')
                        modify = facts.get('modify', 'N/A')
                        found_logs.append({
                            'path': full_path,
                            'name': name,
                            'size': size,
                            'modified': modify
                        })
                    except:
                        found_logs.append({
                            'path': full_path,
                            'name': name,
                            'size': 'N/A',
                            'modified': 'N/A'
                        })
            
            # Diretorios
            if "." not in name or facts.get('type') == 'dir':
                try:
                    scan_directory(full_path)
                    ftp.cwd(path)
                except:
                    pass
    except Exception as e:
        print(f"   [AVISO] Erro ao escanear {path}: {e}")

scan_directory("/")

if not found_logs:
    print("   [ERRO] NENHUM ARQUIVO DE LOG ENCONTRADO!")
    ftp.quit()
    exit(1)

print(f"   [OK] Encontrados {len(found_logs)} arquivo(s) de log:\n")

# Ordenar por data de modificacao (mais recente primeiro)
found_logs.sort(key=lambda x: x.get('modified', ''), reverse=True)

for idx, log in enumerate(found_logs[:5], 1):  # Mostra apenas os 5 mais recentes
    print(f"   {idx}. {log['name']}")
    print(f"      Caminho: {log['path']}")
    print(f"      Tamanho: {log['size']} bytes")
    print(f"      Modificado: {log['modified']}")
    print()

# 4. Verificar log mais recente
latest_log = found_logs[0]
print(f"4. ANALISANDO LOG MAIS RECENTE: {latest_log['name']}")

try:
    ftp.cwd(os.path.dirname(latest_log['path']) or "/")
    
    # Ler ultimas 50 linhas
    lines = []
    def handle_line(line):
        lines.append(line)
    
    ftp.retrlines(f"RETR {os.path.basename(latest_log['path'])}", handle_line)
    
    total_lines = len(lines)
    print(f"   Total de linhas: {total_lines}")
    
    # Procurar por eventos de morte
    kill_lines = [l for l in lines if "killed by Player" in l or "died" in l]
    
    if kill_lines:
        print(f"   [OK] Encontrados {len(kill_lines)} evento(s) de morte!")
        print("\n   ULTIMOS 3 EVENTOS:")
        for event in kill_lines[-3:]:
            print(f"      - {event[:100]}...")
    else:
        print("   [AVISO] NENHUM EVENTO DE MORTE ENCONTRADO NAS ULTIMAS LINHAS")
        print("\n   ULTIMAS 5 LINHAS DO LOG:")
        for line in lines[-5:]:
            print(f"      {line[:100]}")
    
except Exception as e:
    print(f"   [ERRO] ERRO AO LER LOG: {e}")

# 5. Verificar bot_state.json
print("\n5. VERIFICANDO ESTADO DO BOT...")
try:
    import json
    with open("bot_state.json", "r") as f:
        state = json.load(f)
    
    current_file = state.get("current_log_file", "N/A")
    last_lines = state.get("last_read_lines", 0)
    
    print(f"   Arquivo atual: {current_file}")
    print(f"   Ultima linha lida: {last_lines}")
    
    if current_file != latest_log['name']:
        print(f"\n   [PROBLEMA DETECTADO!]")
        print(f"   O bot esta lendo: {current_file}")
        print(f"   Mas o log mais recente e: {latest_log['name']}")
        print(f"\n   [SOLUCAO] Atualize bot_state.json ou delete o arquivo para forcar re-deteccao.")
    else:
        print(f"   [OK] Bot esta apontando para o log correto!")
        
        if last_lines >= total_lines:
            print(f"\n   [PROBLEMA] Bot ja leu todas as linhas ({last_lines} >= {total_lines})")
            print(f"   [SOLUCAO] Aguarde novas mortes ou reduza 'last_read_lines' para reprocessar.")
        
except FileNotFoundError:
    print("   [AVISO] Arquivo bot_state.json nao encontrado (sera criado na primeira execucao)")
except Exception as e:
    print(f"   [ERRO] {e}")

# 6. Resumo
print("\n" + "=" * 60)
print("RESUMO DO DIAGNOSTICO")
print("=" * 60)
print(f"Conexao FTP: OK")
print(f"Logs encontrados: {len(found_logs)}")
print(f"Log mais recente: {latest_log['name']}")
print(f"Total de linhas: {total_lines if 'total_lines' in locals() else 'N/A'}")
print(f"Eventos de morte: {len(kill_lines) if 'kill_lines' in locals() else 'N/A'}")
print("=" * 60)

ftp.quit()
print("\nDiagnostico concluido!")
