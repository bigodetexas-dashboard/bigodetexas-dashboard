import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
import random
from datetime import datetime, timedelta, timezone
import ftplib
import re
import io
import time
import math
import aiohttp
import xml.etree.ElementTree as ET
from flask import Flask
from dotenv import load_dotenv

# Importar módulo de segurança
from security import (
    rate_limiter,
    input_validator,
    security_logger,
    backup_manager,
    AdminWhitelist
)
import database

# Carregar variáveis de ambiente
load_dotenv()

# --- CONFIGURAÇÃO GERAL (de variáveis de ambiente) ---
TOKEN = os.getenv("DISCORD_TOKEN")

# FTP (Nitrado)
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

# Nitrado API
NITRADO_TOKEN = os.getenv("NITRADO_TOKEN")
SERVICE_ID = os.getenv("SERVICE_ID")

# Segurança
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_IDS_STR = os.getenv("ADMIN_WHITELIST", "")
ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(",") if id.strip()]

# Footer Icon
FOOTER_ICON = os.getenv("FOOTER_ICON", "https://cdn.discordapp.com/attachments/1442262893188878496/1442286419539394682/logo_texas.png")

# Inicializar whitelist de admin
from security import admin_whitelist as _admin_whitelist
admin_whitelist = AdminWhitelist(ADMIN_IDS)

# Validar configurações críticas
if not TOKEN:
    raise ValueError("DISCORD_TOKEN não encontrado no .env!")
if not FTP_HOST or not FTP_USER or not FTP_PASS:
    raise ValueError("Credenciais FTP não encontradas no .env!")

