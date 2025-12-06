
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def list_tables():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Listar tabelas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        
        print("=== TABELAS NO BANCO ===")
        for table in tables:
            print(f"- {table[0]}")
            
            # Listar colunas
            cur.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table[0]}'
            """)
            columns = cur.fetchall()
            for col in columns:
                print(f"  |-- {col[0]} ({col[1]})")
            print("")
            
        conn.close()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    list_tables()
