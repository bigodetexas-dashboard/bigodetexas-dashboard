from PIL import Image
import os

def create_ico_from_png(png_path, ico_path):
    """Converte PNG para ICO (ícone do Windows)"""
    try:
        # Abrir imagem PNG
        img = Image.open(png_path)
        
        # Converter para RGBA se necessário
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Criar ícone em múltiplos tamanhos (Windows usa diferentes tamanhos)
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Salvar como ICO
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        
        print(f"[OK] Icone criado com sucesso: {ico_path}")
        print(f"     Tamanhos incluidos: {icon_sizes}")
        return True
        
    except Exception as e:
        print(f"[ERRO] Erro ao criar icone: {e}")
        return False

if __name__ == "__main__":
    # Caminhos
    png_file = "bot_avatar.png"
    ico_file = "launcher_icon.ico"
    
    # Criar ícone
    if create_ico_from_png(png_file, ico_file):
        print("\n[SUCESSO] Icone pronto para uso!")
        print(f"          Arquivo: {ico_file}")
    else:
        print("\n[FALHA] Falha ao criar icone.")
