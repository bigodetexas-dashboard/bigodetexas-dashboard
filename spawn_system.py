"""
Sistema de Admin Spawner - BigodeTexas Bot
============================================

Permite spawnar itens no servidor DayZ via Discord.

Funcionalidades:
- Spawnar itens em coordenadas específicas
- Spawnar itens próximo a jogadores
- Integração com sistema de loja (delivery automático)
- Fila de spawns pendentes
- Backup automático de XMLs

Arquivos manipulados:
- events.xml - Define eventos de spawn
- cfgeventspawns.xml - Define coordenadas de spawn
"""

import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from datetime import datetime
import os
import shutil

# Arquivo de fila de spawns
SPAWN_QUEUE_FILE = "spawn_queue.json"

def create_spawn_event_xml(event_name, item_name, quantity=1, lifetime=3600):
    """
    Cria um elemento XML para events.xml
    
    Args:
        event_name: Nome único do evento (ex: "spawn_m4a1_001")
        item_name: Nome do item DayZ (ex: "M4A1")
        quantity: Quantidade de itens (padrão: 1)
        lifetime: Tempo de vida em segundos (padrão: 1 hora)
    
    Returns:
        ElementTree.Element: Elemento XML do evento
    """
    event = ET.Element("event", name=event_name)
    
    # Nominal - quantos podem existir simultaneamente
    nominal = ET.SubElement(event, "nominal")
    nominal.text = str(quantity)
    
    # Min - mínimo antes de respawn
    min_elem = ET.SubElement(event, "min")
    min_elem.text = "0"
    
    # Max - máximo possível
    max_elem = ET.SubElement(event, "max")
    max_elem.text = str(quantity)
    
    # Lifetime - tempo de vida
    lifetime_elem = ET.SubElement(event, "lifetime")
    lifetime_elem.text = str(lifetime)
    
    # Restock - tempo para respawn (0 = não respawna)
    restock = ET.SubElement(event, "restock")
    restock.text = "0"
    
    # Saferadius - raio seguro
    saferadius = ET.SubElement(event, "saferadius")
    saferadius.text = "0"
    
    # Distanceradius - raio de distância
    distanceradius = ET.SubElement(event, "distanceradius")
    distanceradius.text = "0"
    
    # Cleanupradius - raio de limpeza
    cleanupradius = ET.SubElement(event, "cleanupradius")
    cleanupradius.text = "0"
    
    # Flags - configurações
    flags = ET.SubElement(event, "flags")
    flags.set("deletable", "1")
    flags.set("init_random", "0")
    flags.set("remove_damaged", "0")
    
    # Children - itens do evento
    children = ET.SubElement(event, "children")
    child = ET.SubElement(children, "child")
    child.set("lootmax", "0")
    child.set("lootmin", "0")
    child.set("max", str(quantity))
    child.set("min", str(quantity))
    child.set("type", item_name)
    
    return event

def create_spawn_position_xml(event_name, x, z, rotation=0, a=0):
    """
    Cria um elemento XML para cfgeventspawns.xml
    
    Args:
        event_name: Nome do evento (deve corresponder ao events.xml)
        x: Coordenada X
        z: Coordenada Z
        rotation: Rotação do item (0-360)
        a: Parâmetro adicional (geralmente 0)
    
    Returns:
        ElementTree.Element: Elemento XML da posição
    """
    event = ET.Element("event", name=event_name)
    pos = ET.SubElement(event, "pos")
    pos.text = f"{x} {z}"
    pos.set("a", str(a))
    pos.set("r", str(rotation))
    
    return event

def prettify_xml(elem):
    """
    Formata XML de forma legível
    
    Args:
        elem: ElementTree.Element
    
    Returns:
        str: XML formatado
    """
    rough_string = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")

def backup_xml_file(file_path):
    """
    Cria backup de arquivo XML
    
    Args:
        file_path: Caminho do arquivo
    
    Returns:
        str: Caminho do backup
    """
    if not os.path.exists(file_path):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.backup_{timestamp}"
    shutil.copy2(file_path, backup_path)
    
    return backup_path

def add_spawn_to_events_xml(events_xml_path, event_name, item_name, quantity=1):
    """
    Adiciona evento de spawn ao events.xml
    
    Args:
        events_xml_path: Caminho do events.xml
        event_name: Nome único do evento
        item_name: Nome do item DayZ
        quantity: Quantidade
    
    Returns:
        bool: True se sucesso, False se erro
    """
    try:
        # Backup
        backup_xml_file(events_xml_path)
        
        # Parse XML existente ou cria novo
        if os.path.exists(events_xml_path):
            tree = ET.parse(events_xml_path)
            root = tree.getroot()
        else:
            root = ET.Element("events")
            tree = ET.ElementTree(root)
        
        # Verifica se evento já existe
        for event in root.findall("event"):
            if event.get("name") == event_name:
                print(f"Evento {event_name} já existe, substituindo...")
                root.remove(event)
                break
        
        # Adiciona novo evento
        new_event = create_spawn_event_xml(event_name, item_name, quantity)
        root.append(new_event)
        
        # Salva
        tree.write(events_xml_path, encoding='utf-8', xml_declaration=True)
        
        return True
        
    except Exception as e:
        print(f"Erro ao adicionar spawn ao events.xml: {e}")
        return False

