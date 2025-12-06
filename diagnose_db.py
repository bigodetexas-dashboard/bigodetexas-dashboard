import os
import sys
import psycopg2
from dotenv import load_dotenv

# Force UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERRO: DATABASE_URL nao definida.")
    sys.exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Listar tabelas
    print("\n--- TABELAS EXISTENTES ---")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n[Tabela: {table_name}]")
        
        # Listar colunas da tabela
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}'
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"ERRO: {e}")
