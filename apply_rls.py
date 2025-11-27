import os
import psycopg2
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Erro: DATABASE_URL não encontrada no .env")
    exit(1)

def apply_rls():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        tables = ["players", "economy", "clans", "links"]
        
        print("[INFO] Iniciando aplicacao de RLS (Row Level Security)...")
        
        for table in tables:
            print(f"\nProcessando tabela: {table}...")
            
            # 1. Habilitar RLS
            cur.execute(f"ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;")
            print(f"  [OK] RLS habilitado.")
            
            # 2. Política para 'postgres' (Admin/Bot) - Acesso Total
            # O usuário postgres geralmente é superuser e ignora RLS, mas isso garante explicitamente.
            policy_name_pg = f"Enable all for postgres on {table}"
            cur.execute(f"DROP POLICY IF EXISTS \"{policy_name_pg}\" ON public.{table};")
            cur.execute(f"""
                CREATE POLICY "{policy_name_pg}"
                ON public.{table}
                FOR ALL
                TO postgres
                USING (true)
                WITH CHECK (true);
            """)
            print(f"  [OK] Politica 'postgres' criada.")

            # 3. Política para 'service_role' (Supabase API Admin) - Acesso Total
            policy_name_sr = f"Enable all for service_role on {table}"
            cur.execute(f"DROP POLICY IF EXISTS \"{policy_name_sr}\" ON public.{table};")
            cur.execute(f"""
                CREATE POLICY "{policy_name_sr}"
                ON public.{table}
                FOR ALL
                TO service_role
                USING (true)
                WITH CHECK (true);
            """)
            print(f"  [OK] Politica 'service_role' criada.")
            
            # 4. Política para 'anon' (Público) - Apenas Leitura (Opcional, mas bom para Dashboard futuro via API)
            # Por enquanto, vamos deixar bloqueado para anon (padrão do RLS) para segurança máxima.
            # Se precisarmos ler via JS no frontend depois, criamos uma política "Enable read for anon".
            
        conn.commit()
        cur.close()
        conn.close()
        print("\n[SUCESSO] Todas as tabelas estao protegidas com RLS.")
        return True
        
    except Exception as e:
        print(f"\n[ERRO] Erro ao aplicar RLS: {e}")
        return False

if __name__ == "__main__":
    apply_rls()
