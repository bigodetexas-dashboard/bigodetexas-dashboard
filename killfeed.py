import ftplib
import time
import re
import requests
import discord
import os
import json
from datetime import datetime
import io
import asyncio

# --- CONFIGURAÇÃO ---
FTP_HOST = "brsp012.gamedata.io"
FTP_PORT = 21
FTP_USER = "ni3622181_1"
FTP_PASS = "hqPuAFd9"

# URL do Webhook do Discord
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1441892129591922782/20eO0Z6wurnlD47-BgQ7yP5ePt0mK-2pXF8iQUuLfllqkPyVGdkVuSdTr6vd5sBEWCz2"

# Arquivo de Banco de Dados Local
DB_FILE = "players_db.json"

# Intervalo de verificação em segundos
CHECK_INTERVAL = 30

# --- FIM DA CONFIGURAÇÃO ---

last_read_lines = 0
current_log_file = ""

# --- SISTEMA DE BANCO DE DADOS ---
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_db(data):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar DB: {e}")

def get_player_stats(db, player_name):
    if player_name not in db:
        db[player_name] = {
            "kills": 0,
            "deaths": 0,
            "killstreak": 0,
            "best_killstreak": 0,
            "last_death_time": time.time(), # Começa a contar vida agora
            "first_seen": time.time()
        }
    return db[player_name]

def update_stats(killer_name, victim_name):
    db = load_db()
    current_time = time.time()
    
    # Atualiza Matador
    killer = get_player_stats(db, killer_name)
    killer["kills"] += 1
    killer["killstreak"] += 1
    if killer["killstreak"] > killer["best_killstreak"]:
        killer["best_killstreak"] = killer["killstreak"]
    
    # Atualiza Vítima
    victim = get_player_stats(db, victim_name)
    victim["deaths"] += 1
    victim["killstreak"] = 0 # Zera a série
    
    # Calcula tempo de vida da vítima antes de resetar
    time_alive_seconds = int(current_time - victim.get("last_death_time", current_time))
    victim["last_death_time"] = current_time # Reseta o timer de vida
    
    save_db(db)
    return killer, victim, time_alive_seconds

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}h:{minutes:02d}m:{secs:02d}s"

def calculate_level(kills):
    # Fórmula simples: Nível = 1 + (Kills / 5)
    return 1 + int(kills / 5)

def calculate_kd(kills, deaths):
    if deaths == 0:
        return kills # Se nunca morreu, K/D é igual às kills
    return round(kills / deaths, 2)

# --- FUNÇÕES DE REDE ---
def connect_ftp():
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        print(f"Conectado ao FTP: {FTP_HOST}")
        return ftp
    except Exception as e:
        print(f"Erro ao conectar no FTP: {e}")
        return None

def find_latest_adm_log(ftp):
    """Encontra o arquivo .ADM mais recente no servidor (Busca Recursiva)."""
    print("Buscando arquivos de log (.ADM, .RPT, .log)...")
    found_files = []

    def traverse(path):
        try:
            ftp.cwd(path)
            items = ftp.mlsd() 
        except:
            try:
                ftp.cwd(path)
                items = []
                for name in ftp.nlst():
                    items.append((name, {'type': 'unknown'}))
            except Exception as e:
                return

        for name, facts in items:
            if name in [".", ".."]:
                continue
            
            full_path = f"{path}/{name}" if path != "/" else f"/{name}"
            
            lower_name = name.lower()
            if lower_name.endswith(".adm") or lower_name.endswith(".rpt"):
                if "crash" not in lower_name:
                    found_files.append(full_path)
            
            if "." not in name or facts.get('type') == 'dir': 
                try:
                    traverse(full_path)
                    ftp.cwd(path) 
                except:
                    pass

    try:
        ftp.cwd("/")
        root_items = ftp.nlst()
        for item in root_items:
            lower_item = item.lower()
            if lower_item.endswith(".adm") or lower_item.endswith(".rpt"):
                if "crash" not in lower_item:
                    found_files.append(f"/{item}")
            elif "." not in item: 
                traverse(f"/{item}")
    except Exception as e:
        print(f"Erro na busca inicial: {e}")

    if not found_files:
        print("Nenhum arquivo de log (.ADM ou .RPT) encontrado.")
        return None

    found_files.sort()
    latest_file = found_files[-1]
    print(f"Usando log mais recente: {latest_file}")
    return latest_file

def send_discord_message(embed):
    """Envia um embed via webhook (usado apenas quando o script é executado standalone)."""
    data = {
        "username": "DayZ Killfeed",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",
        "embeds": [embed.to_dict()]
    }
    try:
        result = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if result.status_code == 204:
            print("Mensagem enviada via webhook.")
        else:
            print(f"Falha ao enviar webhook: {result.status_code}")
    except Exception as e:
        print(f"Erro ao enviar webhook: {e}")

