from PIL import Image
import sys

def image_to_ascii(image_path, width=100):
    """Converte imagem para ASCII art"""
    
    # Caracteres ASCII do mais escuro ao mais claro
    ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.', ' ']
    
    try:
        # Abrir imagem
        img = Image.open(image_path)
        
        # Calcular altura proporcional
        aspect_ratio = img.height / img.width
        height = int(width * aspect_ratio * 0.55)  # 0.55 para compensar proporção dos caracteres
        
        # Redimensionar
        img = img.resize((width, height))
        
        # Converter para escala de cinza
        img = img.convert('L')
        
        # Converter pixels para ASCII
        pixels = img.getdata()
        ascii_str = ''
        
        for i, pixel in enumerate(pixels):
            # Mapear valor do pixel (0-255) para caractere ASCII
            ascii_str += ASCII_CHARS[pixel // 25]
            
            # Nova linha a cada 'width' caracteres
            if (i + 1) % width == 0:
                ascii_str += '\n'
        
        return ascii_str
    
    except Exception as e:
        return f"Erro ao converter imagem: {e}"

if __name__ == "__main__":
    # Converter banner
    banner_path = "banner_bigode_texas.png"
    ascii_art = image_to_ascii(banner_path, width=80)
    
    # Salvar em arquivo
    with open("banner_ascii.txt", "w", encoding="utf-8") as f:
        f.write(ascii_art)
    
    print("Banner ASCII gerado em banner_ascii.txt")
    print("\nPreview:")
    print(ascii_art[:500])  # Mostrar primeiras linhas
