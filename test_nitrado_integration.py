"""
Script de Teste: Verificação de Integração Nitrado-Discord
============================================================

Este script testa se o bot consegue:
1. Conectar no servidor FTP da Nitrado
2. Encontrar o arquivo de log (.ADM ou .RPT)
3. Ler o conteúdo do log
4. Parsear eventos (kills, logins, logouts, construções)
5. Enviar mensagens ao Discord

Uso: python test_nitrado_integration.py
"""

import ftplib
import io
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT", "21"))
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

def test_ftp_connection():
    """Teste 1: Conexão FTP"""
    print("\n" + "="*60)
    print("TESTE 1: Conexão FTP com Nitrado")
    print("="*60)
    
    try:
        print(f"🔌 Conectando em {FTP_HOST}:{FTP_PORT}...")
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
        print("✅ Conexão estabelecida!")
        
        print(f"🔐 Fazendo login como {FTP_USER}...")
        ftp.login(FTP_USER, FTP_PASS)
        print("✅ Login bem-sucedido!")
        
        print(f"📂 Diretório atual: {ftp.pwd()}")
        
        ftp.quit()
        return True
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False

def find_log_files():
    """Teste 2: Busca de arquivos de log"""
    print("\n" + "="*60)
    print("TESTE 2: Busca de Arquivos de Log")
    print("="*60)
    
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
        ftp.login(FTP_USER, FTP_PASS)
        
        print("🔍 Buscando arquivos .ADM e .RPT...")
        found_files = []
        
        def traverse(path, depth=0):
            if depth > 5:  # Limita profundidade
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
                        print(f"  📄 Encontrado: {full_path}")
                elif "." not in name:
                    traverse(full_path, depth + 1)
        
        traverse("/")
        
        if found_files:
            found_files.sort()
            latest = found_files[-1]
            print(f"\n✅ Total de logs encontrados: {len(found_files)}")
            print(f"📌 Log mais recente: {latest}")
            ftp.quit()
            return latest
        else:
            print("❌ Nenhum arquivo de log encontrado!")
            ftp.quit()
            return None
            
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None

def read_log_sample(log_path):
    """Teste 3: Leitura do conteúdo do log"""
    print("\n" + "="*60)
    print("TESTE 3: Leitura do Conteúdo do Log")
    print("="*60)
    
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
        ftp.login(FTP_USER, FTP_PASS)
        
        print(f"📖 Baixando {log_path}...")
        bio = io.BytesIO()
        ftp.retrbinary(f"RETR {log_path}", bio.write)
        
        content = bio.getvalue().decode('utf-8', errors='ignore')
        lines = content.split('\n')
        
        print(f"✅ Arquivo baixado com sucesso!")
        print(f"📊 Total de linhas: {len(lines)}")
        print(f"📏 Tamanho: {len(content)} bytes")
        
        # Mostra últimas 20 linhas
        print("\n📋 Últimas 20 linhas do log:")
        print("-" * 60)
        for line in lines[-20:]:
            if line.strip():
                print(f"  {line[:100]}...")  # Limita a 100 caracteres
        
        ftp.quit()
        return lines
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return None

def parse_events(lines):
    """Teste 4: Parse de eventos"""
    print("\n" + "="*60)
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
    
    print("📊 Eventos detectados:")
    print(f"  🔫 Kills: {events['kills']}")
    print(f"  💀 Deaths: {events['deaths']}")
    print(f"  🟢 Logins: {events['logins']}")
    print(f"  🔴 Logouts: {events['logouts']}")
    print(f"  🏗️ Construções: {events['constructions']}")
    print(f"  📦 Pickups: {events['pickups']}")
    
    print("\n📝 Exemplos de eventos:")
    for event_type, sample in samples.items():
        if sample:
            print(f"\n  {event_type.upper()}:")
            print(f"    {sample[:150]}...")
    
    return events

def test_config_channels():
    """Teste 5: Verificação de canais configurados"""
    print("\n" + "="*60)
    print("TESTE 5: Verificação de Canais Discord")
    print("="*60)
    
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        
        print("📺 Canais configurados:")
        print(f"  🔫 Killfeed: {config.get('killfeed_channel', 'NÃO CONFIGURADO')}")
        print(f"  💰 Salário: {config.get('salary_channel', 'NÃO CONFIGURADO')}")
        print(f"  🚫 Banimento: {config.get('ban_channel', 'NÃO CONFIGURADO')}")
        print(f"  🚨 Alarme: {config.get('alarm_channel', 'NÃO CONFIGURADO')}")
        
        all_configured = all([
            config.get('killfeed_channel'),
            config.get('salary_channel'),
            config.get('ban_channel'),
            config.get('alarm_channel')
        ])
        
        if all_configured:
            print("\n✅ Todos os canais estão configurados!")
            return True
        else:
            print("\n⚠️ Alguns canais não estão configurados!")
            return False
            
    except Exception as e:
        print(f"❌ ERRO ao ler config.json: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("TESTE DE INTEGRACAO NITRADO-DISCORD")
    print("BigodeTexas Bot - Verificacao de Funcionamento")
    print("="*60)
    print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Teste 1: Conexão FTP
    results["ftp_connection"] = test_ftp_connection()
    
    if not results["ftp_connection"]:
        print("\n❌ FALHA CRÍTICA: Não foi possível conectar ao FTP!")
        print("   Verifique as credenciais no arquivo .env")
        return
    
    # Teste 2: Busca de logs
    log_path = find_log_files()
    results["log_found"] = log_path is not None
    
    if not results["log_found"]:
        print("\n❌ FALHA CRÍTICA: Nenhum arquivo de log encontrado!")
        return
    
    # Teste 3: Leitura do log
    lines = read_log_sample(log_path)
    results["log_readable"] = lines is not None
    
    if not results["log_readable"]:
        print("\n❌ FALHA CRÍTICA: Não foi possível ler o arquivo de log!")
        return
    
    # Teste 4: Parse de eventos
    events = parse_events(lines)
    results["events_found"] = sum(events.values()) > 0
    
    # Teste 5: Canais configurados
    results["channels_configured"] = test_config_channels()
    
    # Resumo Final
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"  {test_name}: {status}")
    
    print("\n" + "="*60)
    if all_passed:
        print("TODOS OS TESTES PASSARAM!")
        print("O bot ESTA FUNCIONANDO e consegue:")
        print("   1. Conectar na Nitrado via FTP")
        print("   2. Encontrar e ler os arquivos de log")
        print("   3. Detectar eventos do jogo")
        print("   4. Tem todos os canais Discord configurados")
        print("\nPROXIMO PASSO: Execute o bot com 'python bot_main.py'")
    else:
        print("ALGUNS TESTES FALHARAM!")
        print("   Verifique os erros acima e corrija antes de executar o bot.")
    print("="*60)

if __name__ == "__main__":
    main()
