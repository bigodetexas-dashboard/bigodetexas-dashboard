"""
Script de Migracao: JSON -> PostgreSQL
Migra dados existentes de arquivos JSON para o banco PostgreSQL
"""

import json
import os
from database import (
    init_database, 
    save_player, 
    save_economy, 
    save_link,
    get_connection
)

def load_json_file(filename):
    """Carrega arquivo JSON se existir"""
    if not os.path.exists(filename):
        print(f"[AVISO] Arquivo {filename} nao encontrado, pulando...")
        return {}
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRO] Erro ao ler {filename}: {e}")
        return {}

def migrate_players():
    """Migra players_db.json -> PostgreSQL"""
    print("\n[PLAYERS] Migrando jogadores...")
    players = load_json_file('players_db.json')
    
    if not players:
        print("   Nenhum jogador para migrar")
        return
    
    count = 0
    for gamertag, data in players.items():
        if save_player(gamertag, data):
            count += 1
            print(f"   [OK] {gamertag}")
        else:
            print(f"   [ERRO] Falha: {gamertag}")
    
    print(f"   Total migrado: {count}/{len(players)}")

def migrate_economy():
    """Migra economy.json -> PostgreSQL"""
    print("\n[ECONOMY] Migrando economia...")
    economy = load_json_file('economy.json')
    
    if not economy:
        print("   Nenhum dado de economia para migrar")
        return
    
    count = 0
    for discord_id, data in economy.items():
        if save_economy(discord_id, data):
            count += 1
            print(f"   [OK] {discord_id}")
        else:
            print(f"   [ERRO] Falha: {discord_id}")
    
    print(f"   Total migrado: {count}/{len(economy)}")

def migrate_links():
    """Migra links.json -> PostgreSQL"""
    print("\n[LINKS] Migrando links Discord-Gamertag...")
    links = load_json_file('links.json')
    
    if not links:
        print("   Nenhum link para migrar")
        return
    
    count = 0
    for discord_id, gamertag in links.items():
        if save_link(discord_id, gamertag):
            count += 1
            print(f"   [OK] {discord_id} -> {gamertag}")
        else:
            print(f"   [ERRO] Falha: {discord_id}")
    
    print(f"   Total migrado: {count}/{len(links)}")

def main():
    """Executa migracao completa"""
    print("="*60)
    print("[MIGRACAO] JSON -> PostgreSQL")
    print("="*60)
    
    # Verificar conexao
    conn = get_connection()
    if not conn:
        print("\n[ERRO] Nao foi possivel conectar ao PostgreSQL!")
        print("   Verifique se DATABASE_URL esta configurado no .env")
        return
    
    print("[OK] Conexao com PostgreSQL estabelecida!")
    conn.close()
    
    # Criar tabelas
    print("\n[SETUP] Criando tabelas...")
    if init_database():
        print("[OK] Tabelas criadas/verificadas!")
    else:
        print("[ERRO] Erro ao criar tabelas!")
        return
    
    # Migrar dados
    migrate_players()
    migrate_economy()
    migrate_links()
    
    print("\n" + "="*60)
    print("[SUCESSO] MIGRACAO CONCLUIDA!")
    print("="*60)
    print("\n[INFO] Proximos passos:")
    print("   1. Verifique os dados no painel web")
    print("   2. Teste comandos do bot (!link, !stats, etc)")
    print("   3. Os arquivos JSON foram mantidos como backup")

if __name__ == "__main__":
    main()
