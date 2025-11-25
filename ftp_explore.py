import ftplib

FTP_HOST = "brsp012.gamedata.io"
FTP_PORT = 21
FTP_USER = "ni3622181_1"
FTP_PASS = "hqPuAFd9"

def find_paths():
    try:
        ftp = ftplib.FTP()
        ftp.connect(FTP_HOST, FTP_PORT)
        ftp.login(FTP_USER, FTP_PASS)
        print("Connected.")
        
        # 1. Procurar init.c em dayzxb_missions
        print("\n--- Searching init.c ---")
        try:
            ftp.cwd("/dayzxb_missions")
            missions = ftp.nlst()
            for m in missions:
                if "." in m: # Pasta da missao
                    print(f"Checking: {m}")
                    try:
                        ftp.cwd(f"/dayzxb_missions/{m}")
                        files = ftp.nlst()
                        if "init.c" in files:
                            print(f"FOUND INIT.C: /dayzxb_missions/{m}/init.c")
                    except: pass
        except: pass
        
        # 3. Tentar baixar globals.xml
        print("\n--- Downloading globals.xml ---")
        target_path = "/dayzxb_missions/dayzOffline.chernarusplus/db/globals.xml" # Caminho padrão comum
        # Mas pode estar em outro lugar. Vamos tentar achar.
        
        possible_paths = [
            "/dayzxb_missions/dayzOffline.chernarusplus/db/globals.xml",
            "/dayzxb/config/globals.xml",
            "/config/globals.xml",
            "/SC/globals.xml"
        ]
        
        for p in possible_paths:
            try:
                with open("globals_downloaded.xml", "wb") as f:
                    ftp.retrbinary(f"RETR {p}", f.write)
                print(f"SUCCESS: Downloaded from {p}")
                break
            except Exception as e:
                print(f"Failed {p}: {e}")

        ftp.quit()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_paths()
