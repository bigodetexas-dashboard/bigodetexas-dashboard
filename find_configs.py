import ftplib

FTP_HOST = "brsp012.gamedata.io"
FTP_PORT = 21
FTP_USER = "ni3622181_1"
FTP_PASS = "hqPuAFd9"

def list_configs():
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        
        paths_to_check = ["/dayzxb/config", "/dayzxb", "/dayzxb/battleye"]
        
        for path in paths_to_check:
            print(f"\n--- Listando {path} ---")
            try:
                ftp.cwd(path)
                items = []
                ftp.retrlines('LIST', items.append)
                for item in items:
                    if ".cfg" in item.lower() or "battleye" in item.lower():
                        print(f"FOUND: {path}/{item}")
            except Exception as e:
                print(f"Erro ao acessar {path}: {e}")
                
        ftp.quit()
    except Exception as e:
        print(f"Erro Geral: {e}")

if __name__ == "__main__":
    list_configs()
