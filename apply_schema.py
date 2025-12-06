import os
import sys
import psycopg2
from dotenv import load_dotenv

# Forcar encoding UTF-8 para o stdout/stderr para evitar erros no Windows
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Carregar variaveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("--- INICIANDO APLICACAO DE SCHEMA ---")

if not DATABASE_URL:
    print("ERRO: DATABASE_URL nao encontrada no arquivo .env")
    print("Verifique se o arquivo .env existe e contem a linha: DATABASE_URL=postgresql://...")
    sys.exit(1)

try:
    print("Conectando ao Banco de Dados...")
    # Conectar ao banco
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Ler o arquivo SQL
    print("Lendo arquivo schema_v2_compat.sql...")
    try:
        with open("schema_v2_compat.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()
    except FileNotFoundError:
        print("ERRO: Arquivo schema_v2_compat.sql nao encontrado!")
        sys.exit(1)
        
    # Executar SQL
    print("Aplicando Schema SQL...")
    cursor.execute(schema_sql)
    conn.commit()
    
    print("SUCESSO: Schema aplicado com sucesso!")
    print("As tabelas (users, clans, bases, transactions, etc.) foram criadas ou atualizadas.")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"ERRO CRITICO durante a execucao: {e}")
    sys.exit(1)
