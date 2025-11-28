# -*- coding: utf-8 -*-
"""
Gerador de Tiles do Mapa Chernarus para BigodeTexas
Gera tiles placeholder com grid, coordenadas e nomes de cidades
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configurações
MAP_SIZE = 15360  # Chernarus em metros
TILE_SIZE = 256
OUTPUT_DIR = "static/tiles"

# Cidades principais do Chernarus (coordenadas aproximadas X, Z)
CITIES = [
    {"name": "Elektrozavodsk", "x": 10300, "z": 2200, "size": "large"},
    {"name": "Cherno", "x": 6700, "z": 2500, "size": "large"},
    {"name": "Berezino", "x": 12500, "z": 9200, "size": "medium"},
    {"name": "Novo", "x": 7100, "z": 7700, "size": "medium"},
    {"name": "Stary Sobor", "x": 6100, "z": 7700, "size": "medium"},
    {"name": "Novy Sobor", "x": 7100, "z": 7700, "size": "medium"},
    {"name": "Gorka", "x": 9700, "z": 8900, "size": "small"},
    {"name": "Polana", "x": 7000, "z": 6500, "size": "small"},
    {"name": "Vybor", "x": 3800, "z": 8900, "size": "medium"},
    {"name": "Zelenogorsk", "x": 2500, "z": 5100, "size": "medium"},
    {"name": "NWAF", "x": 4500, "z": 10200, "size": "military"},
    {"name": "NEAF", "x": 12100, "z": 12600, "size": "military"},
    {"name": "Balota", "x": 4500, "z": 2300, "size": "military"},
]

def create_tile(z, x, y):
    """Cria um tile individual"""
    img = Image.new('RGB', (TILE_SIZE, TILE_SIZE), color=(45, 52, 54))
    draw = ImageDraw.Draw(img)
    
    # Calcular escala baseada no zoom
    tiles_per_side = 2 ** z
    pixels_per_tile_in_map = MAP_SIZE / tiles_per_side
    
    # Posição do tile no mapa (em metros)
    tile_map_x = x * pixels_per_tile_in_map
    tile_map_y = y * pixels_per_tile_in_map
    
    # Desenhar grid
    grid_color = (70, 70, 70)
    grid_step = 32
    
    for gx in range(0, TILE_SIZE, grid_step):
        draw.line([(gx, 0), (gx, TILE_SIZE)], fill=grid_color, width=1)
    for gy in range(0, TILE_SIZE, grid_step):
        draw.line([(0, gy), (TILE_SIZE, gy)], fill=grid_color, width=1)
    
    # Tentar carregar fonte
    try:
        font_small = ImageFont.truetype("arial.ttf", 10)
        font_medium = ImageFont.truetype("arial.ttf", 14)
        font_large = ImageFont.truetype("arialbd.ttf", 18)
    except:
        font_small = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_large = ImageFont.load_default()
    
    # Desenhar coordenadas do tile (canto superior esquerdo)
    coord_text = f"{int(tile_map_x)},{int(tile_map_y)}"
    draw.text((5, 5), coord_text, fill=(100, 100, 100), font=font_small)
    
    # Desenhar cidades que aparecem neste tile
    for city in CITIES:
        # Converter coordenadas da cidade para posição no tile
        city_x_in_map = city["x"]
        city_z_in_map = city["z"]
        
        # Verificar se a cidade está dentro deste tile
        if (tile_map_x <= city_x_in_map < tile_map_x + pixels_per_tile_in_map and
            tile_map_y <= city_z_in_map < tile_map_y + pixels_per_tile_in_map):
            
            # Posição relativa dentro do tile
            rel_x = int(((city_x_in_map - tile_map_x) / pixels_per_tile_in_map) * TILE_SIZE)
            rel_y = int(((city_z_in_map - tile_map_y) / pixels_per_tile_in_map) * TILE_SIZE)
            
            # Escolher cor e fonte baseado no tamanho
            if city["size"] == "large":
                color = (255, 107, 53)  # Laranja
                font = font_large
                marker_size = 8
            elif city["size"] == "military":
                color = (231, 76, 60)  # Vermelho
                font = font_medium
                marker_size = 6
            elif city["size"] == "medium":
                color = (52, 152, 219)  # Azul
                font = font_medium
                marker_size = 5
            else:
                color = (149, 165, 166)  # Cinza
                font = font_small
                marker_size = 4
            
            # Desenhar marcador
            draw.ellipse([rel_x-marker_size, rel_y-marker_size, 
                         rel_x+marker_size, rel_y+marker_size], 
                        fill=color, outline=(255, 255, 255))
            
            # Desenhar nome
            draw.text((rel_x + marker_size + 3, rel_y - 7), 
                     city["name"], fill=color, font=font)
    
    # Adicionar textura sutil
    if z > 2:  # Apenas em zooms maiores
        for _ in range(50):
            import random
            px = random.randint(0, TILE_SIZE-1)
            py = random.randint(0, TILE_SIZE-1)
            noise_color = (random.randint(40, 60), random.randint(45, 65), random.randint(45, 65))
            draw.point((px, py), fill=noise_color)
    
    return img

def generate_tiles(max_zoom=6):
    """Gera todos os tiles para todos os níveis de zoom"""
    print(f"[MAP] Gerando tiles do mapa Chernarus...")
    print(f"[SIZE] Tamanho do mapa: {MAP_SIZE}x{MAP_SIZE} metros")
    print(f"[ZOOM] Niveis de zoom: 0 ate {max_zoom}")
    
    total_tiles = 0
    
    for z in range(max_zoom + 1):
        tiles_per_side = 2 ** z
        print(f"\n[Z{z}] Gerando {tiles_per_side}x{tiles_per_side} tiles")
        
        for x in range(tiles_per_side):
            for y in range(tiles_per_side):
                # Criar diretórios
                tile_dir = os.path.join(OUTPUT_DIR, str(z), str(x))
                os.makedirs(tile_dir, exist_ok=True)
                
                # Gerar tile
                tile = create_tile(z, x, y)
                
                # Salvar
                tile_path = os.path.join(tile_dir, f"{y}.png")
                tile.save(tile_path, "PNG", optimize=True)
                
                total_tiles += 1
                
                if total_tiles % 10 == 0:
                    print(f"   Gerados: {total_tiles} tiles...", end='\r')
        
        print(f"   [OK] Zoom {z} completo: {tiles_per_side * tiles_per_side} tiles")
    
    print(f"\n[DONE] Concluido! Total: {total_tiles} tiles gerados")
    print(f"[PATH] Localizacao: {os.path.abspath(OUTPUT_DIR)}")
    print(f"\n[INFO] Copie a pasta 'tiles' para 'server/public/static/tiles'")

if __name__ == "__main__":
    # Criar diretório de saída
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Gerar tiles
    generate_tiles(max_zoom=6)
    
    print("\n[SUCCESS] Tiles prontos para uso!")
    print("[WEB] Acesse http://localhost:3000/checkout para ver o mapa")
