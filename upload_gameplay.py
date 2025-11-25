import ftplib
import os

# Configurações FTP
FTP_HOST = "brsp012.gamedata.io"
FTP_PORT = 21
FTP_USER = "ni3622181_1"
FTP_PASS = "hqPuAFd9"

# Arquivo Local
LOCAL_FILE = "cfggameplay.json"

# Caminho Remoto (Pasta da Missão)
# Baseado na descoberta anterior: /dayzxb_missions/dayzOffline.chernarusplus/
REMOTE_PATH = "/dayzxb_missions/dayzOffline.chernarusplus/cfggameplay.json"

def upload_gameplay_config():
    if not os.path.exists(LOCAL_FILE):
        print(f"Erro: Arquivo {LOCAL_FILE} não encontrado!")
        return

    try:
        print(f"Conectando ao FTP {FTP_HOST}...")
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        print("Conectado!")

        print(f"Enviando {LOCAL_FILE} para {REMOTE_PATH}...")
        with open(LOCAL_FILE, 'rb') as f:
            ftp.storbinary(f"STOR {REMOTE_PATH}", f)
        
        print("[OK] Upload concluido com sucesso!")
        ftp.quit()

    except Exception as e:
        print(f"[ERRO] Erro no upload: {e}")

if __name__ == "__main__":
    upload_gameplay_config()
