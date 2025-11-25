"""
Verifica eventos de PvP (killed by Player) no log ADM
Le linhas completas sem truncar
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

print("=" * 80)
print("VERIFICACAO DE EVENTOS PVP (killed by Player)")
print("=" * 80)

# Conectar FTP
print(f"\nConectando ao FTP...")
ftp = ftplib.FTP()
ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
ftp.login(FTP_USER, FTP_PASS)
print("[OK] Conectado!")

# Navegar para o diretorio do log
ftp.cwd(LOG_PATH)

# Ler o arquivo
print(f"\nLendo arquivo: {LOG_FILE}")
lines = []

def handle_line(line):
    lines.append(line)

ftp.retrlines(f"RETR {LOG_FILE}", handle_line)

print(f"[OK] Total de linhas: {len(lines)}")

# Procurar eventos de PvP
print("\nProcurando eventos 'killed by Player'...")
pvp_events = []

for idx, line in enumerate(lines, 1):
    if "killed by Player" in line:
        pvp_events.append((idx, line))

print(f"\n[RESULTADO] Eventos PvP encontrados: {len(pvp_events)}")

if pvp_events:
    print("\n" + "=" * 80)
    print("EVENTOS PVP COMPLETOS:")
    print("=" * 80)
    for idx, line in pvp_events:
        print(f"\nLinha {idx}:")
        print(f"{line}")
        print("-" * 80)
else:
    print("\n[CONCLUSAO] NAO HA EVENTOS DE PVP NO LOG!")
    print("\nIsso significa que:")
    print("  1. Nao houve mortes PvP desde as 9h da manha")
    print("  2. Apenas mortes naturais (zumbis, fome, queda, etc.)")
    
    print("\n[ULTIMOS 10 EVENTOS DE MORTE (qualquer tipo)]:")
    death_lines = [l for l in lines if "died" in l or "killed" in l]
    for line in death_lines[-10:]:
        print(f"  {line}")

ftp.quit()
print("\n" + "=" * 80)
print("Verificacao concluida!")
print("=" * 80)
