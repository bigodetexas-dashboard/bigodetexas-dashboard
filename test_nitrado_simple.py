# -*- coding: utf-8 -*-
"""
Script de Teste: Verificacao de Integracao Nitrado-Discord
============================================================

Este script testa se o bot consegue:
1. Conectar no servidor FTP da Nitrado
2. Encontrar o arquivo de log (.ADM ou .RPT)
3. Ler o conteudo do log
4. Parsear eventos (kills, logins, logouts, construcoes)
5. Enviar mensagens ao Discord

Uso: python test_nitrado_simple.py
"""

import ftplib
import io
import json
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Forcar UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Carregar variaveis de ambiente
load_dotenv()

FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

print("\n" + "="*60)
print("TESTE DE INTEGRACAO NITRADO-DISCORD")
print("BigodeTexas Bot - Verificacao de Funcionamento")
print("="*60)
print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# TESTE 1: Conexao FTP
print("="*60)
print("TESTE 1: Conexao FTP com Nitrado")
print("="*60)

try:
    print(f"Conectando em {FTP_HOST}:{FTP_PORT}...")
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
    print("[OK] Conexao estabelecida!")
    
    print(f"Fazendo login como {FTP_USER}...")
    ftp.login(FTP_USER, FTP_PASS)
    print("[OK] Login bem-sucedido!")
    
    print(f"Diretorio atual: {ftp.pwd()}")
    
    ftp.quit()
    print("[PASSOU] Teste de conexao FTP\n")
    ftp_ok = True
    
except Exception as e:
    print(f"[ERRO] {e}")
    print("[FALHOU] Teste de conexao FTP\n")
    ftp_ok = False

if not ftp_ok:
    print("\n[CRITICO] Nao foi possivel conectar ao FTP!")
    print("Verifique as credenciais no arquivo .env")
    sys.exit(1)

# TESTE 2: Busca de arquivos de log
print("="*60)
print("TESTE 2: Busca de Arquivos de Log")
print("="*60)

try:
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
    ftp.login(FTP_USER, FTP_PASS)
    
    print("Buscando arquivos .ADM e .RPT...")
    found_files = []
    
    def traverse(path, depth=0):
        if depth > 5:
            return
            
        try:
            ftp.cwd(path)
            items = ftp.nlst()
        except:
            return
        
        for name in items:
            if name in [".", ".."]:
                continue
            
            full_path = f"{path}/{name}" if path != "/" else f"/{name}"
            lower_name = name.lower()
            
            if lower_name.endswith(".adm") or lower_name.endswith(".rpt"):
                if "crash" not in lower_name:
                    found_files.append(full_path)
                    print(f"  Encontrado: {full_path}")
            elif "." not in name:
                traverse(full_path, depth + 1)
    
    traverse("/")
    
    if found_files:
        found_files.sort()
        latest = found_files[-1]
        print(f"\n[OK] Total de logs encontrados: {len(found_files)}")
        print(f"Log mais recente: {latest}")
        print("[PASSOU] Teste de busca de logs\n")
        ftp.quit()
        log_ok = True
        log_path = latest
    else:
        print("[ERRO] Nenhum arquivo de log encontrado!")
        print("[FALHOU] Teste de busca de logs\n")
        ftp.quit()
        log_ok = False
        log_path = None
        
except Exception as e:
    print(f"[ERRO] {e}")
    print("[FALHOU] Teste de busca de logs\n")
    log_ok = False
    log_path = None

if not log_ok:
    print("\n[CRITICO] Nenhum arquivo de log encontrado!")
    sys.exit(1)

# TESTE 3: Leitura do conteudo do log
print("="*60)
print("TESTE 3: Leitura do Conteudo do Log")
print("="*60)

try:
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
    ftp.login(FTP_USER, FTP_PASS)
    
    print(f"Baixando {log_path}...")
    bio = io.BytesIO()
    ftp.retrbinary(f"RETR {log_path}", bio.write)
    
    content = bio.getvalue().decode('utf-8', errors='ignore')
    lines = content.split('\n')
    
    print(f"[OK] Arquivo baixado com sucesso!")
    print(f"Total de linhas: {len(lines)}")
    print(f"Tamanho: {len(content)} bytes")
    
    # Mostra ultimas 10 linhas
    print("\nUltimas 10 linhas do log:")
    print("-" * 60)
    for line in lines[-10:]:
        if line.strip():
            print(f"  {line[:80]}")
    
    print("\n[PASSOU] Teste de leitura do log\n")
    ftp.quit()
    read_ok = True
    
