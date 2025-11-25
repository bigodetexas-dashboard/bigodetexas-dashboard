import json

try:
    with open('items.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("JSON Valido! Categorias encontradas:")
    print(list(data.keys()))
except json.JSONDecodeError as e:
    print(f"Erro no JSON: {e}")
except Exception as e:
    print(f"Erro desconhecido: {e}")