async def parse_log_line(line):
    """Analisa a linha do log para ver se é uma morte e devolve um Embed Discord."""
    line = line.strip()
    if not line:
        return None

    # Ignora suicídios
    if "committed suicide" in line:
        return None

    # --- KILLFEED (MORTES) ---
    if "killed by Player" in line:
        try:
            parts = line.split("killed by Player")
            victim_part = parts[0]
            killer_part = parts[1]

            victim_name = victim_part.split("Player")[1].split("(")[0].strip().replace('"', '').replace("'", "")
            killer_name = killer_part.split("(")[0].strip().replace('"', '').replace("'", "")

            # Atualiza Stats
            k_stats, v_stats, time_alive = update_stats(killer_name, victim_name)

            # Dados do Matador
            k_level = calculate_level(k_stats["kills"])
            k_kd = calculate_kd(k_stats["kills"], k_stats["deaths"])

            # Dados da Vítima
            v_level = calculate_level(v_stats["kills"])  # Nível baseado nas kills dela
            v_kd = calculate_kd(v_stats["kills"], v_stats["deaths"])

            # Extração de Arma
            weapon = "Desconhecida"
            if " with " in line:
                weapon_part = line.split(" with ")[1]
                weapon = weapon_part.split(" ")[0].strip()

            # Extração de Localização e Distância
            location = "Desconhecido"
            distance = "N/A"
            coords_text = ""
            if "<" in line and ">" in line:
                coords_text = line.split("<")[1].split(">")[0]
                try:
                    c_parts = coords_text.split(",")
                    x = float(c_parts[0])
                    z = float(c_parts[2])
                    location = f"{x:.1f} x {z:.1f}"
                    
                    # Tenta calcular distância se houver duas coordenadas (ex: killer e victim)
                    # O log padrão do DayZ geralmente mostra apenas a coordenada da vítima ou do evento
                    # Mas se tivermos sorte de ter ambas, poderíamos calcular.
                    # Por enquanto, vamos assumir que não temos a do killer facilmente na mesma linha
                    # a menos que o formato seja específico.
                    # Se o log tiver <x1,y1,z1> ... <x2,y2,z2>, podemos tentar.
                    
                    all_coords = re.findall(r"<([^>]+)>", line)
                    if len(all_coords) >= 2:
                        c1 = all_coords[0].split(",")
                        c2 = all_coords[1].split(",")
                        x1, y1, z1 = float(c1[0]), float(c1[1]), float(c1[2])
                        x2, y2, z2 = float(c2[0]), float(c2[1]), float(c2[2])
                        dist = ((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)**0.5
                        distance = f"{dist:.1f}m"

                except:
                    location = coords_text

            # Monta mensagem
            msg = f"""
🧛‍♂️ **Assassino**
  ╒┄{killer_name}
  ╞┄Nível:………〘{k_level}〙
  ╞┄Matou:……… {k_stats['kills']}
  ╞┄Série:……… {k_stats['killstreak']}
  ╞┄Distância:… {distance}
  ╘┄PvP K/D:… {k_kd}
🧟 **Vítima**
  ╒┄{victim_name}
  ╞┄Nível:………〘{v_level}〙
  ╞┄Morreu:…… {v_stats['deaths']}
  ╞┄Série:……… {v_stats['killstreak']}
  ╞┄PvP K/D:… {v_kd}
  ╘┄Viveu:… ⌛ {format_time(time_alive)}
🕵️‍♂️ **Perícia**
  ╒┄Arma: {weapon}
  ╘┄Local: {location}
"""
            embed = discord.Embed(description=msg, color=discord.Color.orange())
            return embed
        except Exception as e:
            print(f"Erro ao processar linha de morte: {e}")
            return None

    # Caso seja apenas morte sem matador (ex.: "Player X died")
    if "died" in line and "Player" in line:
        try:
            victim_name = line.split("Player")[1].split("died")[0].split("(")[0].strip().replace('"', '').replace("'", "")
            db = load_db()
            victim = get_player_stats(db, victim_name)
            victim["deaths"] += 1
            victim["killstreak"] = 0
            time_alive = int(time.time() - victim.get("last_death_time", time.time()))
            victim["last_death_time"] = time.time()
            save_db(db)
            msg = f"💀 **{victim_name}** morreu. (Viveu: {format_time(time_alive)})"
            embed = discord.Embed(description=msg, color=discord.Color.red())
            return embed
        except Exception as e:
            print(f"Erro ao processar morte sem matador: {e}")
            return None

    return None

def main():
    global last_read_lines
    global current_log_file

    print("Iniciando Monitoramento de Killfeed (Standalone)...")
    
    while True:
        ftp = connect_ftp()
        if not ftp:
            time.sleep(60)
            continue

        if not current_log_file:
            current_log_file = find_latest_adm_log(ftp)
            if current_log_file:
                try:
                    bio = io.BytesIO()
                    ftp.retrbinary(f"RETR {current_log_file}", bio.write)
                    content = bio.getvalue().decode('utf-8', errors='ignore')
                    lines = content.split('\n')
                    last_read_lines = len(lines)
                    print(f"Iniciando leitura a partir da linha {last_read_lines}")
                except Exception as e:
                    print(f"Erro ao ler arquivo inicial: {e}")
                    current_log_file = ""

        else:
            try:
                bio = io.BytesIO()
                ftp.retrbinary(f"RETR {current_log_file}", bio.write)
                content = bio.getvalue().decode('utf-8', errors='ignore')
                lines = content.split('\n')
                
                total_lines = len(lines)
                
                if total_lines > last_read_lines:
                    new_lines = lines[last_read_lines:]
                    print(f"Novas linhas detectadas: {len(new_lines)}")
                    
                    for line in new_lines:
                        # parse_log_line agora é async, então precisamos rodar no loop de eventos
                        # Como main() é síncrono aqui (legado), usamos asyncio.run
                        embed = asyncio.run(parse_log_line(line))
                        if embed:
                            send_discord_message(embed)
                    
                    last_read_lines = total_lines
                
                elif total_lines < last_read_lines:
                    print("Arquivo de log mudou. Reiniciando busca.")
                    current_log_file = ""
                    last_read_lines = 0

            except Exception as e:
                print(f"Erro ao processar arquivo: {e}")
                current_log_file = ""

        try:
            ftp.quit()
        except:
            pass
            
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
