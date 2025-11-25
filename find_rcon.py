import ftplib

# Credenciais do bot_main.py
FTP_HOST = "brsp012.gamedata.io"
FTP_PORT = 21
FTP_USER = "ni3622181_1"
FTP_PASS = "hqPuAFd9"

def list_recursive(ftp, path=""):
    try:
        ftp.cwd(path)
        items = []
        ftp.retrlines('LIST', items.append)
        
        for item in items:
            print(f"{path}/{item}")
            if "<DIR>" in item or item.startswith("d"): # Detecção básica de diretório
                parts = item.split()
                name = parts[-1]
                if name not in [".", ".."]:
                    try:
                        list_recursive(ftp, f"{path}/{name}")
                        ftp.cwd("..")
                    except: pass
    except Exception as e:
        print(f"Erro em {path}: {e}")

def explore():
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        print("Conectado. Listando arquivos...")
        
        # Lista raiz e subpastas principais
        list_recursive(ftp, "/")
        
        ftp.quit()
    except Exception as e:
        print(f"Erro Geral: {e}")

if __name__ == "__main__":
    explore()
