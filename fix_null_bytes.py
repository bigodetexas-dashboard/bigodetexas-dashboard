
import os

file_path = 'new_dashboard/app.py'

try:
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Remover bytes nulos e caracteres estranhos de encoding errado (UTF-16 headers FE FF)
    # 0x00 é null byte
    clean_content = content.replace(b'\x00', b'')
    
    # Salvar de volta
    with open(file_path, 'wb') as f:
        f.write(clean_content)
        
    print(f"Arquivo limpo. Tamanho original: {len(content)}, Novo: {len(clean_content)}")
    
except Exception as e:
    print(f"Erro: {e}")