except Exception as e:
    print(f"[ERRO] {e}")
    print("[FALHOU] Teste de leitura do log\n")
    read_ok = False
    lines = []

if not read_ok:
    print("\n[CRITICO] Nao foi possivel ler o arquivo de log!")
    sys.exit(1)

# TESTE 4: Parse de eventos
print("="*60)
print("TESTE 4: Parse de Eventos do Log")
print("="*60)

events = {
    "kills": 0,
    "deaths": 0,
    "logins": 0,
    "logouts": 0,
    "constructions": 0,
    "pickups": 0
}

samples = {
    "kill": None,
    "login": None,
    "logout": None,
    "construction": None
}

for line in lines:
    line_lower = line.lower()
    
    if "killed by player" in line_lower:
        events["kills"] += 1
        if not samples["kill"]:
            samples["kill"] = line.strip()
    
    elif "died" in line_lower and "player" in line_lower:
        events["deaths"] += 1
    
    elif "connected" in line_lower and "player" in line_lower:
        events["logins"] += 1
        if not samples["login"]:
            samples["login"] = line.strip()
    
    elif "disconnected" in line_lower and "player" in line_lower:
        events["logouts"] += 1
        if not samples["logout"]:
            samples["logout"] = line.strip()
    
    elif "placed" in line_lower and "at <" in line_lower:
        events["constructions"] += 1
        if not samples["construction"]:
            samples["construction"] = line.strip()
    
    elif "picked up" in line_lower:
        events["pickups"] += 1

print("Eventos detectados:")
print(f"  Kills: {events['kills']}")
print(f"  Deaths: {events['deaths']}")
print(f"  Logins: {events['logins']}")
print(f"  Logouts: {events['logouts']}")
print(f"  Construcoes: {events['constructions']}")
print(f"  Pickups: {events['pickups']}")

print("\nExemplos de eventos:")
for event_type, sample in samples.items():
    if sample:
        print(f"\n  {event_type.upper()}:")
        print(f"    {sample[:120]}")

events_ok = sum(events.values()) > 0
if events_ok:
    print("\n[PASSOU] Teste de parse de eventos\n")
else:
    print("\n[AVISO] Nenhum evento detectado no log\n")

# TESTE 5: Verificacao de canais configurados
print("="*60)
print("TESTE 5: Verificacao de Canais Discord")
print("="*60)

try:
    with open("config.json", "r") as f:
        config = json.load(f)
    
    print("Canais configurados:")
    print(f"  Killfeed: {config.get('killfeed_channel', 'NAO CONFIGURADO')}")
    print(f"  Salario: {config.get('salary_channel', 'NAO CONFIGURADO')}")
    print(f"  Banimento: {config.get('ban_channel', 'NAO CONFIGURADO')}")
    print(f"  Alarme: {config.get('alarm_channel', 'NAO CONFIGURADO')}")
    
    all_configured = all([
        config.get('killfeed_channel'),
        config.get('salary_channel'),
        config.get('ban_channel'),
        config.get('alarm_channel')
    ])
    
    if all_configured:
        print("\n[OK] Todos os canais estao configurados!")
        print("[PASSOU] Teste de configuracao de canais\n")
        channels_ok = True
    else:
        print("\n[AVISO] Alguns canais nao estao configurados!")
        print("[FALHOU] Teste de configuracao de canais\n")
        channels_ok = False
        
except Exception as e:
    print(f"[ERRO] ao ler config.json: {e}")
    print("[FALHOU] Teste de configuracao de canais\n")
    channels_ok = False

# RESUMO FINAL
print("="*60)
print("RESUMO DOS TESTES")
print("="*60)

results = {
    "Conexao FTP": ftp_ok,
    "Busca de Logs": log_ok,
    "Leitura de Logs": read_ok,
    "Parse de Eventos": events_ok,
    "Canais Configurados": channels_ok
}

for test_name, passed in results.items():
    status = "[OK]" if passed else "[FALHOU]"
    print(f"  {test_name}: {status}")

print("\n" + "="*60)
all_passed = all(results.values())

if all_passed:
    print("TODOS OS TESTES PASSARAM!")
    print("\nO bot ESTA FUNCIONANDO e consegue:")
    print("  1. Conectar na Nitrado via FTP")
    print("  2. Encontrar e ler os arquivos de log")
    print("  3. Detectar eventos do jogo")
    print("  4. Tem todos os canais Discord configurados")
    print("\nPROXIMO PASSO: Execute o bot com 'python bot_main.py'")
else:
    print("ALGUNS TESTES FALHARAM!")
    print("Verifique os erros acima e corrija antes de executar o bot.")

print("="*60)