def add_spawn_to_positions_xml(positions_xml_path, event_name, x, z, rotation=0):
    """
    Adiciona posição de spawn ao cfgeventspawns.xml
    
    Args:
        positions_xml_path: Caminho do cfgeventspawns.xml
        event_name: Nome do evento
        x: Coordenada X
        z: Coordenada Z
        rotation: Rotação
    
    Returns:
        bool: True se sucesso, False se erro
    """
    try:
        # Backup
        backup_xml_file(positions_xml_path)
        
        # Parse XML existente ou cria novo
        if os.path.exists(positions_xml_path):
            tree = ET.parse(positions_xml_path)
            root = tree.getroot()
        else:
            root = ET.Element("eventposdef")
            tree = ET.ElementTree(root)
        
        # Verifica se posição já existe
        for event in root.findall("event"):
            if event.get("name") == event_name:
                print(f"Posição para {event_name} já existe, substituindo...")
                root.remove(event)
                break
        
        # Adiciona nova posição
        new_position = create_spawn_position_xml(event_name, x, z, rotation)
        root.append(new_position)
        
        # Salva
        tree.write(positions_xml_path, encoding='utf-8', xml_declaration=True)
        
        return True
        
    except Exception as e:
        print(f"Erro ao adicionar posição ao cfgeventspawns.xml: {e}")
        return False

def create_complete_spawn(events_path, positions_path, item_name, x, z, quantity=1, rotation=0):
    """
    Cria spawn completo (evento + posição)
    
    Args:
        events_path: Caminho do events.xml
        positions_path: Caminho do cfgeventspawns.xml
        item_name: Nome do item
        x: Coordenada X
        z: Coordenada Z
        quantity: Quantidade
        rotation: Rotação
    
    Returns:
        tuple: (sucesso, event_name)
    """
    # Gera nome único do evento
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    event_name = f"spawn_{item_name.lower()}_{timestamp}"
    
    # Adiciona ao events.xml
    if not add_spawn_to_events_xml(events_path, event_name, item_name, quantity):
        return False, None
    
    # Adiciona ao cfgeventspawns.xml
    if not add_spawn_to_positions_xml(positions_path, event_name, x, z, rotation):
        return False, None
    
    return True, event_name

# Funções de gerenciamento de fila

def load_spawn_queue():
    """Carrega fila de spawns pendentes"""
    from bot_main import load_json
    return load_json(SPAWN_QUEUE_FILE)

def save_spawn_queue(queue):
    """Salva fila de spawns"""
    from bot_main import save_json
    save_json(SPAWN_QUEUE_FILE, queue)

def add_to_spawn_queue(item_name, x, z, quantity=1, requested_by=None, gamertag=None):
    """
    Adiciona spawn à fila
    
    Returns:
        str: ID do spawn
    """
    queue = load_spawn_queue()
    
    if "pending_spawns" not in queue:
        queue["pending_spawns"] = []
    
    spawn_id = f"spawn_{len(queue['pending_spawns']) + 1:03d}"
    
    spawn_entry = {
        "id": spawn_id,
        "item": item_name,
        "quantity": quantity,
        "x": x,
        "z": z,
        "rotation": 0,
        "requested_by": requested_by,
        "gamertag": gamertag,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }
    
    queue["pending_spawns"].append(spawn_entry)
    save_spawn_queue(queue)
    
    return spawn_id

def get_pending_spawns():
    """Retorna lista de spawns pendentes"""
    queue = load_spawn_queue()
    return queue.get("pending_spawns", [])

def mark_spawn_processed(spawn_id):
    """Marca spawn como processado"""
    queue = load_spawn_queue()
    
    for spawn in queue.get("pending_spawns", []):
        if spawn["id"] == spawn_id:
            spawn["status"] = "processed"
            spawn["processed_at"] = datetime.now().isoformat()
            break
    
    save_spawn_queue(queue)

def clear_processed_spawns():
    """Remove spawns já processados da fila"""
    queue = load_spawn_queue()
    
    if "pending_spawns" in queue:
        queue["pending_spawns"] = [
            s for s in queue["pending_spawns"] 
            if s.get("status") != "processed"
        ]
    
    save_spawn_queue(queue)
    return len(queue.get("pending_spawns", []))
