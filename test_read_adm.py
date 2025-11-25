"""
Teste de Leitura do Log ADM
Verifica se ha eventos de morte no log atual
"""
import ftplib
import os
from dotenv import load_dotenv
import sys
import codecs

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

LOG_FILE = "DayZServer_X1_x64_2025-11-24_19-53-43.ADM"
LOG_PATH = "/dayzxb/config"

print("=" * 60)
print("TESTE DE LEITURA DO LOG ADM")
print("=" * 60)

# Conectar FTP
print(f"\nConectando ao FTP...")
ftp = ftplib.FTP()
ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
ftp.login(FTP_USER, FTP_PASS)
print("[OK] Conectado!")

# Navegar para o diretorio do log
print(f"\nNavegando para: {LOG_PATH}")
ftp.cwd(LOG_PATH)

# Ler o arquivo
print(f"\nLendo arquivo: {LOG_FILE}")
lines = []

def handle_line(line):
    lines.append(line)

ftp.retrlines(f"RETR {LOG_FILE}", handle_line)

print(f"[OK] Total de linhas: {len(lines)}")

# Procurar eventos de morte
print("\nProcurando eventos de morte...")
kill_events = []
death_events = []

for idx, line in enumerate(lines, 1):
    if "killed by Player" in line:
        kill_events.append((idx, line))
    elif "died" in line and "Player" in line and "committed suicide" not in line:
        death_events.append((idx, line))

print(f"\n[RESULTADO]")
print(f"  Eventos 'killed by Player': {len(kill_events)}")
print(f"  Eventos 'died': {len(death_events)}")

if kill_events:
    print(f"\n[ULTIMOS 5 KILLS]")
    for idx, line in kill_events[-5:]:
        print(f"  Linha {idx}: {line[:120]}")

if death_events:
    print(f"\n[ULTIMAS 5 MORTES]")
    for idx, line in death_events[-5:]:
        print(f"  Linha {idx}: {line[:120]}")

if not kill_events and not death_events:
    print("\n[AVISO] Nenhum evento de morte encontrado no log!")
    print("\nULTIMAS 10 LINHAS DO LOG:")
    for line in lines[-10:]:
        print(f"  {line[:120]}")

ftp.quit()
print("\n" + "=" * 60)
print("Teste concluido!")
print("=" * 60)