async def restart_server():
    """Envia comando de restart para a API da Nitrado."""
    url = f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers/restart"
    headers = {"Authorization": f"Bearer {NITRADO_TOKEN}"}
    
    print(f"Tentando reiniciar servidor ID {SERVICE_ID}...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'success':
                        print(f"[SUCESSO] Servidor reiniciando!")
                        return True, "Servidor reiniciando com sucesso!"
                    else:
                        print(f"[AVISO] API: {data}")
                        return False, f"Erro API: {data.get('message')}"
                else:
                    text = await response.text()
                    print(f"❌ ERRO API: {response.status} - {text}")
                    return False, f"Erro HTTP: {response.status}"
    except Exception as e:
        print(f"[ERRO] Erro de conexao: {e}")
        return False, f"Erro de conexao: {e}"

# Arquivos de Dados
ECONOMY_FILE = "economy.json"
ITEMS_FILE = "items.json"
LINKS_FILE = "links.json"
CONFIG_FILE = "config.json"
PLAYERS_DB_FILE = "players_db.json"
ACHIEVEMENTS_FILE = "achievements.json"
CLANS_FILE = "clans.json"
MISSIONS_FILE = "missions.json"

# Rastreamento de Duplicação
pickup_tracker = {} # {player_name: [(item_id, timestamp)]}
active_sessions = {} # {player_name: login_timestamp}

# Configurações de Economia
DAILY_BONUS = 500
HOURLY_SALARY = 1000
BONUS_10H = 5000
KILL_REWARD = 50

# Killfeed State
current_log_file = ""
last_read_lines = 0

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# --- DASHBOARD & WEB SERVER ---
from web_dashboard import dashboard_bp
from discord_oauth import init_oauth

# Inicializar Flask App
health_app = Flask(__name__)
health_app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key") # Importante para sessões

# CRITICAL: Desabilitar cache de templates para forçar reload
health_app.config['TEMPLATES_AUTO_RELOAD'] = True
health_app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
health_app.config['EXPLAIN_TEMPLATE_LOADING'] = True

# Inicializar OAuth
init_oauth(health_app)

# Registrar Blueprint do Dashboard
health_app.register_blueprint(dashboard_bp)

# Rota de Health Check (mantida para compatibilidade)
@health_app.route("/health")
def health():
    return "OK", 200

import threading
# Rodar o servidor web em uma thread separada
threading.Thread(target=lambda: health_app.run(host="0.0.0.0", port=int(os.getenv("PORT", 3000))), daemon=True).start()

# Iniciar processador de entregas em background
from delivery_processor import process_pending_deliveries
threading.Thread(target=lambda: asyncio.run(process_pending_deliveries()), daemon=True).start()
print("[DELIVERY] Processador de entregas iniciado!")

# --- CLASSE DE PAGINAÇÃO INTERATIVA ---
class ShopPaginator(discord.ui.View):
    def __init__(self, items_list, category_name, category_emoji, items_per_page=5):
        super().__init__(timeout=60)
        self.items_list = items_list
        self.category_name = category_name
        self.category_emoji = category_emoji
        self.items_per_page = items_per_page
        self.current_page = 0
        self.max_pages = (len(items_list) - 1) // items_per_page + 1
        
    def get_embed(self):
        start = self.current_page * self.items_per_page
        end = start + self.items_per_page
        page_items = self.items_list[start:end]
        
        embed = discord.Embed(
            title=f"{self.category_emoji} LOJA: {self.category_name.upper()}",
            description=f"Use `!comprar <codigo>` para adquirir.\nPágina {self.current_page + 1}/{self.max_pages}",
            color=discord.Color.gold()
        )
        
        for k, v in page_items:
            desc = v.get('description', 'Sem descrição')
            embed.add_field(
                name=f"{v['name']} (`{k}`)",
                value=f"💰 {v['price']} DZ Coins\n_{desc}_",
                inline=False
            )
        
        embed.set_footer(text="BigodeTexas • Qualidade Garantida", icon_url=FOOTER_ICON)
        return embed
    
    @discord.ui.button(label="◀️ Anterior", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.send_message("Você já está na primeira página!", ephemeral=True)
    
    @discord.ui.button(label="▶️ Próximo", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
        else:
            await interaction.response.send_message("Você já está na última página!", ephemeral=True)

# --- FUNÇÕES AUXILIARES (JSON) ---
def load_json(filename):
    if not os.path.exists(filename): return {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return {}

def save_json(filename, data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar {filename}: {e}")

# --- DECORATOR DE RATE LIMITING ---
def rate_limit():
    """Decorator que aplica rate limiting em comandos"""
    async def predicate(ctx):
        if not rate_limiter.is_allowed(ctx.author.id):
            security_logger.log_rate_limit(ctx.author.id)
            await ctx.send("⏰ **Calma lá, parceiro!** Você está enviando comandos muito rápido. Aguarde um momento.")
            return False
        return True
    return commands.check(predicate)

# --- DECORATOR DE AUTENTICAÇÃO ADMIN ---
def require_admin_password():
    """Decorator que solicita senha E verifica whitelist antes de executar comandos admin"""
    async def predicate(ctx):
        # Verifica whitelist primeiro
        if not admin_whitelist.is_admin(ctx.author.id):
            security_logger.log_failed_auth(ctx.author.id, ctx.command.name)
            await ctx.send("❌ **Acesso Negado!** Você não está autorizado a usar comandos administrativos.")
            return False
        
        # Envia mensagem solicitando senha
        await ctx.send("🔐 **Comando Administrativo**\nDigite a senha de acesso:")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            msg = await bot.wait_for('message', check=check, timeout=30.0)
            
            if msg.content == ADMIN_PASSWORD:
                # Deleta a mensagem com a senha por segurança
                try:
                    await msg.delete()
                except:
                    pass
                security_logger.log_admin_action(ctx.author.id, ctx.command.name)
                return True
            else:
                await ctx.send("❌ **Senha incorreta!** Acesso negado.")
                security_logger.log_failed_auth(ctx.author.id, f"{ctx.command.name} - wrong password")
                # Deleta a tentativa incorreta
                try:
                    await msg.delete()
                except:
                    pass
                return False
                
        except asyncio.TimeoutError:
            await ctx.send("⏰ **Tempo esgotado!** Autenticação cancelada.")
            return False
    
    return commands.check(predicate)

# --- SISTEMA DE ECONOMIA ---
def get_balance(user_id):
    eco = database.get_economy(user_id)
    return eco.get("balance", 0) if eco else 0

def update_balance(user_id, amount, transaction_type="other", details=""):
    user_id = str(user_id)
    eco = database.get_economy(user_id)
    
    if not eco:
        eco = {"discord_id": user_id, "balance": 0, "transactions": []}
    
    # PROTEÇÃO: Não permite saldo negativo
    new_balance = eco.get("balance", 0) + amount
    if new_balance < 0:
        print(f"[AVISO] Tentativa de saldo negativo bloqueada para user {user_id}: {eco.get('balance', 0)} + {amount} = {new_balance}")
        new_balance = 0
    
    eco["balance"] = new_balance
    
    # Registra transação
    transactions = eco.get("transactions", [])
    if isinstance(transactions, str): # Handle JSON string if needed
        try: transactions = json.loads(transactions)
        except: transactions = []
        
    transactions.append({
        "type": transaction_type,
        "amount": amount,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "balance_after": new_balance
    })
    
    # Mantém apenas últimas 50 transações
    if len(transactions) > 50:
        transactions = transactions[-50:]
    
    eco["transactions"] = transactions
    
    database.save_economy(user_id, eco)
    return new_balance

def add_to_inventory(user_id, item_key, item_name):
    user_id = str(user_id)
    eco = database.get_economy(user_id)
    
    if not eco:
        eco = {"discord_id": user_id, "balance": 0, "inventory": {}}
        
    inventory = eco.get("inventory", {})
    if isinstance(inventory, str):
        try: inventory = json.loads(inventory)
        except: inventory = {}

    if item_key in inventory:
        inventory[item_key]["count"] += 1
    else:
        inventory[item_key] = {"name": item_name, "count": 1}
    
    eco["inventory"] = inventory
    database.save_economy(user_id, eco)

# --- SISTEMA DE LOJA ---
def find_item_by_key(key):
    items_data = load_json(ITEMS_FILE)
    for category, items in items_data.items():
        if key in items:
            return items[key]
    return None

# --- SINCRONIZAÇÃO DE TYPES ---
def sync_types_from_server():
    """Baixa types.xml do servidor e atualiza items.json"""
    try:
        ftp = connect_ftp()
        if not ftp:
            return False, "Erro ao conectar FTP"
        
        # Caminho do types.xml no servidor
        types_path = "/dayzxb_missions/dayzOffline.chernarusplus/db/types.xml"
        
        # Baixa o arquivo
        bio = io.BytesIO()
        try:
            ftp.retrbinary(f"RETR {types_path}", bio.write)
        except Exception as e:
            ftp.quit()
            return False, f"Erro ao baixar types.xml: {e}"
        
        ftp.quit()
        
        # Parseia XML
        bio.seek(0)
        tree = ET.parse(bio)
        root = tree.getroot()
        
        # Categorias baseadas em tags/flags
        category_map = {
            "weapons": "armas",
            "ammunition": "municao",
            "magazines": "carregadores",
            "attachments": "acessorios",
            "tools": "ferramentas",
            "medical": "medico",
            "clothes": "roupas",
            "vehicles": "veiculos",
            "default": "construcao"
        }
        
        new_items = {}
        items_added = 0
        
        for type_elem in root.findall("type"):
            name = type_elem.get("name")
            if not name:
                continue
            
            # Pega nominal (quantidade no servidor) como base de preço
            nominal_elem = type_elem.find("nominal")
            nominal = int(nominal_elem.text) if nominal_elem is not None else 10
            
            # Preço baseado em raridade (quanto menor nominal, mais raro, mais caro)
            if nominal <= 5:
                price = 5000
            elif nominal <= 10:
                price = 3000
            elif nominal <= 20:
                price = 2000
            elif nominal <= 50:
                price = 1000
            else:
                price = 500
            
            # Detecta categoria por nome (simplificado)
            category = "construcao"  # padrão
            name_lower = name.lower()
            if any(x in name_lower for x in ["rifle", "gun", "pistol", "shotgun"]):
                category = "armas"
            elif "ammo" in name_lower or "round" in name_lower:
                category = "municao"
            elif "mag" in name_lower:
                category = "carregadores"
            elif any(x in name_lower for x in ["optic", "suppressor", "scope"]):
                category = "acessorios"
            elif any(x in name_lower for x in ["bandage", "blood", "saline", "morphine"]):
                category = "medico"
            elif any(x in name_lower for x in ["jacket", "pants", "boots", "helmet", "vest"]):
                category = "roupas"
            elif any(x in name_lower for x in ["wheel", "battery", "spark"]):
                category = "veiculos"
            
            if category not in new_items:
                new_items[category] = {}
            
            # Usa nome do type como key (simplificado)
            item_key = name.lower().replace("_", "")
            new_items[category][item_key] = {
                "name": name,
                "price": price,
                "description": f"Nominal: {nominal}"
            }
            items_added += 1
        
        # Salva novo items.json
        save_json(ITEMS_FILE, new_items)
        
        return True, f"Sincronização concluída! {items_added} itens processados."
        
    except Exception as e:
        return False, f"Erro na sincronização: {e}"

# --- SISTEMA DE CONQUISTAS ---
ACHIEVEMENTS_DEF = {
    "first_kill": {
        "name": "🎯 Primeira Vítima",
        "description": "Mate seu primeiro jogador",
        "reward": 500,
        "check": lambda data: data.get("kills", 0) >= 1
    },
    "assassin": {
        "name": "💀 Assassino",
        "description": "Acumule 10 kills",
        "reward": 1000,
        "check": lambda data: data.get("kills", 0) >= 10
    },
    "serial_killer": {
        "name": "☠️ Serial Killer",
        "description": "Acumule 50 kills",
        "reward": 5000,
        "check": lambda data: data.get("kills", 0) >= 50
    },
    "rich": {
        "name": "💰 Rico",
        "description": "Acumule 10.000 DZ Coins",
        "reward": 0,
        "check": lambda data: data.get("balance", 0) >= 10000
    },
    "millionaire": {
        "name": "💎 Milionário",
        "description": "Acumule 100.000 DZ Coins",
        "reward": 10000,
        "check": lambda data: data.get("balance", 0) >= 100000
    },
    "shopper": {
        "name": "🛒 Comprador",
        "description": "Faça 10 compras na loja",
        "reward": 1000,
        "check": lambda data: data.get("purchases", 0) >= 10
    },
    "veteran": {
        "name": "⏰ Veterano",
        "description": "Jogue por 50 horas",
        "reward": 5000,
        "check": lambda data: data.get("hours_played", 0) >= 50
    },
    "clan_founder": {
        "name": "🛡️ Fundador de Clã",
        "description": "Crie um clã",
        "reward": 0,
        "check": lambda data: data.get("clan_created", False)
    }
}

def check_achievements(user_id):
    """Verifica e desbloqueia conquistas para um jogador"""
    uid = str(user_id)
    eco = database.get_economy(uid)
    
    if not eco:
        return []
    
    achievements = eco.get("achievements", {})
    if isinstance(achievements, str):
        try: achievements = json.loads(achievements)
        except: achievements = {}
    
    # Dados do jogador para verificação
    gamertag = eco.get("gamertag", "")
    player_data = {
        "kills": database.get_player(gamertag).get("kills", 0) if gamertag else 0,
        "balance": eco.get("balance", 0),
        "purchases": sum(1 for t in eco.get("transactions", []) if isinstance(t, dict) and t.get("type") == "purchase"),
        "hours_played": 0,  # TODO: calcular do players_db
        "clan_created": False  # TODO: verificar se é líder de clã
    }
    
    newly_unlocked = []
    
    for ach_id, ach_def in ACHIEVEMENTS_DEF.items():
        # Se já desbloqueou, pula
        if achievements.get(ach_id, {}).get("unlocked"):
            continue
        
        # Verifica condição
        if ach_def["check"](player_data):
            achievements[ach_id] = {
                "unlocked": True,
                "date": datetime.now().isoformat()
            }
            
            # Dá recompensa
            if ach_def["reward"] > 0:
                eco["balance"] = eco.get("balance", 0) + ach_def["reward"]
            
            newly_unlocked.append((ach_id, ach_def))
    
    eco["achievements"] = achievements
    database.save_economy(uid, eco)
    return newly_unlocked

# --- SISTEMA DE VÍNCULO (LINKING) ---
def get_discord_id_by_gamertag(gamertag):
    return database.get_link_by_gamertag(gamertag)

# --- SISTEMA DE CLÃS (WARS) ---
def get_user_clan(user_id):
    """Retorna a tag do clã e os dados do clã do usuário."""
    clans = database.get_all_clans()
    uid = str(user_id)
    
    for tag, data in clans.items():
        members = data.get("members", [])
        if isinstance(members, str):
            try: members = json.loads(members)
            except: members = []
            
        if data.get("leader") == uid or uid in members:
            return tag, data
    return None, None

def get_clan_by_tag(tag):
    return database.get_clan(tag.upper())

def update_war_score(killer_name, victim_name):
    """Verifica se há guerra entre os clãs e atualiza o placar."""
    killer_id = get_discord_id_by_gamertag(killer_name)
    victim_id = get_discord_id_by_gamertag(victim_name)
    
    if not killer_id or not victim_id:
        return None
        
    k_tag, k_clan = get_user_clan(killer_id)
    v_tag, v_clan = get_user_clan(victim_id)
    
    if not k_tag or not v_tag or k_tag == v_tag:
        return None
        
    # TODO: Implement War System in Database
    # For now, we skip war updates as it requires a new table or complex JSON structure
    return None

# --- SISTEMA DE STATS (KILLFEED) ---
def get_player_stats(db, player_name):
    # db argument is ignored in favor of database call, kept for compatibility if needed
    player = database.get_player(player_name)
    if not player:
        player = {
            "gamertag": player_name,
            "kills": 0, "deaths": 0, "killstreak": 0, "best_killstreak": 0,
            "last_death_time": time.time(), "first_seen": time.time(),
            "longest_shot": 0, "weapons_stats": {}, "total_playtime": 0
        }
    
    # Ensure JSON fields are parsed
    if isinstance(player.get("weapons_stats"), str):
        try: player["weapons_stats"] = json.loads(player["weapons_stats"])
        except: player["weapons_stats"] = {}
        
    return player

def update_stats_db(killer_name, victim_name, weapon=None, distance=0):
    current_time = time.time()
    
    # Matador
    killer = get_player_stats(None, killer_name)
    killer["kills"] = killer.get("kills", 0) + 1
    killer["killstreak"] = killer.get("killstreak", 0) + 1
    if killer["killstreak"] > killer.get("best_killstreak", 0):
        killer["best_killstreak"] = killer["killstreak"]
        
    # Longest Shot
    if distance > killer.get("longest_shot", 0):
        killer["longest_shot"] = int(distance)
        
    # Weapon Stats
    if weapon:
        w_key = weapon.replace('"', '').strip()
        weapons_stats = killer.get("weapons_stats", {})
        if w_key not in weapons_stats:
            weapons_stats[w_key] = 0
        weapons_stats[w_key] += 1
        killer["weapons_stats"] = weapons_stats
    
    database.save_player(killer_name, killer)
    
    # Vítima
    victim = get_player_stats(None, victim_name)
    victim["deaths"] = victim.get("deaths", 0) + 1
    victim["killstreak"] = 0
    time_alive = int(current_time - victim.get("last_death_time", current_time))
    victim["last_death_time"] = current_time
    
    database.save_player(victim_name, victim)
    
    return killer, victim, time_alive

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}h:{minutes:02d}m:{secs:02d}s"

def calculate_level(kills):
    return 1 + int(kills / 5)

def calculate_kd(kills, deaths):
    return kills if deaths == 0 else round(kills / deaths, 2)

# --- FTP & LOGS ---
def connect_ftp():
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        return ftp
    except Exception as e:
        print(f"Erro FTP: {e}")
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

# --- ANTI-SPAM DE CONSTRUÇÃO & DUPLICAÇÃO ---
spam_tracker = {} # {player_name: [timestamps]}

def check_duplication(player_name, item_name, item_id):
    """Verifica se o jogador está pegando o mesmo item (ID) repetidamente."""
    if not item_id or item_id == "Unknown": return False
    
    now = time.time()
    if player_name not in pickup_tracker:
        pickup_tracker[player_name] = []
    
    # Limpa histórico antigo (5 minutos)
    pickup_tracker[player_name] = [t for t in pickup_tracker[player_name] if now - t[1] < 300]
    
    # Adiciona atual
    pickup_tracker[player_name].append((item_id, now))
    
    # Conta quantas vezes esse ID foi pego
    count = sum(1 for i, t in pickup_tracker[player_name] if i == item_id)
    
    # Se pegou o mesmo ID mais de 2 vezes em 5 minutos -> SUSPEITO
    if count > 2:
        return True
    return False

def check_spam(player_name, item_name):
    """Verifica se o jogador está spamando itens (Lag Machine)."""
    if "fencekit" not in item_name.lower():
        return False
        
    now = time.time()
    if player_name not in spam_tracker:
        spam_tracker[player_name] = []
        
    # Limpa timestamps antigos (60 segundos)
    spam_tracker[player_name] = [t for t in spam_tracker[player_name] if now - t < 60]
    
    # Adiciona atual
    spam_tracker[player_name].append(now)
    
    # Limite: 10 kits em 1 minuto
    if len(spam_tracker[player_name]) > 10:
        return True
    return False

def check_construction(x, z, y, player_name, item_name):
    """Verifica se a construção é permitida."""
    item_lower = item_name.lower()
    
    # 1. BANIMENTO DE JARDIM (GardenPlot)
    if "gardenplot" in item_lower:
        return False, "GardenPlot"
        
    # 2. SKY BASE (Altura > 1000m)
    if y > 1000:
        return False, "SkyBase"
        
    # 3. UNDERGROUND BASE (Altura < -10m)
    if y < -10:
        return False, "UndergroundBase"
        
    # 4. PROTEÇÃO DE BASE
    alarms = load_alarms()
    for aid, data in alarms.items():
        dist = math.sqrt((x - data['x'])**2 + (z - data['z'])**2)
        if dist <= data['radius']:
            # --- REGRAS ESPECÍFICAS DE BASE ---
            
            # A. PNEUS (Glitch) -> BANIMENTO IMEDIATO
            if "wheel" in item_lower or "tire" in item_lower:
                return False, f"BannedItemBase:{item_name}"
            
            # B. SHELTER (Glitch de Visão) -> BANIMENTO IMEDIATO
            if "improvisedshelter" in item_lower:
                return False, f"BannedItemBase:{item_name}"
                
            # C. FOGUEIRA (Fireplace) -> APENAS CLÃ
            
            # Verifica se o jogador é do clã ou dono
            builder_id = get_discord_id_by_gamertag(player_name)
            
            if not builder_id:
                # Se não tem conta vinculada, é considerado INIMIGO na área protegida
                return False, f"UnauthorizedBase:{data['name']}"
            
            owner_clan, _ = get_user_clan(data['owner_id'])
            builder_clan, _ = get_user_clan(builder_id)
            
            # Se for o dono ou do mesmo clã, permite
            if data['owner_id'] == builder_id:
                return True, "Owner"
            if owner_clan and builder_clan == owner_clan:
                return True, "ClanMember"
                
            return False, f"UnauthorizedBase:{data['name']}"
            
    return True, "OK"

async def parse_log_line(line):
    line = line.strip()
    if not line or "committed suicide" in line: return None

    if "killed by Player" in line:
        try:
            parts = line.split("killed by Player")
            victim_name = parts[0].split("Player")[1].split("(")[0].strip().replace('"', '').replace("'", "")
            
            # Fix: O nome do killer vem logo após "killed by Player", não tem outro "Player"
            # parts[1] ex: ' "Bandit" (id=Unknown) with M4A1 ...'
            killer_name = parts[1].split("(")[0].strip().replace('"', '').replace("'", "")
            
            # 1. Extrai Arma (Se houver)
            weapon = "Desconhecida"
            if " with " in line:
                weapon = line.split(" with ")[1].split(" ")[0].strip()

            # 2. Calcula Distância (Se possível)
            distance = 0
            location = "Desconhecido"
            
            if "<" in line and ">" in line:
                try:
                    coords = line.split("<")[1].split(">")[0].split(",")
                    lx, lz = float(coords[0]), float(coords[2])
                    
                    # Usa Geolocalização
                    loc_name = get_location_name(lx, lz)
                    location = f"{loc_name} `({lx:.0f}, {lz:.0f})`"
                    
                    # VERIFICA ALARMES 🚨
                    triggered = check_alarms(lx, lz, f"Morte de {victim_name}")
                    for owner_id, base_name, dist in triggered:
                        try:
                            owner = await bot.fetch_user(int(owner_id))
                            alert_embed = discord.Embed(title="🚨 ALARME DE BASE DISPARADO!", color=discord.Color.red())
                            alert_embed.description = f"**Atividade detectada na base {base_name}!**\n\n💀 **Evento:** Morte de {victim_name}\n🔫 **Assassino:** {killer_name}\n📍 **Local:** {loc_name}\n📏 **Distância do Centro:** {dist:.1f}m"
                            alert_embed.set_footer(text="Sistema de Segurança BigodeTexas", icon_url=FOOTER_ICON)
                            await owner.send(embed=alert_embed)
                        except Exception as e:
                            print(f"Erro ao enviar DM de alarme: {e}")

                    # VERIFICA ZONA QUENTE 🔥
                    is_hot, count = check_hotzone(lx, lz)
                    if is_hot and count == 3: 
                        hot_embed = discord.Embed(title="🔥 ZONA QUENTE DETECTADA!", color=discord.Color.dark_orange())
                        hot_embed.description = f"**Atenção Sobreviventes!**\n\nO pau tá quebrando em **{loc_name}**!\nJá foram **{count} mortes** nos últimos 15 minutos.\nPreparem-se para o PVP! ⚔️"
                        hot_embed.set_footer(text="BigodeTexas • Radar de Conflitos", icon_url=FOOTER_ICON)
                        channel = bot.get_channel(load_json(CONFIG_FILE).get("killfeed_channel"))
                        if channel:
                            await channel.send(embed=hot_embed)

                except: pass

            # 3. Atualiza Stats (Agora com arma e distância)
            k_stats, v_stats, time_alive = update_stats_db(killer_name, victim_name, weapon, distance)

            # --- CLAN WAR UPDATE ---
            war_update = update_war_score(killer_name, victim_name)
            if war_update:
                try:
                    c1 = war_update["clan1"]
                    c2 = war_update["clan2"]
                    s1 = war_update["score"][c1]
                    s2 = war_update["score"][c2]
                    
                    war_embed = discord.Embed(title="⚔️ GUERRA DE CLÃS ATUALIZADA!", color=discord.Color.dark_red())
                    war_embed.description = f"**{c1}** vs **{c2}**\n\n💀 **Baixa Confirmada!**\nO clã **{war_update['killer_clan']}** marcou um ponto!"
                    war_embed.add_field(name="Placar", value=f"**{c1}:** {s1}\n**{c2}:** {s2}", inline=False)
                    war_embed.set_footer(text="BigodeTexas • Sistema de Guerra", icon_url=FOOTER_ICON)
                    
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("killfeed_channel"))
                    if channel:
                        await channel.send(embed=war_embed)
                except Exception as e:
                    print(f"Erro ao enviar update de guerra: {e}")
            # --- END CLAN WAR UPDATE ---

            # --- HEATMAP LOGGING ---
            try:
                if location != "Desconhecido" and "x" not in location: # Se location for nomeado, tentamos usar as coords raw se disponiveis
                     # A variavel location ja foi formatada com nome, entao precisamos das coords originais
                     # lx e lz foram definidos no bloco try anterior
                     pass
                
                # Se tivermos lx e lz do bloco anterior (linha 760), salvamos
                # Precisamos garantir que lx e lz estao no escopo.
                # O bloco try onde lx e lz sao definidos esta dentro do if "<" in line...
                # Vamos refatorar levemente para garantir que temos as coords.
                pass
            except: pass

            # Refatorando a logica de extracao para persistir dados do heatmap
            heatmap_coords = None
            if "<" in line and ">" in line:
                try:
                    coords = line.split("<")[1].split(">")[0].split(",")
                    lx, lz = float(coords[0]), float(coords[2])
                    heatmap_coords = (lx, lz)
                except: pass
            
            discord_id = get_discord_id_by_gamertag(killer_name)
            reward_msg = ""
            total_reward = KILL_REWARD
            
            # Verifica BOUNTY (Procurado)
            bounties = load_bounties()
            victim_lower = victim_name.lower()
            
            if victim_lower in bounties:
                bounty_val = bounties[victim_lower]["amount"]
                total_reward += bounty_val
                reward_msg += f"\n🤠 **RECOMPENSA COLETADA:** +{bounty_val}!"
                # Remove a recompensa
                del bounties[victim_lower]
                save_bounties(bounties)
            
            if discord_id:
                update_balance(discord_id, total_reward, "kill", f"Kill: {victim_name}")
                reward_msg += f"\n💰 **Total Ganho:** +{total_reward} DZ Coins"
                
                # Verifica conquistas
                new_achievements = check_achievements(discord_id)
                if new_achievements:
                    for ach_id, ach_def in new_achievements:
                        reward_msg += f"\n🏆 **CONQUISTA DESBLOQUEADA:** {ach_def['name']}!"
                        if ach_def['reward'] > 0:
                            reward_msg += f" (+{ach_def['reward']} DZ Coins)"

            # TEMA BIGODE TEXAS 🤠
            embed = discord.Embed(title="🤠 KILLFEED TEXAS", color=discord.Color.orange())
            
            # Assassino
            embed.add_field(
                name="🔫 Pistoleiro (Assassino)", 
                value=f"**{killer_name}**\n⭐ Nível: {calculate_level(k_stats['kills'])}\n🎯 K/D: {calculate_kd(k_stats['kills'], k_stats['deaths'])}\n🔥 Série: {k_stats['killstreak']}\n📏 Longest: {k_stats.get('longest_shot', 0)}m{reward_msg}", 
                inline=True
            )
            
            # Vítima
            embed.add_field(
                name="⚰️ Finado (Vítima)", 
                value=f"**{victim_name}**\n⭐ Nível: {calculate_level(v_stats['kills'])}\n⏳ Viveu: {format_time(time_alive)}", 
                inline=True
            )
            
            # Detalhes
            embed.add_field(name="🌵 Detalhes do Crime", value=f"🛠️ Arma: `{weapon}`\n📍 Local: `{location}`", inline=False)
            
            embed.set_thumbnail(url="https://i.imgur.com/S71j4qO.png") # Ícone de caveira/wanted
            embed.set_footer(text=f"BigodeTexas • {datetime.now().strftime('%H:%M')} • O Xerife está de olho 👀", icon_url=FOOTER_ICON)
            
            return embed
        except Exception as e:
            print(f"Erro parse kill: {e}")
            return None

    elif "died" in line and "Player" in line:
        try:
            victim_name = line.split("Player")[1].split("died")[0].split("(")[0].strip().replace('"', '').replace("'", "")
            # Atualiza DB (morte natural)
            db = load_json(PLAYERS_DB_FILE)
            victim = get_player_stats(db, victim_name)
            victim["deaths"] += 1
            victim["killstreak"] = 0
            victim["last_death_time"] = time.time()
            save_json(PLAYERS_DB_FILE, db)
            
            embed = discord.Embed(description=f"💀 **{victim_name}** morreu.", color=discord.Color.dark_grey())
            return embed
        except: return None
        
    elif "placed" in line and "at <" in line:
        try:
            # Ex: Player "Survivor" (id=...) placed "GardenPlot" at <123, 456, 789>
            parts = line.split(" placed ")
            player_part = parts[0]
            item_part = parts[1]
            
            player_name = player_part.split('Player "')[1].split('"')[0]
            item_name = item_part.split('"')[1]
            
            coords = item_part.split("at <")[1].split(">")[0].split(",")
            x, z = float(coords[0]), float(coords[2])
            y = float(coords[1]) # Altura
            
            # 1. CHECK SPAM (Lag Machine)
            if check_spam(player_name, item_name):
                print(f"BANINDO {player_name} por SPAM de Construção (Lag Machine)!")
                channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                if channel:
                    await channel.send(f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por Spam de Construção (Lag Machine)!")
                ban_player(player_name, "Spam de Construcao/Lag Machine")
                return None

            # 2. CHECK CONSTRUCTION (Regras Gerais)
            allowed, reason = check_construction(x, z, y, player_name, item_name)
            
            if not allowed:
                if reason == "GardenPlot":
                    # AÇÃO: BANIR JOGADOR
                    print(f"BANINDO {player_name} por plantar GardenPlot!")
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                    if channel:
                        await channel.send(f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por plantar GardenPlot (Proibido)!")
                    
                    # Executa Banimento Real
                    ban_player(player_name, "GardenPlot Proibido")
                
                elif reason == "SkyBase":
                    print(f"BANINDO {player_name} por Sky Base!")
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                    if channel:
                        await channel.send(f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por construir Sky Base (Altura > 1000m)!")
                    ban_player(player_name, "Sky Base Detectada")

                elif reason == "UndergroundBase":
                    print(f"BANINDO {player_name} por Base Subterrânea!")
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                    if channel:
                        await channel.send(f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por construir Base Subterrânea!")
                    ban_player(player_name, "Underground Base Detectada")
                    
                elif reason.startswith("BannedItemBase"):
                    # AÇÃO: BANIR JOGADOR (Glitch de Pneu/Shelter)
                    item_banned = reason.split(":")[1]
                    print(f"BANINDO {player_name} por item proibido em Base: {item_banned}!")
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                    if channel:
                        await channel.send(f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por usar **{item_banned}** em área de Base (Anti-Glitch)!")
                    
                    # Executa Banimento Real
                    ban_player(player_name, f"Glitch Item em Base: {item_banned}")
                
                elif reason.startswith("UnauthorizedBase"):
                    base_name = reason.split(":")[1]
                    print(f"ALERTA: Construção ilegal de {player_name} na base {base_name}")
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("alarm_channel"))
                    if channel:
                        await channel.send(f"🚨 **ALERTA DE INVASÃO**\n**{player_name}** tentou colocar **{item_name}** na área protegida da base **{base_name}**!")
                    
        except Exception as e:
            print(f"Erro parse placement: {e}")

    # --- DETECÇÃO DE DUPLICAÇÃO (PICKED UP) ---
    elif " picked up " in line:
        try:
            # Ex: Player "Survivor" (id=Unknown) picked up "M4A1" (id=12345)
            parts = line.split(" picked up ")
            player_part = parts[0]
            item_part = parts[1]
            
            player_name = player_part.split('Player "')[1].split('"')[0]
            item_name = item_part.split('"')[1]
            
            item_id = None
            if "(id=" in item_part:
                item_id = item_part.split("(id=")[1].split(")")[0]
            
            if check_duplication(player_name, item_name, item_id):
                print(f"BANINDO {player_name} por Duplicação de Item (ID: {item_id})!")
                channel = bot.get_channel(load_json(CONFIG_FILE).get("ban_channel"))
                if channel:
                    await channel.send(f"🚫 **BANIMENTO AUTOMÁTICO**\nO jogador **{player_name}** foi banido por Duplicação de Item (Duping)!\nItem: {item_name} (ID: {item_id})")
                ban_player(player_name, f"Duplicação de Item: {item_name}")
                
        except Exception as e:
            print(f"Erro parse pickup: {e}")

    # --- DETECÇÃO DE LOGIN/LOGOUT (SALÁRIO) ---
    elif " is connected" in line:
        try:
            # Ex: Player "Survivor" is connected
            player_name = line.split('Player "')[1].split('"')[0]
            
            # 1. Registra Login
            active_sessions[player_name] = time.time()
            print(f"[LOGIN] Detectado: {player_name}")
            
            # 2. Daily Automático
            discord_id = get_discord_id_by_gamertag(player_name)
            if discord_id:
                eco = load_json(ECONOMY_FILE)
                uid = str(discord_id)
                
                if uid not in eco: eco[uid] = {"balance": 0, "last_daily": None}
                
                last = eco[uid].get("last_daily")
                should_pay = True
                if last:
                    last_date = datetime.fromisoformat(last)
                    if datetime.now() - last_date < timedelta(hours=24):
                        should_pay = False
                
                if should_pay:
                    eco[uid]["balance"] += DAILY_BONUS
                    eco[uid]["last_daily"] = datetime.now().isoformat()
                    save_json(ECONOMY_FILE, eco)
                    
                    channel = bot.get_channel(load_json(CONFIG_FILE).get("salary_channel"))
                    if channel:
                        await channel.send(f"🌞 **BÔNUS DIÁRIO!**\n**{player_name}** conectou e ganhou **{DAILY_BONUS} DZ Coins**!")

        except Exception as e:
            print(f"Erro parse login: {e}")
            
    elif " has been disconnected" in line:
        try:
            # Ex: Player "Survivor" has been disconnected
            player_name = line.split('Player "')[1].split('"')[0]
            
            if player_name in active_sessions:
                login_time = active_sessions.pop(player_name)
                duration_seconds = time.time() - login_time
                hours_played = duration_seconds / 3600
                
                # Pagamento Proporcional (Mínimo 10 minutos para ganhar algo)
                if duration_seconds > 600:
                    salary = int(hours_played * HOURLY_SALARY)
                    
                    # Formata tempo
                    h = int(hours_played)
                    m = int((duration_seconds % 3600) // 60)
                    
                    discord_id = get_discord_id_by_gamertag(player_name)
                    if discord_id and salary > 0:
                        update_balance(discord_id, salary, "salary", f"Tempo jogado: {h}h {m}m")
                        
                        msg = f"💸 **SALÁRIO RECEBIDO!**\n**{player_name}** jogou por {h}h {m}m e ganhou **{salary} DZ Coins**."
                        
                        # Bônus de 10 Horas
                        if hours_played >= 10:
                            update_balance(discord_id, BONUS_10H, "salary", "Bônus Maratonista +10h")
                            msg += f"\n🏆 **MARATONISTA!** Bônus de {BONUS_10H} por jogar +10h direto!"
                            
                        channel = bot.get_channel(load_json(CONFIG_FILE).get("salary_channel"))
                        if channel:
                            await channel.send(msg)
                else:
                    print(f"Sessão curta de {player_name}: {duration_seconds:.0f}s (Sem pagamento)")
                    
        except Exception as e:
            print(f"Erro parse logout: {e}")

    return None

def ban_player(gamertag, reason="Banido pelo Bot"):
    """Adiciona o jogador ao arquivo ban.txt no servidor via FTP."""
    local_file = "ban.txt"
    remote_path = "/ban.txt" # Tenta na raiz primeiro, ou /dayzxb/config/ban.txt
    
    try:
        ftp = connect_ftp()
        if not ftp: return
        
        # 1. Baixa o ban.txt atual (se existir)
        current_bans = ""
        try:
            bio = io.BytesIO()
            ftp.retrbinary(f"RETR {remote_path}", bio.write)
            current_bans = bio.getvalue().decode('utf-8', errors='ignore')
        except:
            print("Arquivo ban.txt não encontrado, criando novo.")
            
        # 2. Verifica se já está banido
        if gamertag in current_bans:
            print(f"{gamertag} já está na lista de banimento.")
            ftp.quit()
            return

        # 3. Adiciona o novo ban
        # Formato: Gamertag // Motivo
        new_entry = f"{gamertag} // {reason}\n"
        current_bans += new_entry
        
        # 4. Salva e Upload
        with open(local_file, 'w', encoding='utf-8') as f:
            f.write(current_bans)
            
        with open(local_file, 'rb') as f:
            ftp.storbinary(f"STOR {remote_path}", f)
            
        print(f"✅ Jogador {gamertag} adicionado ao ban.txt com sucesso.")
        ftp.quit()
        
    except Exception as e:
        print(f"Erro ao banir jogador: {e}")

# --- PERSISTÊNCIA DE ESTADO (MEMÓRIA) ---
STATE_FILE = "bot_state.json"

def load_state():
    return load_json(STATE_FILE)

def save_state(file_name, lines_read):
    if not save_data_loop.is_running():
        print("[LOOP] Iniciando save_data_loop...")
        save_data_loop.start()
    
    if not backup_loop.is_running():
        print("[LOOP] Iniciando backup_loop...")
        backup_loop.start()
    
    print("[READY] Todos os sistemas operacionais! 🚀\n")

# --- TASKS (LOOP) ---
@tasks.loop(seconds=30)
async def killfeed_loop():
    global last_read_lines, current_log_file
    
    config = load_json(CONFIG_FILE)
    channel_id = config.get("killfeed_channel")
    if not channel_id: return

    channel = bot.get_channel(channel_id)
    if not channel: return

    ftp = connect_ftp()
    if not ftp: return

    try:
        # Tenta carregar estado se não tivermos um arquivo definido na memória
        if not current_log_file:
            state = load_state()
            if state:
                saved_file = state.get("current_log_file")
                saved_lines = state.get("last_read_lines", 0)
                
                # Verifica se o arquivo salvo ainda existe no servidor
                # (Simplificação: assume que existe se foi salvo recentemente, 
                # mas o ideal seria checar. Se falhar o RETR abaixo, vai pro except)
                current_log_file = saved_file
                last_read_lines = saved_lines
                print(f"Estado carregado: {current_log_file} (Linha {last_read_lines})")

        if not current_log_file:
            current_log_file = find_latest_adm_log(ftp)
            if current_log_file:
                # Primeira leitura: só pega o tamanho
                bio = io.BytesIO()
                ftp.retrbinary(f"RETR {current_log_file}", bio.write)
                last_read_lines = len(bio.getvalue().decode('utf-8', errors='ignore').split('\n'))
                print(f"Log inicial: {current_log_file} ({last_read_lines} linhas)")
                save_state(current_log_file, last_read_lines)
        else:
            bio = io.BytesIO()
            ftp.retrbinary(f"RETR {current_log_file}", bio.write)
            content = bio.getvalue().decode('utf-8', errors='ignore')
            lines = content.split('\n')
            
            if len(lines) > last_read_lines:
                new_lines = lines[last_read_lines:]
                print(f"Novas linhas: {len(new_lines)}")
                for line in new_lines:
                    embed = await parse_log_line(line)
                    if embed:
                        await channel.send(embed=embed)
                last_read_lines = len(lines)
                save_state(current_log_file, last_read_lines)
                
            elif len(lines) < last_read_lines:
                current_log_file = "" # Log rotacionou
                last_read_lines = 0
                save_state("", 0)

    except Exception as e:
        print(f"Erro Loop: {e}")
        # Se der erro de arquivo não encontrado (ex: log antigo deletado), reseta
        if "550" in str(e):
            print("Arquivo de log salvo não existe mais. Resetando estado.")
            current_log_file = ""
            last_read_lines = 0
            save_state("", 0)
    
    try: ftp.quit()
    except: pass

@tasks.loop(minutes=1)
async def save_data_loop():
    """Salva periodicamente todos os dados críticos para garantir persistência."""
    # Como usamos save_json a cada operação crítica, os arquivos já devem estar atualizados.
    # Mas isso serve como redundância e para garantir flushing se mudarmos para cache em memória.
    # Por enquanto, apenas imprime um log de checkpoint.
    print(f"[AUTOSAVE] Dados verificados em {datetime.now().strftime('%H:%M:%S')}")
    # Futuramente: Se migrarmos para DB em memória, aqui chamamos save_all()

# --- LOOP DE BACKUP AUTOMÁTICO ---
@tasks.loop(hours=1)
async def backup_loop():
    """Cria backup automático dos arquivos críticos a cada hora"""
    critical_files = [
        ECONOMY_FILE,
        PLAYERS_DB_FILE,
        LINKS_FILE,
        CLANS_FILE,
        CONFIG_FILE,
        "bot_state.json"
    ]
    
    print(f"[BACKUP] Iniciando backup automático...")
    backup_manager.backup_all(critical_files)
    print(f"[BACKUP] Backup concluído em {datetime.now().strftime('%H:%M:%S')}")

# --- AGENDADOR DE RAID ---
@tasks.loop(minutes=1)
async def raid_scheduler():
    # Horário de Brasília (UTC-3)
    # Ajuste conforme o fuso horário da máquina onde o bot roda.
    # Se a máquina for UTC-6, adicionamos 3 horas.
    # Para garantir, vamos usar UTC e subtrair 3.
    utc_now = datetime.now(timezone.utc)
    br_time = utc_now - timedelta(hours=3)
    
    weekday = br_time.weekday() # 5 = Sábado, 6 = Domingo
    hour = br_time.hour
    minute = br_time.minute
    
    # Sábado (5) e Domingo (6)
    if weekday in [5, 6]:
        # 1. Preparação do Raid (20:55)
        if hour == 20 and minute == 55:
            print("⏰ Preparando Raid! Enviando globals_raid.xml...")
            if upload_globals("globals_raid.xml"):
                channel = bot.get_channel(load_json(CONFIG_FILE).get("killfeed_channel"))
                if channel:
                    await channel.send("⚠️ **ATENÇÃO:** O Raid será liberado no próximo reinício (21:00)!")

        # 2. Início do Raid (21:00) - RESTART
        if hour == 21 and minute == 0:
            print("⏰ HORA DO RAID! Reiniciando servidor...")
            success, msg = await restart_server()
            channel = bot.get_channel(load_json(CONFIG_FILE).get("killfeed_channel"))
            if channel:
                if success:
                    await channel.send("🚨 **INICIANDO RAID!** O servidor está reiniciando para liberar a destruição! ⚔️")
                else:
                    await channel.send(f"❌ **ERRO:** Falha ao reiniciar o servidor: {msg}")

        # 3. Preparação do Fim (22:55)
        if hour == 22 and minute == 55:
            print("⏰ Encerrando Raid! Enviando globals_safe.xml...")
            if upload_globals("globals_safe.xml"):
                channel = bot.get_channel(load_json(CONFIG_FILE).get("killfeed_channel"))
                if channel:
                    await channel.send("🛡️ **ATENÇÃO:** O Raid será desativado no próximo reinício (23:00)!")

        # 4. Fim do Raid (23:00) - RESTART
        if hour == 23 and minute == 0:
            print("⏰ FIM DO RAID! Reiniciando servidor...")
            success, msg = await restart_server()
            channel = bot.get_channel(load_json(CONFIG_FILE).get("killfeed_channel"))
            if channel:
                if success:
                    await channel.send("🛡️ **RAID ENCERRADO!** O servidor está reiniciando e as bases estão seguras novamente.")
                else:
                    await channel.send(f"❌ **ERRO:** Falha ao reiniciar o servidor: {msg}")

def upload_globals(local_filename):
    try:
        ftp = connect_ftp()
        if not ftp: return False
        
        # Caminho do arquivo no servidor (Tenta achar)
        remote_path = "/dayzxb_missions/dayzOffline.chernarusplus/db/globals.xml"
        
        # Tenta enviar
        try:
            with open(local_filename, 'rb') as f:
                ftp.storbinary(f"STOR {remote_path}", f)
            print(f"Upload de {local_filename} concluído com sucesso.")
            ftp.quit()
            return True
        except Exception as e:
            print(f"Erro ao enviar {local_filename}: {e}")
            ftp.quit()
            return False
            
    except Exception as e:
        print(f"Erro global no upload: {e}")
        return False

@bot.command()
@require_admin_password()
async def set_killfeed(ctx):
    config = load_json(CONFIG_FILE)
    config["killfeed_channel"] = ctx.channel.id
    save_json(CONFIG_FILE, config)
    await ctx.send(f"✅ Canal de Killfeed definido para: {ctx.channel.mention}")

@bot.command()
@require_admin_password()
async def restart(ctx):
    """(Admin) Reinicia o servidor DayZ imediatamente."""
    await ctx.send("⏳ **Enviando comando de restart para a Nitrado...**")
    success, msg = await restart_server()
    if success:
        await ctx.send("✅ **Servidor reiniciando!** Aguarde alguns minutos para voltar.")
    else:
        await ctx.send(f"❌ **Falha ao reiniciar:** {msg}")

@bot.command()
@rate_limit()
async def registrar(ctx, gamertag: str):
    """Vincula sua Gamertag do Xbox ao Discord. Ex: !registrar DarkJoel"""
    # Validar gamertag
    if not input_validator.validate_gamertag(gamertag):
        security_logger.log_invalid_input(ctx.author.id, f"Invalid gamertag: {gamertag}")
        await ctx.send("❌ **Gamertag inválida!** Use apenas letras, números, _ e - (3-20 caracteres).")
        return
    
    links = load_json(LINKS_FILE)
    
    # Verifica se já existe
    for gt, did in links.items():
        if did == ctx.author.id:
            await ctx.send(f"❌ Você já registrou a Gamertag: **{gt}**")
            return
        if gt.lower() == gamertag.lower():
            await ctx.send(f"❌ A Gamertag **{gamertag}** já está em uso por outro usuário.")
            return

    links[gamertag] = ctx.author.id
    save_json(LINKS_FILE, links)
    
    # Atualiza gamertag no economy.json
    eco = load_json(ECONOMY_FILE)
    uid = str(ctx.author.id)
    if uid not in eco: eco[uid] = {"balance": 0, "last_daily": None, "inventory": {}, "transactions": [], "gamertag": None}
    eco[uid]["gamertag"] = gamertag
    save_json(ECONOMY_FILE, eco)
    
    await ctx.send(f"✅ **Sucesso!** Gamertag **{gamertag}** vinculada a {ctx.author.mention}.\nAgora você ganhará DZ Coins por kills!")

@bot.command()
async def saldo(ctx):
    bal = get_balance(ctx.author.id)
    eco = load_json(ECONOMY_FILE)
    uid = str(ctx.author.id)
    gamertag = eco.get(uid, {}).get("gamertag", "Não vinculada")
    
    embed = discord.Embed(title="💰 Saldo", color=discord.Color.gold())
    embed.add_field(name="Usuário", value=ctx.author.mention, inline=True)
    embed.add_field(name="Gamertag", value=gamertag, inline=True)
    embed.add_field(name="DZ Coins", value=f"**{bal}** 💵", inline=False)
    embed.set_footer(text="BigodeTexas • Sistema Bancário", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

@bot.command()
async def daily(ctx):
    eco = load_json(ECONOMY_FILE)
    user_id = str(ctx.author.id)
    if user_id not in eco: eco[user_id] = {"balance": 0, "last_daily": None}
    
    last = eco[user_id].get("last_daily")
    if last:
        last_date = datetime.fromisoformat(last)
        if datetime.now() - last_date < timedelta(hours=24):
            await ctx.send("⏳ Você já pegou hoje.")
            return

    reward = random.randint(100, 500)
    eco[user_id]["balance"] += reward
    eco[user_id]["last_daily"] = datetime.now().isoformat()
    save_json(ECONOMY_FILE, eco)
    await ctx.send(f"🎁 Ganhou **{reward} DZ Coins**!")

@bot.command()
async def loja(ctx, categoria: str = None):
    items_data = load_json(ITEMS_FILE)
    
    # Emojis por categoria
    category_emojis = {
        "armas": "🔫",
        "municao": "🎯",
        "carregadores": "📦",
        "acessorios": "🔧",
        "construcao": "🏗️",
        "ferramentas": "🛠️",
        "medico": "💊",
        "roupas": "👕",
        "veiculos": "🚗"
    }
    
    if not categoria:
        msg = "🛒 **LOJA BIGODE TEXAS** 🛒\n\n"
        msg += "Use `!loja <categoria>` para ver os itens.\n\n"
        msg += "**Categorias Disponíveis:**\n"
        for cat in items_data.keys():
            emoji = category_emojis.get(cat, "📦")
            msg += f"{emoji} **{cat.capitalize()}**\n"
        
        await ctx.send(msg)
    else:
        cat = categoria.lower()
        if cat not in items_data:
            await ctx.send("❌ Categoria não encontrada, parceiro.")
            return
        
        emoji = category_emojis.get(cat, "📦")
        items_list = list(items_data[cat].items())
        
        # Usa paginação interativa
        paginator = ShopPaginator(items_list, cat, emoji, items_per_page=5)
        await ctx.send(embed=paginator.get_embed(), view=paginator)

@bot.command()
async def comprar(ctx, item_key: str):
    item = find_item_by_key(item_key.lower())
    if not item:
        await ctx.send("❌ Item não encontrado.")
        return
    
    price = item["price"]
    bal = get_balance(ctx.author.id)
    if bal < price:
        await ctx.send(f"❌ Falta dinheiro. Custa {price}, você tem {bal}.")
        return

    # Pergunta as coordenadas
    await ctx.send(f"📍 **Onde você quer receber o {item['name']}?**\nDigite as coordenadas no formato: `X Z` (Exemplo: `4500 10200`)\nOu digite `cancelar`.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=60.0)
        
        if msg.content.lower() == 'cancelar':
            await ctx.send("🚫 Compra cancelada.")
            return

        coords_text = msg.content.strip()
        # Validação simples de coordenadas
        if not re.match(r'^[\d\.\-]+\s+[\d\.\-]+$', coords_text) and not re.match(r'^[\d\.\-]+\s+[\d\.\-]+\s+[\d\.\-]+$', coords_text):
             await ctx.send("⚠️ Formato inválido! Use apenas números e espaços. Ex: `4500 10200`. Compra cancelada.")
             return

        # Processa a compra
        update_balance(ctx.author.id, -price, "purchase", f"Compra: {item['name']}")
        add_to_inventory(ctx.author.id, item_key.lower(), item["name"])
        
        # Adiciona à fila de entrega
        if upload_spawn_request(item["name"], coords_text):
            await ctx.send(f"✅ **Compra realizada!**\nItem: {item['name']}\nLocal: {coords_text}\nO drone do Bigode logo deixará seu item lá! 🚁")
        else:
            await ctx.send(f"✅ Compra realizada, mas **erro ao agendar entrega**. O item está no seu inventário virtual. Contate o Admin.")

    except asyncio.TimeoutError:
        await ctx.send("⏰ Tempo esgotado. Compra cancelada.")

def upload_spawn_request(item_name, coords):
    """Gera o JSON e envia para o FTP."""
    spawn_data = {
        "items": [
            {
                "name": item_name, # Precisa ser o ClassName do DayZ (ex: M4A1), não o nome bonito
                "coords": coords
            }
        ]
    }
    
    # Nota: Se já houver um arquivo lá, deveríamos ler e adicionar, 
    # mas para simplificar vamos sobrescrever ou anexar se possível.
    # O script do servidor deleta o arquivo após ler, então o risco de conflito é baixo se o tráfego for baixo.
    
    filename = "spawns.json"
    try:
        with open(filename, 'w') as f:
            json.dump(spawn_data, f)
            
        ftp = connect_ftp()
        if ftp:
            # Tenta entrar na pasta do profile encontrada: /dayzxb/config
            try: 
                ftp.cwd("/dayzxb/config")
            except:
                # Se falhar, tenta SC ou raiz como fallback
                try: ftp.cwd("SC")
                except: pass
            
            with open(filename, 'rb') as f:
                ftp.storbinary(f"STOR {filename}", f)
            ftp.quit()
            return True
    except Exception as e:
        print(f"Erro upload spawn: {e}")
        return False
    return False

@bot.command()
async def inventario(ctx):
    eco = load_json(ECONOMY_FILE)
    uid = str(ctx.author.id)
    if uid not in eco or "inventory" not in eco[uid] or not eco[uid]["inventory"]:
        await ctx.send("🎒 Mochila vazia.")
        return
    
    msg = f"🎒 **Mochila de {ctx.author.name}**\n\n"
    for k, v in eco[uid]["inventory"].items():
        msg += f"📦 **{v['name']}**: {v['count']}x\n"
    await ctx.send(msg)

@bot.command()
async def extrato(ctx, limite: int = 10):
    """Mostra o histórico de transações. Ex: !extrato 20"""
    eco = load_json(ECONOMY_FILE)
    uid = str(ctx.author.id)
    
    if uid not in eco or "transactions" not in eco[uid] or not eco[uid]["transactions"]:
        await ctx.send("📜 Você ainda não tem transações registradas.")
        return
    
    transactions = eco[uid]["transactions"][-limite:]
    transactions.reverse()
    
    embed = discord.Embed(title="📜 Extrato Bancário", color=discord.Color.blue())
    embed.description = f"Últimas {len(transactions)} transações:"
    
    for i, t in enumerate(transactions, 1):
        amount_str = f"+{t['amount']}" if t['amount'] > 0 else str(t['amount'])
        timestamp = datetime.fromisoformat(t['timestamp']).strftime('%d/%m %H:%M')
        
        type_emoji = {
            "kill": "🔫",
            "purchase": "🛒",
            "daily": "🎁",
            "transfer_in": "📥",
            "transfer_out": "📤",
            "salary": "💼"
        }.get(t['type'], "💰")
        
        embed.add_field(
            name=f"{type_emoji} {t['type'].capitalize()}",
            value=f"{amount_str} DZ Coins\n{t.get('details', '')}\n`{timestamp}` • Saldo: {t['balance_after']}",
            inline=False
        )
    
@bot.command()
async def transferir(ctx, destinatario: discord.Member, valor: int):
    """Transfere DZ Coins para outro jogador. Ex: !transferir @Amigo 500"""
    if valor <= 0:
        await ctx.send("❌ Valor inválido.")
        return
        
    if destinatario.id == ctx.author.id:
        await ctx.send("❌ Você não pode transferir para si mesmo.")
        return
    
    bal = get_balance(ctx.author.id)
    if bal < valor:
        await ctx.send(f"❌ Saldo insuficiente. Você tem {bal} DZ Coins.")
        return
    
    # Realiza transferência
    update_balance(ctx.author.id, -valor, "transfer_out", f"Transferido para {destinatario.name}")
    update_balance(destinatario.id, valor, "transfer_in", f"Recebido de {ctx.author.name}")
    
    embed = discord.Embed(title="💸 Transferência Realizada", color=discord.Color.green())
    embed.add_field(name="De", value=ctx.author.mention, inline=True)
    embed.add_field(name="Para", value=destinatario.mention, inline=True)
    embed.add_field(name="Valor", value=f"**{valor} DZ Coins**", inline=False)
    embed.set_footer(text="BigodeTexas • Banco", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

@bot.command()
@require_admin_password()
async def desvincular(ctx, gamertag: str):
    """(Admin) Remove vinculação de uma gamertag. Ex: !desvincular PlayerName"""
    links = load_json(LINKS_FILE)
    
    if gamertag not in links:
        await ctx.send(f"❌ Gamertag **{gamertag}** não está vinculada.")
        return
    
    user_id = links[gamertag]
    del links[gamertag]
    save_json(LINKS_FILE, links)
    
    # Remove do economy.json também
    eco = load_json(ECONOMY_FILE)
    uid = str(user_id)
    if uid in eco:
        eco[uid]["gamertag"] = None
        save_json(ECONOMY_FILE, eco)
    
    await ctx.send(f"✅ Gamertag **{gamertag}** desvinculada com sucesso.")

@bot.command()
async def favoritar(ctx, item_key: str):
    """Adiciona um item aos favoritos. Ex: !favoritar m4a1"""
    item = find_item_by_key(item_key.lower())
    if not item:
        await ctx.send("❌ Item não encontrado.")
        return
    
    eco = load_json(ECONOMY_FILE)
    uid = str(ctx.author.id)
    if uid not in eco:
        eco[uid] = {"balance": 0, "last_daily": None, "inventory": {}, "transactions": [], "gamertag": None, "favorites": []}
    
    if "favorites" not in eco[uid]:
        eco[uid]["favorites"] = []
    
    # Limite de 10 favoritos
    if len(eco[uid]["favorites"]) >= 10:
        await ctx.send("❌ Você já tem 10 favoritos. Use `!desfavoritar <codigo>` para remover algum.")
        return
    
    # Verifica se já está favoritado
    if item_key.lower() in eco[uid]["favorites"]:
        await ctx.send(f"⭐ **{item['name']}** já está nos seus favoritos!")
        return
    
    eco[uid]["favorites"].append(item_key.lower())
    save_json(ECONOMY_FILE, eco)
    await ctx.send(f"⭐ **{item['name']}** adicionado aos favoritos!")

@bot.command()
async def favoritos(ctx):
    """Lista seus itens favoritos."""
    eco = load_json(ECONOMY_FILE)
    uid = str(ctx.author.id)
    
    if uid not in eco or "favorites" not in eco[uid] or not eco[uid]["favorites"]:
        await ctx.send("💫 Você ainda não tem favoritos. Use `!favoritar <codigo>` para adicionar!")
        return
    
    embed = discord.Embed(title="⭐ Seus Favoritos", color=discord.Color.gold())
    embed.description = "Use `!comprar <codigo>` para adquirir.\n\n"
    
    for i, fav_key in enumerate(eco[uid]["favorites"], 1):
        item = find_item_by_key(fav_key)
        if item:
            embed.add_field(
                name=f"{i}. {item['name']} (`{fav_key}`)",
                value=f"💰 {item['price']} DZ Coins\n_{item.get('description', 'Sem descrição')}_",
                inline=False
            )
    
    embed.set_footer(text="BigodeTexas • Favoritos", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

@bot.command()
async def desfavoritar(ctx, item_key: str):
    """Remove um item dos favoritos. Ex: !desfavoritar m4a1"""
    eco = load_json(ECONOMY_FILE)
    uid = str(ctx.author.id)
    
    if uid not in eco or "favorites" not in eco[uid] or item_key.lower() not in eco[uid]["favorites"]:
        await ctx.send("❌ Este item não está nos seus favoritos.")
        return
    
    eco[uid]["favorites"].remove(item_key.lower())
    save_json(ECONOMY_FILE, eco)
    
    item = find_item_by_key(item_key.lower())
    item_name = item['name'] if item else item_key
    await ctx.send(f"🗑️ **{item_name}** removido dos favoritos.")

@bot.command()
@require_admin_password()
async def atualizar_loja(ctx):
    """(Admin) Sincroniza a loja com types.xml do servidor"""
    await ctx.send("⏳ **Sincronizando loja com o servidor...**")
    
    # Executa em thread separada para não bloquear
    loop = asyncio.get_event_loop()
    success, message = await loop.run_in_executor(None, sync_types_from_server)
    
    if success:
        await ctx.send(f"✅ {message}")
    else:
        await ctx.send(f"❌ {message}")

@bot.command()
async def conquistas(ctx):
    """Lista todas as conquistas disponíveis e seu progresso"""
    eco = load_json(ECONOMY_FILE)
    uid = str(ctx.author.id)
    
    if uid not in eco:
        eco[uid] = {"balance": 0, "achievements": {}}
    
    if "achievements" not in eco[uid]:
        eco[uid]["achievements"] = {}
    
    embed = discord.Embed(title="🏆 CONQUISTAS", color=discord.Color.gold())
    embed.description = "Desbloqueie conquistas para ganhar recompensas!\n\n"
    
    unlocked_count = 0
    for ach_id, ach_def in ACHIEVEMENTS_DEF.items():
        is_unlocked = eco[uid]["achievements"].get(ach_id, {}).get("unlocked", False)
        
        if is_unlocked:
            unlocked_count += 1
            status = "✅ **DESBLOQUEADO**"
            date = eco[uid]["achievements"][ach_id].get("date", "")
            if date:
                date_obj = datetime.fromisoformat(date)
                status += f" ({date_obj.strftime('%d/%m/%Y')})"
        else:
            status = "🔒 Bloqueado"
        
        reward_text = f"+{ach_def['reward']} DZ Coins" if ach_def['reward'] > 0 else "Badge"
        
        embed.add_field(
            name=f"{ach_def['name']}",
            value=f"{ach_def['description']}\n💰 {reward_text}\n{status}",
            inline=False
        )
    
    embed.set_footer(text=f"Progresso: {unlocked_count}/{len(ACHIEVEMENTS_DEF)} • BigodeTexas", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

@bot.command()
async def perfil(ctx, usuario: discord.Member = None):
    """Mostra o perfil completo de um jogador"""
    target = usuario or ctx.author
    eco = load_json(ECONOMY_FILE)
    uid = str(target.id)
    
    if uid not in eco:
        await ctx.send(f"❌ {target.name} ainda não está registrado.")
        return
    
    # Dados do jogador
    balance = eco[uid].get("balance", 0)
    gamertag = eco[uid].get("gamertag", "Não vinculada")
    achievements = eco[uid].get("achievements", {})
    
    # Stats do jogo
    stats = get_player_stats(gamertag) if gamertag != "Não vinculada" else {}
    kills = stats.get("kills", 0)
    deaths = stats.get("deaths", 0)
    kd = calculate_kd(kills, deaths)
    
    # Conquistas desbloqueadas
    unlocked = sum(1 for a in achievements.values() if a.get("unlocked"))
    
    embed = discord.Embed(title=f"👤 Perfil de {target.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=target.avatar.url if target.avatar else None)
    
    embed.add_field(name="🎮 Gamertag", value=gamertag, inline=True)
    embed.add_field(name="💰 DZ Coins", value=f"{balance:,}", inline=True)
    embed.add_field(name="🏆 Conquistas", value=f"{unlocked}/{len(ACHIEVEMENTS_DEF)}", inline=True)
    
    if kills > 0 or deaths > 0:
        embed.add_field(name="💀 Kills", value=str(kills), inline=True)
        embed.add_field(name="☠️ Deaths", value=str(deaths), inline=True)
        embed.add_field(name="📊 K/D", value=kd, inline=True)
    
    # Badges desbloqueados
    badges = []
    for ach_id, ach_data in achievements.items():
        if ach_data.get("unlocked"):
            ach_def = ACHIEVEMENTS_DEF.get(ach_id)
            if ach_def:
                badges.append(ach_def["name"].split()[0])  # Pega só o emoji
    
    if badges:
        embed.add_field(name="🎖️ Badges", value=" ".join(badges), inline=False)
    
    embed.set_footer(text="BigodeTexas • Perfil", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

@bot.command()
async def ajuda(ctx):
    msg = """
**📜 Comandos Bigode V2**
`!registrar <Gamertag>` - Vincular conta para ganhar $ por kill
`!saldo` - Ver dinheiro
`!daily` - Prêmio diário
`!loja` - Ver itens
`!comprar <codigo>` - Comprar item
`!inventario` - Ver compras
`!set_killfeed` - (Admin) Definir canal de mortes
    """
    await ctx.send(msg)

# --- SISTEMA DE CLÃS ---
CLANS_FILE = "clans.json"

def load_clans():
    return load_json(CLANS_FILE)

def save_clans(data):
    save_json(CLANS_FILE, data)

def get_user_clan(user_id):
    clans = load_clans()
    for name, data in clans.items():
        if user_id in data["members"] or user_id == data["leader"]:
            return name, data
    return None, None

@bot.group(invoke_without_command=True)
async def clan(ctx):
    """Sistema de Clãs. Use !clan ajuda para ver os comandos."""
    await ctx.send("🛡️ **Sistema de Clãs**\nUse `!clan ajuda` para ver os comandos disponíveis.")

@clan.command()
async def ajuda(ctx):
    msg = """
**🛡️ Comandos de Clã**
`!clan criar <nome>` - Cria um novo clã (Custo: 50.000 DZ Coins)
`!clan convidar <@usuario>` - Convida um jogador para o clã
`!clan entrar` - Aceita um convite pendente
`!clan sair` - Sai do clã atual
`!clan info` - Mostra informações do seu clã
`!clan kick <@usuario>` - (Líder) Expulsa um membro
    """
    await ctx.send(msg)

@clan.command()
async def criar(ctx, *, nome: str):
    """Cria um novo clã."""
    clan_name, _ = get_user_clan(ctx.author.id)
    if clan_name:
        await ctx.send(f"❌ Você já está no clã **{clan_name}**. Saia primeiro.")
        return

    # Custo de criação
    COST = 50000
    bal = get_balance(ctx.author.id)
    if bal < COST:
        await ctx.send(f"❌ Você precisa de **{COST} DZ Coins** para fundar um clã.")
        return

    clans = load_clans()
    # Verifica nome duplicado
    for cname in clans:
        if cname.lower() == nome.lower():
            await ctx.send(f"❌ Já existe um clã com o nome **{nome}**.")
            return

    update_balance(ctx.author.id, -COST, "other", "Criação de Clã")
    
    clans[nome] = {
        "leader": ctx.author.id,
        "members": [], # Membros não incluem o líder na lista, mas a verificação checa ambos
        "created_at": datetime.now().isoformat(),
        "invites": [] # Lista de IDs convidados
    }
    save_clans(clans)
    await ctx.send(f"✅ **Clã {nome} fundado com sucesso!**\nParabéns, Comandante {ctx.author.mention}!")

@clan.command()
async def convidar(ctx, member: discord.Member):
    """Convida alguém para o clã."""
    clan_name, clan_data = get_user_clan(ctx.author.id)
    if not clan_data:
        await ctx.send("❌ Você não tem clã.")
        return
    
    if clan_data["leader"] != ctx.author.id:
        await ctx.send("❌ Apenas o líder pode convidar.")
        return

    # Verifica se o convidado já tem clã
    target_clan, _ = get_user_clan(member.id)
    if target_clan:
        await ctx.send(f"❌ {member.name} já pertence ao clã **{target_clan}**.")
        return

    clans = load_clans()
    if member.id not in clans[clan_name]["invites"]:
        clans[clan_name]["invites"].append(member.id)
        save_clans(clans)
        await ctx.send(f"📩 Convite enviado para {member.mention}!\nEle deve digitar `!clan entrar` para aceitar.")
    else:
        await ctx.send(f"⚠️ {member.name} já foi convidado.")

@clan.command()
async def entrar(ctx):
    """Aceita o convite de um clã."""
    current_clan, _ = get_user_clan(ctx.author.id)
    if current_clan:
        await ctx.send(f"❌ Você já está no clã **{current_clan}**.")
        return

    clans = load_clans()
    found_invite = False
    
    for name, data in clans.items():
        if ctx.author.id in data.get("invites", []):
            # Aceita o convite
            data["invites"].remove(ctx.author.id)
            data["members"].append(ctx.author.id)
            save_clans(clans)
            await ctx.send(f"✅ **Bem-vindo ao clã {name}, {ctx.author.mention}!**")
            found_invite = True
            break
    
    if not found_invite:
        await ctx.send("❌ Você não tem convites pendentes.")

@clan.command()
async def sair(ctx):
    """Sai do clã atual."""
    clan_name, clan_data = get_user_clan(ctx.author.id)
    if not clan_data:
        await ctx.send("❌ Você não tem clã.")
        return

    clans = load_clans()
    
    if clan_data["leader"] == ctx.author.id:
        await ctx.send("⚠️ **Você é o Líder!**\nUse `!clan desfazer` para apagar o clã ou passe a liderança (não implementado ainda).")
        return

    if ctx.author.id in clans[clan_name]["members"]:
        clans[clan_name]["members"].remove(ctx.author.id)
        save_clans(clans)
        await ctx.send(f"👋 Você saiu do clã **{clan_name}**.")

@clan.command()
async def info(ctx):
    """Mostra informações do clã."""
    clan_name, clan_data = get_user_clan(ctx.author.id)
    if not clan_data:
        await ctx.send("❌ Você não tem clã.")
        return

    leader = await bot.fetch_user(clan_data["leader"])
    member_names = []
    for mid in clan_data["members"]:
        try:
            m = await bot.fetch_user(mid)
            member_names.append(m.name)
        except:
            member_names.append(str(mid))

    embed = discord.Embed(title=f"🛡️ Clã: {clan_name}", color=discord.Color.blue())
    embed.add_field(name="👑 Líder", value=leader.name, inline=True)
    embed.add_field(name="👥 Membros", value=f"{len(member_names)}", inline=True)
    
    if member_names:
        embed.add_field(name="Lista", value=", ".join(member_names), inline=False)
    
    await ctx.send(embed=embed)

@clan.command()
async def kick(ctx, member: discord.Member):
    """Expulsa um membro do clã."""
    clan_name, clan_data = get_user_clan(ctx.author.id)
    if not clan_data:
        await ctx.send("❌ Você não tem clã.")
        return
    
    if clan_data["leader"] != ctx.author.id:
        await ctx.send("❌ Apenas o líder pode expulsar.")
        return

    if member.id == ctx.author.id:
        await ctx.send("❌ Você não pode se expulsar.")
        return

    clans = load_clans()
    if member.id in clans[clan_name]["members"]:
        clans[clan_name]["members"].remove(member.id)
        save_clans(clans)
        await ctx.send(f"👢 **{member.name}** foi expulso do clã.")
    else:
        await ctx.send("❌ Este jogador não é membro do seu clã.")

# --- SISTEMA DE RECOMPENSAS (BOUNTIES) ---
BOUNTIES_FILE = "bounties.json"

def load_bounties():
    return load_json(BOUNTIES_FILE)

def save_bounties(data):
    save_json(BOUNTIES_FILE, data)

# --- SISTEMA DE ALARMES ---
ALARMS_FILE = "alarms.json"

def load_alarms():
    return load_json(ALARMS_FILE)

def save_alarms(data):
    save_json(ALARMS_FILE, data)

def check_alarms(x, z, event_desc):
    """Verifica se uma coordenada aciona algum alarme."""
    alarms = load_alarms()
    triggered = []
    
    for alarm_id, data in alarms.items():
        try:
            ax, az = data['x'], data['z']
            radius = data['radius']
            
            # Distância Euclidiana
            dist = math.sqrt((x - ax)**2 + (z - az)**2)
            
            if dist <= radius:
                triggered.append((data['owner_id'], data['name'], dist))
        except: pass
        
    return triggered

# --- SISTEMA DE ZONA QUENTE (HEATMAP) ---
recent_kills = [] # Lista de tuplas (x, z, timestamp)

def check_hotzone(new_x, new_z):
    """Verifica se há muitas mortes recentes perto desta."""
    global recent_kills
    now = datetime.now()
    
    # 1. Limpa kills antigas (> 15 minutos)
    recent_kills = [k for k in recent_kills if (now - k[2]).total_seconds() < 900]
    
    # 2. Adiciona a nova kill
    recent_kills.append((new_x, new_z, now))
    
    # 3. Conta kills próximas (Raio 500m)
    count = 0
    for kx, kz, _ in recent_kills:
        dist = math.sqrt((new_x - kx)**2 + (new_z - kz)**2)
        if dist <= 500:
            count += 1
            
    # DEBUG
    # print(f"DEBUG HEATMAP: New({new_x},{new_z}) TotalKills={len(recent_kills)} Count={count}")

    # Se tiver 3 ou mais mortes (incluindo a atual), é Zona Quente!
    if count >= 3:
        return True, count
    return False, count

# --- GEOLOCALIZAÇÃO (CIDADES) ---
CHERNARUS_LOCATIONS = {
    "NWAF (Aeroporto)": (4600, 10000),
    "Berezino": (12000, 9000),
    "Chernogorsk": (6500, 2500),
    "Elektrozavodsk": (10500, 2300),
    "Krasnostav": (11000, 12300),
    "Stary Sobor": (6000, 7700),
    "Vybor": (3800, 8900),
    "Zelenogorsk": (2700, 5300),
    "Tisy Military": (1700, 14000),
    "Balota AF": (4500, 2500),
    "Svetlojarsk": (13900, 13300),
    "Novodmitrovsk": (11500, 14500),
    "Severograd": (8400, 13700),
    "Gorka": (9500, 8800),
    "Kabanino": (5300, 8600),
    "Grishino": (7200, 9700),
    "Pavlovo": (1700, 3800),
    "Kamenka": (1800, 2200),
    "Myshkino": (2000, 7300),
    "VMC (Military)": (4500, 8300)
}

def get_location_name(x, z):
    """Retorna o nome da cidade mais próxima."""
    closest_city = "Ermo"
    min_dist = float('inf')
    
    for city, (cx, cz) in CHERNARUS_LOCATIONS.items():
        dist = math.sqrt((x - cx)**2 + (z - cz)**2)
        if dist < min_dist:
            min_dist = dist
            closest_city = city
            
    if min_dist < 600:
        return f"Em **{closest_city}**"
    elif min_dist < 2000:
        return f"Perto de **{closest_city}** ({min_dist:.0f}m)"
    else:
        return f"No meio do nada (Ermo)"

# --- COMANDOS EXTRAS ---

@bot.group(invoke_without_command=True)
async def alarme(ctx):
    """Sistema de Alarmes de Base."""
    await ctx.send("🚨 **Sistema de Alarmes**\nUse `!alarme set <nome> <X> <Z> <raio>` para proteger sua base.")

@alarme.command()
async def set(ctx, nome: str, x: float, z: float, raio: int):
    """Define um alarme. Ex: !alarme set BasePrincipal 4500 10200 100"""
    if raio > 500:
        await ctx.send("❌ Raio máximo permitido: 500 metros.")
        return
        
    cost = 10000 # Custo para instalar alarme
    bal = get_balance(ctx.author.id)
    if bal < cost:
        await ctx.send(f"❌ Custa {cost} DZ Coins para instalar um sistema de segurança.")
        return
        
    update_balance(ctx.author.id, -cost, "other", f"Instalação de Alarme: {nome}")
    
    alarms = load_alarms()
    
    user_clan, _ = get_user_clan(ctx.author.id)
    
    for aid, data in alarms.items():
        # Calcula distância entre o novo alarme e o existente
        dist = math.sqrt((x - data['x'])**2 + (z - data['z'])**2)
        # Se as áreas se sobrepõem (soma dos raios) ou estão muito perto
        if dist < (raio + data['radius']):
            owner_clan, _ = get_user_clan(data['owner_id'])
            
            # Se o dono do alarme existente não for o mesmo usuário
            if data['owner_id'] != ctx.author.id:
                # Se não tiverem clã, ou forem de clãs diferentes -> BLOQUEIA
                if user_clan is None or owner_clan != user_clan:
                    await ctx.send(f"❌ **Acesso Negado!**\nEsta área já é monitorada por outro sobrevivente (ou Clã).\nVocê só pode colocar alarmes aqui se fizer parte do mesmo Clã que o dono.")
                    # Devolve o dinheiro
                    update_balance(ctx.author.id, cost, "other", "Reembolso de Alarme")
                    return

    # ID único para o alarme
    alarm_id = f"{ctx.author.id}_{len(alarms)+1}"
    
    alarms[alarm_id] = {
        "owner_id": ctx.author.id,
        "name": nome,
        "x": x,
        "z": z,
        "radius": raio,
        "created_at": datetime.now().isoformat()
    }
    save_alarms(alarms)
    await ctx.send(f"🚨 **Alarme Instalado!**\nBase: {nome}\nLocal: {x}, {z}\nRaio: {raio}m\nSe houver tiros aqui, você será avisado!")

@alarme.command()
async def lista(ctx):
    alarms = load_alarms()
    msg = "🚨 **Seus Alarmes Ativos**\n"
    count = 0
    for aid, data in alarms.items():
        if data['owner_id'] == ctx.author.id:
            msg += f"📡 **{data['name']}**: {data['x']}x {data['z']}z ({data['radius']}m)\n"
        await ctx.send("❌ Valor mínimo: 1000 DZ Coins.")
        return
        
    bal = get_balance(ctx.author.id)
    if bal < valor:
        await ctx.send("❌ Saldo insuficiente.")
        return
        
    update_balance(ctx.author.id, -valor, "other", f"Recompensa por {gamertag}")
    
    bounties = load_bounties()
    gt_lower = gamertag.lower()
    
    if gt_lower in bounties:
        bounties[gt_lower]["amount"] += valor
    else:
        bounties[gt_lower] = {"amount": valor, "placed_by": ctx.author.id}
        
    save_bounties(bounties)
    
    embed = discord.Embed(title="🤠 PROCURADO!", description=f"Recompensa por **{gamertag}**!", color=discord.Color.orange())
    embed.add_field(name="💰 Valor", value=f"{bounties[gt_lower]['amount']} DZ Coins")
    embed.set_image(url="https://i.imgur.com/S71j4qO.png") # Imagem de Wanted
    await ctx.send(embed=embed)

# =============================================================================
# SISTEMA DE LEADERBOARD - Rankings de Jogadores
# =============================================================================

@bot.command()
async def top(ctx, categoria: str = None):
    """
    Sistema de Leaderboard - Rankings de jogadores
    
    Uso:
        !top - Menu com todas as categorias
        !top kills - Top 10 matadores
        !top kd - Top 10 K/D ratio
        !top streak - Maior killstreak
        !top coins - Mais rico em DZ Coins
        !top playtime - Mais tempo jogado
    """
    
    if not categoria:
        # Menu principal
        embed = discord.Embed(
            title="🏆 LEADERBOARD - BIGODE TEXAS",
            description="Escolha uma categoria para ver o ranking:",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="📊 Categorias Disponíveis",
            value=(
                "🔫 `!top kills` - Top Matadores\n"
                "🎯 `!top kd` - Melhor K/D Ratio\n"
                "🔥 `!top streak` - Maior Killstreak\n"
                "💰 `!top coins` - Mais Rico\n"
                "⏰ `!top playtime` - Mais Tempo Jogado"
            ),
            inline=False
        )
        
        embed.set_footer(text="BigodeTexas • Sistema de Rankings", icon_url=FOOTER_ICON)
        await ctx.send(embed=embed)
        return
    
    categoria = categoria.lower()
    
    # Carrega dados
    players_db = load_json(PLAYERS_DB_FILE)
    economy = load_json(ECONOMY_FILE)
    
    if not players_db and categoria not in ["coins"]:
        await ctx.send("❌ Ainda não há dados de jogadores suficientes para gerar rankings!")
        return
    
    # Processa ranking baseado na categoria
    if categoria == "kills":
        await show_kills_leaderboard(ctx, players_db)
    elif categoria == "kd":
        await show_kd_leaderboard(ctx, players_db)
    elif categoria == "streak":
        await show_streak_leaderboard(ctx, players_db)
    elif categoria == "coins":
        await show_coins_leaderboard(ctx, economy)
    elif categoria == "playtime":
        await show_playtime_leaderboard(ctx, players_db)
    else:
        await ctx.send(f"❌ Categoria inválida! Use `!top` para ver as opções.")

async def show_kills_leaderboard(ctx, players_db):
    """Mostra ranking de kills"""
    sorted_players = sorted(
        players_db.items(),
        key=lambda x: x[1].get('kills', 0),
        reverse=True
    )[:10]
    
    if not sorted_players:
        await ctx.send("❌ Nenhum dado de kills disponível ainda!")
        return
    
    embed = discord.Embed(
        title="🔫 TOP 10 MATADORES",
        description="Os pistoleiros mais letais do servidor!",
        color=discord.Color.red()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (player_name, stats) in enumerate(sorted_players):
        kills = stats.get('kills', 0)
        deaths = stats.get('deaths', 0)
        kd = calculate_kd(kills, deaths)
        level = calculate_level(kills)
        
        embed.add_field(
            name=f"{medals[idx]} {player_name}",
            value=f"💀 Kills: **{kills}** | 🎯 K/D: **{kd}** | ⭐ Nível: **{level}**",
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

async def show_kd_leaderboard(ctx, players_db):
    """Mostra ranking de K/D ratio"""
    qualified_players = {
        name: stats for name, stats in players_db.items()
        if stats.get('kills', 0) >= 5
    }
    
    if not qualified_players:
        await ctx.send("❌ Nenhum jogador com kills suficientes (mínimo 5) para ranking de K/D!")
        return
    
    sorted_players = sorted(
        qualified_players.items(),
        key=lambda x: calculate_kd(x[1].get('kills', 0), x[1].get('deaths', 0)),
        reverse=True
    )[:10]
    
    embed = discord.Embed(
        title="🎯 TOP 10 K/D RATIO",
        description="Os jogadores mais eficientes em combate!\n*(Mínimo 5 kills)*",
        color=discord.Color.blue()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (player_name, stats) in enumerate(sorted_players):
        kills = stats.get('kills', 0)
        deaths = stats.get('deaths', 0)
        kd = calculate_kd(kills, deaths)
        
        embed.add_field(
            name=f"{medals[idx]} {player_name}",
            value=f"🎯 K/D: **{kd}** | 💀 Kills: **{kills}** | ☠️ Deaths: **{deaths}**",
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

async def show_streak_leaderboard(ctx, players_db):
    """Mostra ranking de killstreak"""
    sorted_players = sorted(
        players_db.items(),
        key=lambda x: x[1].get('best_killstreak', 0),
        reverse=True
    )[:10]
    
    if not sorted_players or sorted_players[0][1].get('best_killstreak', 0) == 0:
        await ctx.send("❌ Nenhum killstreak registrado ainda!")
        return
    
    embed = discord.Embed(
        title="🔥 TOP 10 KILLSTREAKS",
        description="As maiores sequências de kills sem morrer!",
        color=discord.Color.orange()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (player_name, stats) in enumerate(sorted_players):
        best_streak = stats.get('best_killstreak', 0)
        if best_streak == 0:
            break
            
        current_streak = stats.get('killstreak', 0)
        kills = stats.get('kills', 0)
        
        streak_status = f"🔥 **ATIVO: {current_streak}**" if current_streak > 0 else "💀 Morreu"
        
        embed.add_field(
            name=f"{medals[idx]} {player_name}",
            value=f"🏆 Melhor: **{best_streak}** kills | {streak_status} | Total: **{kills}**",
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

async def show_coins_leaderboard(ctx, economy):
    """Mostra ranking de DZ Coins"""
    if not economy:
        await ctx.send("❌ Nenhum jogador com DZ Coins ainda!")
        return
    
    sorted_players = sorted(
        economy.items(),
        key=lambda x: x[1].get('balance', 0),
        reverse=True
    )[:10]
    
    sorted_players = [(uid, data) for uid, data in sorted_players if data.get('balance', 0) > 0]
    
    if not sorted_players:
        await ctx.send("❌ Nenhum jogador com DZ Coins ainda!")
        return
    
    embed = discord.Embed(
        title="💰 TOP 10 MAIS RICOS",
        description="Os jogadores com mais DZ Coins!",
        color=discord.Color.gold()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (user_id, data) in enumerate(sorted_players):
        balance = data.get('balance', 0)
        gamertag = data.get('gamertag', 'Não vinculada')
        
        try:
            user = await bot.fetch_user(int(user_id))
            username = user.name
        except:
            username = f"User {user_id}"
        
        embed.add_field(
            name=f"{medals[idx]} {username}",
            value=f"💵 **{balance:,} DZ Coins** | 🎮 Gamertag: {gamertag}",
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Sistema Econômico", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

async def show_playtime_leaderboard(ctx, players_db):
    """Mostra ranking de tempo jogado"""
    sorted_players = sorted(
        players_db.items(),
        key=lambda x: x[1].get('total_playtime', 0),
        reverse=True
    )[:10]
    
    if not sorted_players or sorted_players[0][1].get('total_playtime', 0) == 0:
        await ctx.send("❌ Nenhum dado de tempo jogado disponível ainda!")
        return
    
    embed = discord.Embed(
        title="⏰ TOP 10 TEMPO JOGADO",
        description="Os sobreviventes mais dedicados!",
        color=discord.Color.purple()
    )
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for idx, (player_name, stats) in enumerate(sorted_players):
        playtime = stats.get('total_playtime', 0)
        if playtime == 0:
            break
        
        hours = int(playtime // 3600)
        minutes = int((playtime % 3600) // 60)
        
        kills = stats.get('kills', 0)
        
        embed.add_field(
            name=f"{medals[idx]} {player_name}",
            value=f"⏰ **{hours}h {minutes}m** jogadas | 💀 {kills} kills",
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Atualizado em tempo real", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

# =============================================================================
# SISTEMA DE ADMIN SPAWNER - Spawnar Itens no Servidor
# =============================================================================

# Importar sistema de spawn
from spawn_system import (
    add_to_spawn_queue,
    get_pending_spawns,
    mark_spawn_processed,
    clear_processed_spawns,
    create_complete_spawn
)

@bot.command()
@require_admin_password()
async def spawn(ctx, item_name: str, quantidade: int, *, gamertag: str):
    """
    Spawna item próximo a um jogador (última posição conhecida)
    
    Uso: !spawn M4A1 1 PlayerName
    Requer: Admin + Senha
    """
    # Valida quantidade
    if quantidade < 1 or quantidade > 10:
        await ctx.send("❌ Quantidade deve ser entre 1 e 10!")
        return
    
    # Valida item
    item = find_item_by_key(item_name.lower())
    if not item:
        await ctx.send(f"❌ Item `{item_name}` não encontrado! Use `!loja` para ver itens disponíveis.")
        return
    
    item_classname = item['name']  # Nome real do item no DayZ
    
    # Busca última posição do jogador nos logs
    # Por enquanto, usa coordenadas padrão (centro do mapa)
    # TODO: Implementar busca de posição real nos logs
    default_x, default_z = 7500, 7500  # Centro de Chernarus
    
    await ctx.send(f"⚠️ **AVISO**: Sistema de busca de posição ainda não implementado.\nUsando coordenadas padrão: ({default_x}, {default_z})")
    
    # Adiciona à fila de spawns
    spawn_id = add_to_spawn_queue(
        item_name=item_classname,
        x=default_x,
        z=default_z,
        quantity=quantidade,
        requested_by=ctx.author.id,
        gamertag=gamertag
    )
    
    embed = discord.Embed(
        title="📦 SPAWN ADICIONADO À FILA",
        description=f"Item será spawnado após próximo restart do servidor!",
        color=discord.Color.green()
    )
    
    embed.add_field(name="🎯 Item", value=f"`{item_classname}` x{quantidade}", inline=True)
    embed.add_field(name="🎮 Jogador", value=gamertag, inline=True)
    embed.add_field(name="📍 Coordenadas", value=f"X: {default_x}, Z: {default_z}", inline=False)
    embed.add_field(name="🆔 ID do Spawn", value=f"`{spawn_id}`", inline=True)
    embed.add_field(name="⏰ Status", value="⏳ Aguardando processamento", inline=True)
    
    embed.set_footer(text="BigodeTexas • Admin Spawner", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)
    
    # Log de auditoria
    security_logger.log_admin_action(ctx.author.id, f"spawn {item_classname} x{quantidade} para {gamertag}")

@bot.command()
@require_admin_password()
async def spawn_coords(ctx, item_name: str, quantidade: int, x: float, z: float):
    """
    Spawna item em coordenadas específicas
    
    Uso: !spawn_coords M4A1 1 4500 10200
    Requer: Admin + Senha
    """
    # Valida quantidade
    if quantidade < 1 or quantidade > 10:
        await ctx.send("❌ Quantidade deve ser entre 1 e 10!")
        return
    
    # Valida coordenadas (Chernarus: 0-15360)
    if not (0 <= x <= 15360 and 0 <= z <= 15360):
        await ctx.send("❌ Coordenadas inválidas! Chernarus: X e Z entre 0 e 15360")
        return
    
    # Valida item
    item = find_item_by_key(item_name.lower())
    if not item:
        await ctx.send(f"❌ Item `{item_name}` não encontrado! Use `!loja` para ver itens disponíveis.")
        return
    
    item_classname = item['name']
    
    # Adiciona à fila
    spawn_id = add_to_spawn_queue(
        item_name=item_classname,
        x=x,
        z=z,
        quantity=quantidade,
        requested_by=ctx.author.id
    )
    
    embed = discord.Embed(
        title="📦 SPAWN ADICIONADO À FILA",
        description=f"Item será spawnado após próximo restart do servidor!",
        color=discord.Color.green()
    )
    
    embed.add_field(name="🎯 Item", value=f"`{item_classname}` x{quantidade}", inline=True)
    embed.add_field(name="📍 Coordenadas", value=f"X: {x:.0f}, Z: {z:.0f}", inline=True)
    embed.add_field(name="🆔 ID do Spawn", value=f"`{spawn_id}`", inline=True)
    embed.add_field(name="⏰ Status", value="⏳ Aguardando processamento", inline=True)
    
    embed.set_footer(text="BigodeTexas • Admin Spawner", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)
    
    # Log
    security_logger.log_admin_action(ctx.author.id, f"spawn_coords {item_classname} x{quantidade} em ({x}, {z})")

@bot.command()
async def spawn_list(ctx):
    """
    Lista todos os spawns pendentes
    
    Uso: !spawn_list
    """
    pending = get_pending_spawns()
    
    if not pending:
        await ctx.send("✅ Nenhum spawn pendente na fila!")
        return
    
    embed = discord.Embed(
        title="📋 FILA DE SPAWNS PENDENTES",
        description=f"Total: {len(pending)} spawn(s) aguardando processamento",
        color=discord.Color.blue()
    )
    
    for spawn in pending[:10]:  # Mostra apenas os 10 primeiros
        status_emoji = "⏳" if spawn['status'] == 'pending' else "✅"
        
        value = (
            f"🎯 Item: `{spawn['item']}` x{spawn['quantity']}\n"
            f"📍 Coords: ({spawn['x']:.0f}, {spawn['z']:.0f})\n"
            f"{status_emoji} Status: {spawn['status']}"
        )
        
        if spawn.get('gamertag'):
            value += f"\n🎮 Jogador: {spawn['gamertag']}"
        
        embed.add_field(
            name=f"🆔 {spawn['id']}",
            value=value,
            inline=False
        )
    
    if len(pending) > 10:
        embed.set_footer(text=f"Mostrando 10 de {len(pending)} • BigodeTexas", icon_url=FOOTER_ICON)
    else:
        embed.set_footer(text="BigodeTexas • Admin Spawner", icon_url=FOOTER_ICON)
    
    await ctx.send(embed=embed)

@bot.command()
@require_admin_password()
async def process_spawns(ctx):
    """
    Processa todos os spawns pendentes (gera XMLs e faz upload)
    
    Uso: !process_spawns
    Requer: Admin + Senha
    """
    pending = get_pending_spawns()
    
    if not pending:
        await ctx.send("✅ Nenhum spawn pendente para processar!")
        return
    
    await ctx.send(f"⏳ Processando {len(pending)} spawn(s)...")
    
    # Caminhos dos XMLs locais (temporários)
    events_xml = "events_custom.xml"
    positions_xml = "cfgeventspawns_custom.xml"
    
    success_count = 0
    errors = []
    
    try:
        for spawn in pending:
            if spawn['status'] != 'pending':
                continue
            
            # Cria spawn nos XMLs
            success, event_name = create_complete_spawn(
                events_xml,
                positions_xml,
                spawn['item'],
                spawn['x'],
                spawn['z'],
                spawn['quantity']
            )
            
            if success:
                mark_spawn_processed(spawn['id'])
                success_count += 1
            else:
                errors.append(spawn['id'])
        
        # Upload via FTP
        if success_count > 0:
            await ctx.send(f"📤 Fazendo upload dos XMLs para o servidor...")
            
            ftp = connect_ftp()
            if not ftp:
                await ctx.send("❌ Erro ao conectar no FTP!")
                return
            
            try:
                # Upload events.xml
                with open(events_xml, 'rb') as f:
                    ftp.storbinary(f"STOR /dayzxb_missions/dayzOffline.chernarusplus/db/events.xml", f)
                
                # Upload cfgeventspawns.xml
                with open(positions_xml, 'rb') as f:
                    ftp.storbinary(f"STOR /dayzxb_missions/dayzOffline.chernarusplus/db/cfgeventspawns.xml", f)
                
                ftp.quit()
                
                embed = discord.Embed(
                    title="✅ SPAWNS PROCESSADOS COM SUCESSO!",
                    description=f"**{success_count}** spawn(s) foram adicionados ao servidor!",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="⚠️ IMPORTANTE",
                    value="O servidor precisa ser **reiniciado** para os spawns aparecerem!",
                    inline=False
                )
                
                embed.add_field(name="✅ Processados", value=str(success_count), inline=True)
                embed.add_field(name="❌ Erros", value=str(len(errors)), inline=True)
                
                embed.set_footer(text="BigodeTexas • Admin Spawner", icon_url=FOOTER_ICON)
                await ctx.send(embed=embed)
                
                # Limpa spawns processados
                remaining = clear_processed_spawns()
                if remaining > 0:
                    await ctx.send(f"ℹ️ {remaining} spawn(s) ainda pendentes na fila.")
                
            except Exception as e:
                await ctx.send(f"❌ Erro no upload FTP: {e}")
                ftp.quit()
        
    except Exception as e:
        await ctx.send(f"❌ Erro ao processar spawns: {e}")
    
    # Log
    security_logger.log_admin_action(ctx.author.id, f"process_spawns: {success_count} processados")

# =============================================================================
# SISTEMA DE EDITOR DE GAMEPLAY - Modificar cfggameplay.json
# =============================================================================

# Importar sistema de edição
from gameplay_editor import (
    load_gameplay_config,
    save_gameplay_config,
    backup_gameplay_config,
    get_nested_value,
    set_nested_value,
    validate_value,
    get_category_params,
    find_param_category,
    list_all_categories,
    get_latest_backup,
    restore_backup,
    format_param_info,
    EDITABLE_PARAMS
)

@bot.group(invoke_without_command=True)
async def gameplay(ctx):
    """Sistema de Editor de Gameplay. Use !gameplay ajuda para ver os comandos."""
    await ctx.send("⚙️ **Editor de Gameplay**\nUse `!gameplay ajuda` para ver os comandos disponíveis.")

@gameplay.command()
async def ajuda(ctx):
    """Mostra comandos do editor de gameplay"""
    embed = discord.Embed(
        title="⚙️ EDITOR DE GAMEPLAY",
        description="Modifique cfggameplay.json via Discord!",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📋 Comandos Disponíveis",
        value=(
            "`!gameplay view [categoria]` - Ver configurações\n"
            "`!gameplay edit <param> <valor>` - Editar valor\n"
            "`!gameplay upload` - Enviar para servidor\n"
            "`!gameplay backup` - Criar backup\n"
            "`!gameplay restore` - Restaurar último backup"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📂 Categorias",
        value=(
            "`Buffs` - Regeneração, consumo\n"
            "`GeneralData` - Configurações gerais\n"
            "`BaseBuildingData.ConstructionDecayData` - Decay de bases\n"
            "`WorldsData.WeatherData` - Clima"
        ),
        inline=False
    )
    
    embed.set_footer(text="BigodeTexas • Editor de Gameplay", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

@gameplay.command()
async def view(ctx, *, categoria: str = None):
    """
    Visualiza configurações do cfggameplay.json
    
    Uso: !gameplay view Buffs
    """
    config = load_gameplay_config()
    if not config:
        await ctx.send("❌ Arquivo cfggameplay.json não encontrado!")
        return
    
    if not categoria:
        # Lista todas as categorias
        categories = list_all_categories()
        
        embed = discord.Embed(
            title="📂 CATEGORIAS DISPONÍVEIS",
            description="Use `!gameplay view <categoria>` para ver detalhes",
            color=discord.Color.blue()
        )
        
        for cat in categories:
            params = get_category_params(cat)
            embed.add_field(
                name=f"⚙️ {cat}",
                value=f"{len(params)} parâmetro(s) editável(is)",
                inline=True
            )
        
        embed.set_footer(text="BigodeTexas • Editor de Gameplay", icon_url=FOOTER_ICON)
        await ctx.send(embed=embed)
        return
    
    # Mostra parâmetros da categoria
    params = get_category_params(categoria)
    if not params:
        await ctx.send(f"❌ Categoria `{categoria}` não encontrada! Use `!gameplay view` para ver categorias.")
        return
    
    embed = discord.Embed(
        title=f"⚙️ {categoria}",
        description="Parâmetros editáveis:",
        color=discord.Color.green()
    )
    
    for param_name, param_info in params.items():
        # Busca valor atual
        full_path = f"{categoria}.{param_name}" if '.' in categoria else param_name
        current_value = get_nested_value(config, full_path)
        
        if current_value is None:
            # Tenta buscar direto na categoria
            if categoria in config and param_name in config[categoria]:
                current_value = config[categoria][param_name]
        
        info_text = format_param_info(param_name, param_info, current_value)
        
        embed.add_field(
            name=f"🔧 {param_name}",
            value=info_text,
            inline=False
        )
    
    embed.set_footer(text="BigodeTexas • Editor de Gameplay", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)

@gameplay.command()
@require_admin_password()
async def edit(ctx, parametro: str, *, valor: str):
    """
    Edita um parâmetro do cfggameplay.json
    
    Uso: !gameplay edit HealthRegen 5.0
    Requer: Admin + Senha
    """
    config = load_gameplay_config()
    if not config:
        await ctx.send("❌ Arquivo cfggameplay.json não encontrado!")
        return
    
    # Encontra categoria do parâmetro
    category, param_info = find_param_category(parametro)
    
    if not category or not param_info:
        await ctx.send(f"❌ Parâmetro `{parametro}` não encontrado ou não é editável!")
        return
    
    # Valida valor
    valid, converted_value, error_msg = validate_value(param_info, valor)
    
    if not valid:
        await ctx.send(f"❌ {error_msg}")
        return
    
    # Cria backup antes de modificar
    backup_path = backup_gameplay_config()
    
    # Busca valor atual
    full_path = f"{category}.{parametro}" if '.' in category else parametro
    old_value = get_nested_value(config, full_path)
    
    if old_value is None:
        # Tenta buscar direto
        if category in config and parametro in config[category]:
            old_value = config[category][parametro]
    
    # Modifica valor
    if '.' in category:
        # Categoria aninhada
        set_nested_value(config, full_path, converted_value)
    else:
        # Categoria simples
        if category not in config:
            config[category] = {}
        config[category][parametro] = converted_value
    
    # Salva
    save_gameplay_config(config)
    
    embed = discord.Embed(
        title="✅ PARÂMETRO MODIFICADO",
        description=f"Alteração salva localmente!",
        color=discord.Color.green()
    )
    
    embed.add_field(name="🔧 Parâmetro", value=f"`{parametro}`", inline=True)
    embed.add_field(name="📂 Categoria", value=f"`{category}`", inline=True)
    embed.add_field(name="📝 Valor Antigo", value=f"`{old_value}`", inline=True)
    embed.add_field(name="✨ Valor Novo", value=f"`{converted_value}`", inline=True)
    embed.add_field(name="💾 Backup", value=f"`{os.path.basename(backup_path)}`", inline=False)
    
    embed.add_field(
        name="⚠️ IMPORTANTE",
        value="Use `!gameplay upload` para enviar ao servidor!",
        inline=False
    )
    
    embed.set_footer(text="BigodeTexas • Editor de Gameplay", icon_url=FOOTER_ICON)
    await ctx.send(embed=embed)
    
    # Log
    security_logger.log_admin_action(ctx.author.id, f"gameplay edit {parametro}: {old_value} -> {converted_value}")

@gameplay.command()
@require_admin_password()
async def upload(ctx):
    """
    Faz upload do cfggameplay.json para o servidor
    
    Uso: !gameplay upload
    Requer: Admin + Senha
    """
    if not os.path.exists("cfggameplay.json"):
        await ctx.send("❌ Arquivo cfggameplay.json não encontrado!")
        return
    
    await ctx.send("📤 Fazendo upload do cfggameplay.json para o servidor...")
    
    try:
        ftp = connect_ftp()
        if not ftp:
            await ctx.send("❌ Erro ao conectar no FTP!")
            return
        
        # Upload
        with open("cfggameplay.json", 'rb') as f:
            ftp.storbinary("STOR /dayzxb_missions/dayzOffline.chernarusplus/cfggameplay.json", f)
        
        ftp.quit()
        
        embed = discord.Embed(
            title="✅ UPLOAD CONCLUÍDO!",
            description="cfggameplay.json enviado ao servidor!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="⚠️ IMPORTANTE",
            value="O servidor precisa ser **reiniciado** para as mudanças terem efeito!",
            inline=False
        )
        
        embed.set_footer(text="BigodeTexas • Editor de Gameplay", icon_url=FOOTER_ICON)
        await ctx.send(embed=embed)
        
        # Log
        security_logger.log_admin_action(ctx.author.id, "gameplay upload")
        
    except Exception as e:
        await ctx.send(f"❌ Erro no upload: {e}")

@gameplay.command()
async def backup(ctx):
    """
    Cria backup do cfggameplay.json
    
    Uso: !gameplay backup
    """
    if not os.path.exists("cfggameplay.json"):
        await ctx.send("❌ Arquivo cfggameplay.json não encontrado!")
        return
    
    backup_path = backup_gameplay_config()
    
    if backup_path:
        await ctx.send(f"✅ Backup criado: `{os.path.basename(backup_path)}`")
    else:
        await ctx.send("❌ Erro ao criar backup!")

@gameplay.command()
@require_admin_password()
async def restore(ctx):
    """
    Restaura último backup do cfggameplay.json
    
    Uso: !gameplay restore
    Requer: Admin + Senha
    """
    latest_backup = get_latest_backup()
    
    if not latest_backup:
        await ctx.send("❌ Nenhum backup encontrado!")
        return
    
    if restore_backup(latest_backup):
        await ctx.send(f"✅ Backup restaurado: `{os.path.basename(latest_backup)}`\n⚠️ Use `!gameplay upload` para enviar ao servidor.")
        
        # Log
        security_logger.log_admin_action(ctx.author.id, f"gameplay restore: {os.path.basename(latest_backup)}")
    else:
        await ctx.send("❌ Erro ao restaurar backup!")

# --- COMANDOS DE GUERRA ---
@bot.group(name="guerra")
async def guerra(ctx):
    """Comandos de Guerra de Clãs"""
    if ctx.invoked_subcommand is None:
        await ctx.send("Use: `!guerra declarar`, `!guerra aceitar`, `!guerra status`")

@guerra.command(name="declarar")
async def guerra_declarar(ctx, tag_inimiga: str):
    """Declara guerra contra outro clã"""
    tag_inimiga = tag_inimiga.upper()
    my_tag, my_clan = get_user_clan(ctx.author.id)
    
    if not my_tag:
        await ctx.send("❌ Você não tem um clã!")
        return
        
    if my_clan["leader"] != str(ctx.author.id):
        await ctx.send("❌ Apenas o líder pode declarar guerra!")
        return
        
    enemy_clan = get_clan_by_tag(tag_inimiga)
    if not enemy_clan:
        await ctx.send("❌ Clã inimigo não encontrado!")
        return
        
    if tag_inimiga == my_tag:
        await ctx.send("❌ Você não pode declarar guerra a si mesmo!")
        return

    clans = load_json(CLANS_FILE)
    if "wars" not in clans: clans["wars"] = {}
    
    # Verifica se já existe guerra ou pedido
    for wid, wdata in clans["wars"].items():
        if wdata["active"] and ((wdata["clan1"] == my_tag and wdata["clan2"] == tag_inimiga) or (wdata["clan1"] == tag_inimiga and wdata["clan2"] == my_tag)):
            await ctx.send("❌ Já existe uma guerra ativa entre vocês!")
            return
            
    # Cria pedido de guerra
    import uuid
    war_id = str(uuid.uuid4())[:8]
    
    clans["wars"][war_id] = {
        "clan1": my_tag,
        "clan2": tag_inimiga,
        "score": {my_tag: 0, tag_inimiga: 0},
        "start_time": datetime.now().isoformat(),
        "active": False, # Precisa aceitar
        "requester": my_tag
    }
    
    save_json(CLANS_FILE, clans)
    
    await ctx.send(f"⚔️ **DECLARAÇÃO DE GUERRA!**\nO clã **{my_tag}** declarou guerra ao **{tag_inimiga}**!\nO líder do **{tag_inimiga}** deve usar `!guerra aceitar {my_tag}` para começar o massacre.")

@guerra.command(name="aceitar")
async def guerra_aceitar(ctx, tag_rival: str):
    """Aceita um pedido de guerra"""
    tag_rival = tag_rival.upper()
    my_tag, my_clan = get_user_clan(ctx.author.id)
    
    if not my_tag:
        await ctx.send("❌ Você não tem um clã!")
        return
        
    if my_clan["leader"] != str(ctx.author.id):
        await ctx.send("❌ Apenas o líder pode aceitar guerra!")
        return
        
    clans = load_json(CLANS_FILE)
    wars = clans.get("wars", {})
    target_war_id = None
    
    for wid, wdata in wars.items():
        if not wdata["active"] and wdata["requester"] == tag_rival and wdata["clan2"] == my_tag:
            target_war_id = wid
            break
            
    if target_war_id:
        wars[target_war_id]["active"] = True
        wars[target_war_id]["start_time"] = datetime.now().isoformat() # Reinicia tempo ao aceitar
        save_json(CLANS_FILE, clans)
        await ctx.send(f"🔥 **GUERRA ACEITA!**\n**{my_tag}** vs **{tag_rival}**\nQue comece a carnificina! As kills agora valem pontos no placar.")
    else:
        await ctx.send(f"❌ Nenhum pedido de guerra pendente de **{tag_rival}**.")

@guerra.command(name="status")
async def guerra_status(ctx):
    """Mostra guerras ativas"""
    clans = load_json(CLANS_FILE)
    wars = clans.get("wars", {})
    active_found = False
    
    embed = discord.Embed(title="⚔️ GUERRAS EM ANDAMENTO", color=discord.Color.red())
    
    for wid, wdata in wars.items():
        if wdata["active"]:
            active_found = True
            c1 = wdata["clan1"]
    # Executa script de geração em thread separada para não travar o bot
    import subprocess
    
    def run_script():
        try:
            result = subprocess.run(["python", "generate_heatmap.py"], capture_output=True, text=True, cwd=os.getcwd())
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    success, output = await bot.loop.run_in_executor(None, run_script)
    
    if success and os.path.exists("heatmap.png"):
        file = discord.File("heatmap.png", filename="heatmap.png")
        embed = discord.Embed(title="🔥 BigodeTexas - PvP Heatmap", color=discord.Color.dark_orange())
        embed.set_image(url="attachment://heatmap.png")
        embed.set_footer(text=f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", icon_url=FOOTER_ICON)
        await ctx.send(embed=embed, file=file)
    else:
        await ctx.send(f"❌ **Erro ao gerar heatmap:**\n```{output[:1000]}```")

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"\n[ERRO CRITICO] O bot falhou ao iniciar: {e}")
        print("Verifique se o TOKEN esta correto e se a internet esta funcionando.")
        input("Pressione ENTER para fechar...")
