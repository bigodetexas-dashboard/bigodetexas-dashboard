import ftplib
import os

FTP_HOST = "brsp012.gamedata.io"
FTP_PORT = 21
FTP_USER = "ni3622181_1"
FTP_PASS = "hqPuAFd9"

LOCAL_FILE = "init.c"
REMOTE_PATH = "/dayzxb_missions/dayzOffline.chernarusplus/init.c"

def deploy():
    if not os.path.exists(LOCAL_FILE):
        print("Erro: init.c local nao encontrado.")
        return

    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        print("Conectado ao FTP.")
        
        print(f"Enviando {LOCAL_FILE} para {REMOTE_PATH}...")
        with open(LOCAL_FILE, 'rb') as f:
            ftp.storbinary(f"STOR {REMOTE_PATH}", f)
            
        print("Upload concluido com sucesso!")
        ftp.quit()
    except Exception as e:
        print(f"Erro no upload: {e}")

if __name__ == "__main__":
    deploy()
