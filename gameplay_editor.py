"""
Sistema de Editor de Gameplay - BigodeTexas Bot
=================================================

Permite modificar cfggameplay.json via Discord.

Funcionalidades:
- Visualizar configurações atuais
- Editar valores específicos
- Backup automático antes de modificar
- Validação de tipos e ranges
- Upload para servidor via FTP
- Restaurar backups
"""

import json
import os
import shutil
from datetime import datetime

GAMEPLAY_FILE = "cfggameplay.json"
GAMEPLAY_BACKUP_DIR = "backups/gameplay"

# Mapeamento de categorias e seus parâmetros editáveis
EDITABLE_PARAMS = {
    "Buffs": {
        "HealthRegen": {"type": "float", "min": 0.1, "max": 10.0, "desc": "Regeneração de vida"},
        "BloodRegen": {"type": "float", "min": 0.1, "max": 10.0, "desc": "Regeneração de sangue"},
        "ShockRegen": {"type": "float", "min": 0.1, "max": 10.0, "desc": "Regeneração de shock"},
        "FoodConsumption": {"type": "float", "min": 0.1, "max": 5.0, "desc": "Consumo de comida"},
        "WaterConsumption": {"type": "float", "min": 0.1, "max": 5.0, "desc": "Consumo de água"},
        "ClothingDamageMultiplier": {"type": "float", "min": 0.0, "max": 5.0, "desc": "Dano em roupas"},
        "SwimStaminaCost": {"type": "float", "min": 0.1, "max": 5.0, "desc": "Custo de stamina ao nadar"}
    },
    "GeneralData": {
        "disableBaseDamage": {"type": "bool", "desc": "Desabilitar dano em bases"},
        "disableContainerDamage": {"type": "bool", "desc": "Desabilitar dano em containers"},
        "disableRespawnDialog": {"type": "bool", "desc": "Desabilitar diálogo de respawn"},
        "disableRespawnInUnconsciousness": {"type": "bool", "desc": "Desabilitar respawn inconsciente"}
    },
    "BaseBuildingData.ConstructionDecayData": {
        "enableBaseDecay": {"type": "int", "min": 0, "max": 1, "desc": "Ativar decay de base (0/1)"},
        "decayTimeMinutes": {"type": "int", "min": 1, "max": 525600, "desc": "Tempo de decay (minutos)"},
        "refreshFlagDecayTimeMinutes": {"type": "int", "min": 1, "max": 525600, "desc": "Tempo refresh flag (minutos)"}
    },
    "WorldsData.WeatherData": {
        "overcast": {"type": "float", "min": 0.0, "max": 1.0, "desc": "Nuvens (0-1)"},
        "rain": {"type": "float", "min": 0.0, "max": 1.0, "desc": "Chuva (0-1)"},
        "fog": {"type": "float", "min": 0.0, "max": 1.0, "desc": "Neblina (0-1)"},
        "wind": {"type": "float", "min": 0.0, "max": 1.0, "desc": "Vento (0-1)"}
    }
}

def load_gameplay_config():
    """Carrega cfggameplay.json"""
    if not os.path.exists(GAMEPLAY_FILE):
        return None
    
    with open(GAMEPLAY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_gameplay_config(config):
    """Salva cfggameplay.json"""
    with open(GAMEPLAY_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)

def backup_gameplay_config():
    """Cria backup do cfggameplay.json"""
    if not os.path.exists(GAMEPLAY_FILE):
        return None
    
    # Cria diretório de backup se não existir
    os.makedirs(GAMEPLAY_BACKUP_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(GAMEPLAY_BACKUP_DIR, f"cfggameplay_{timestamp}.json")
    
    shutil.copy2(GAMEPLAY_FILE, backup_path)
    return backup_path

def get_nested_value(config, path):
    """
    Obtém valor de caminho aninhado
    Ex: "BaseBuildingData.ConstructionDecayData.enableBaseDecay"
    """
    keys = path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    
    return value

def set_nested_value(config, path, value):
    """
    Define valor em caminho aninhado
    Ex: "BaseBuildingData.ConstructionDecayData.enableBaseDecay" = 1
    """
    keys = path.split('.')
    current = config
    
    # Navega até o penúltimo nível
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Define o valor final
    current[keys[-1]] = value
    return config

def validate_value(param_info, value_str):
    """
    Valida e converte valor baseado no tipo
    
    Returns:
        tuple: (sucesso, valor_convertido, mensagem_erro)
    """
    param_type = param_info["type"]
    
    try:
        if param_type == "bool":
            if value_str.lower() in ["true", "1", "yes", "sim"]:
                return True, True, None
            elif value_str.lower() in ["false", "0", "no", "não", "nao"]:
                return True, False, None
            else:
                return False, None, "Valor booleano inválido! Use: true/false, 1/0, yes/no"
        
        elif param_type == "int":
            value = int(value_str)
            if "min" in param_info and value < param_info["min"]:
                return False, None, f"Valor muito baixo! Mínimo: {param_info['min']}"
            if "max" in param_info and value > param_info["max"]:
                return False, None, f"Valor muito alto! Máximo: {param_info['max']}"
            return True, value, None
        
        elif param_type == "float":
            value = float(value_str)
            if "min" in param_info and value < param_info["min"]:
                return False, None, f"Valor muito baixo! Mínimo: {param_info['min']}"
            if "max" in param_info and value > param_info["max"]:
                return False, None, f"Valor muito alto! Máximo: {param_info['max']}"
            return True, value, None
        
        else:
            return True, value_str, None
            
    except ValueError:
        return False, None, f"Tipo inválido! Esperado: {param_type}"

def get_category_params(category):
    """Retorna parâmetros de uma categoria"""
    return EDITABLE_PARAMS.get(category, {})

def find_param_category(param_name):
    """Encontra categoria de um parâmetro"""
    for category, params in EDITABLE_PARAMS.items():
        if param_name in params:
            return category, params[param_name]
    return None, None

def list_all_categories():
    """Lista todas as categorias editáveis"""
    return list(EDITABLE_PARAMS.keys())

def get_latest_backup():
    """Retorna o backup mais recente"""
    if not os.path.exists(GAMEPLAY_BACKUP_DIR):
        return None
    
    backups = [f for f in os.listdir(GAMEPLAY_BACKUP_DIR) if f.endswith('.json')]
    if not backups:
        return None
    
    backups.sort(reverse=True)
    return os.path.join(GAMEPLAY_BACKUP_DIR, backups[0])

def restore_backup(backup_path):
    """Restaura um backup"""
    if not os.path.exists(backup_path):
        return False
    
    shutil.copy2(backup_path, GAMEPLAY_FILE)
    return True

def format_param_info(param_name, param_info, current_value):
    """Formata informações de um parâmetro para exibição"""
    info = f"**{param_name}**\n"
    info += f"📝 {param_info['desc']}\n"
    info += f"🔧 Tipo: `{param_info['type']}`\n"
    
    if "min" in param_info and "max" in param_info:
        info += f"📊 Range: `{param_info['min']}` - `{param_info['max']}`\n"
    
    info += f"💾 Atual: `{current_value}`"
    
    return info
