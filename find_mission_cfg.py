import ftplib

FTP_HOST = "brsp012.gamedata.io"
FTP_PORT = 21
FTP_USER = "ni3622181_1"
FTP_PASS = "hqPuAFd9"

def list_mission():
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        
        path = "/dayzxb_missions/dayzOffline.chernarusplus"
        print(f"\n--- Listando {path} ---")
        
        items = []
        ftp.cwd(path)
        ftp.retrlines('LIST', items.append)
        
        for item in items:
            print(item)
                
        ftp.quit()
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    list_mission()
