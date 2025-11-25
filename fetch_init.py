import ftplib
import os

FTP_HOST = "brsp012.gamedata.io"
FTP_USER = "ni3622181_1"
FTP_PASS = "hqPuAFd9"

def find_and_download_init():
    print(f"Conectando a {FTP_HOST}...")
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, 21)
        ftp.login(FTP_USER, FTP_PASS)
        print("Login OK.")

        # Navegar para mpmissions
        try:
            ftp.cwd("mpmissions")
            print("Entrou em /mpmissions")
        except:
            print("Pasta /mpmissions não encontrada na raiz.")
            return

        # Listar missões
        items = ftp.nlst()
        mission_folder = None
        for item in items:
            if "dayzOffline" in item:
                mission_folder = item
                break
        
        if not mission_folder:
            print("Nenhuma pasta de missão (dayzOffline.*) encontrada.")
            # Tenta listar tudo pra debug
            print(f"Pastas encontradas: {items}")
            return

        print(f"Acessando missão: {mission_folder}")
        ftp.cwd(mission_folder)

        # Baixar init.c
        if "init.c" in ftp.nlst():
            print("Arquivo init.c encontrado! Baixando...")
            with open("init.c", "wb") as f:
                ftp.retrbinary("RETR init.c", f.write)
            print("✅ Sucesso! init.c salvo localmente.")
        else:
            print("❌ init.c NÃO encontrado nesta pasta.")

        ftp.quit()

    except Exception as e:
        print(f"❌ Erro FTP: {e}")

if __name__ == "__main__":
    find_and_download_init()
