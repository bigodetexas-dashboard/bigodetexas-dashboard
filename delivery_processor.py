"""
Sistema de Processamento de Entregas - BigodeTexas
Processa entregas pendentes e spawna itens no servidor DayZ
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
import ftplib
import io
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

# Mapeamento de códigos de itens para classes DayZ
ITEM_CLASS_MAP = {
    # Armas
    "m4a1": "M4A1",
    "akm": "AKM",
    "ak74": "AK74",
    "ak101": "AK101",
    "lar": "LAR",
    "aur_ax": "Aug",
    "famas": "Famas",
    "vsd": "SVD",
    "mosin": "Mosin9130",
    "tundra": "Repeater",
    "blaze": "Blaze",
    "savanna": "CR527",
    "vss": "VSS",
    "asval": "ASVAL",
    "ump45": "UMP45",
    "mp5": "MP5K",
    "bizon": "PP19",
    "fx45": "FNX45",
    "deagle": "Deagle",
    "revolver": "Revolver",
    "glock": "Glock19",
    
    # Munições
    "556": "Ammo_556x45",
    "762": "Ammo_762x39",
    "545": "Ammo_545x39",
    "308": "Ammo_308Win",
    "54r": "Ammo_762x54",
    "9x39": "Ammo_9x39",
    "45acp": "Ammo_45ACP",
    "9mm": "Ammo_9x19",
    "357": "Ammo_357",
    "12ga": "Ammo_12gaPellets",
    
    # Médico
    "bandagem": "BandageDressing",
    "tetraciclina": "TetracyclineAntibiotics",
    "multivitaminas": "VitaminBottle",
    "codeina": "PainkillerTablets",
    "carvao": "CharcoalTablets",
    "epinefrina": "Epinephrine",
    "morfina": "Morphine",
    "bolsa_sangue": "BloodBagFull",
    
    # Mochilas
    "mochila_campo": "AliceBag_Camo",
    "mochila_montanha": "MountainBag_Blue",
    "mochila_caca": "HuntingBag",
    "mochila_assalto": "AssaultBag_Black",
    "mochila_coiote": "CoyoteBag_Brown",
    
    # Comidas
    "pessego": "PeachesCan",
    "sardinha": "SardinesCan",
    "feijao": "BakedBeansCan",
    "bacon": "TacticalBaconCan",
    "arroz": "Rice",
    "maca": "Apple",
    "pera": "Pear",
    "agua": "WaterBottle",
    "cantil": "Canteen",
    
    # Veículos
    "vela": "SparkPlug",
    "radiador": "Radiator",
    "bateria_carro": "CarBattery",
    "roda_gunter": "HatchbackWheel",
    "gasolina": "CanisterGasoline",
}

class DeliveryProcessor:
    def __init__(self, ftp_host, ftp_user, ftp_pass, ftp_port=21):
        self.ftp_host = ftp_host
        self.ftp_user = ftp_user
        self.ftp_pass = ftp_pass
        self.ftp_port = ftp_port
        self.queue_file = "delivery_queue.json"
        
    def load_queue(self) -> Dict:
        """Carrega a fila de entregas"""
        if not os.path.exists(self.queue_file):
            return {}
        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_queue(self, queue: Dict):
        """Salva a fila de entregas"""
        with open(self.queue_file, 'w', encoding='utf-8') as f:
            json.dump(queue, f, indent=2, ensure_ascii=False)
    
    def get_pending_deliveries(self) -> List[tuple]:
        """Retorna entregas que atingiram o tempo de entrega"""
        queue = self.load_queue()
        now = datetime.now()
        pending = []
        
        for delivery_id, delivery in queue.items():
            if delivery['status'] != 'pending':
                continue
            
            delivery_time = datetime.fromisoformat(delivery['delivery_at'])
            if now >= delivery_time:
                pending.append((delivery_id, delivery))
        
        return pending
    
    def connect_ftp(self) -> Optional[ftplib.FTP]:
        """Conecta ao servidor FTP"""
        try:
            ftp = ftplib.FTP()
            ftp.connect(self.ftp_host, self.ftp_port)
            ftp.login(self.ftp_user, self.ftp_pass)
            return ftp
        except Exception as e:
            print(f"Erro ao conectar FTP: {e}")
            return None
    
    def spawn_items(self, delivery_id: str, delivery: Dict) -> bool:
        """Spawna os itens no servidor"""
        try:
            ftp = self.connect_ftp()
            if not ftp:
                return False
            
            # Caminho do events.xml
            events_path = "/dayzxb_missions/dayzOffline.chernarusplus/events.xml"
            
            # Baixa o arquivo
            bio = io.BytesIO()
            try:
                ftp.retrbinary(f"RETR {events_path}", bio.write)
            except Exception as e:
                print(f"Erro ao baixar events.xml: {e}")
                ftp.quit()
                return False
            
            # Parseia XML
            bio.seek(0)
            tree = ET.parse(bio)
            root = tree.getroot()
            
            # Adiciona eventos de spawn para cada item
            coords = delivery['coordinates']
            for item in delivery['items']:
                item_class = ITEM_CLASS_MAP.get(item['code'])
                if not item_class:
                    print(f"Item não mapeado: {item['code']}")
                    continue
                
                # Cria evento de spawn para cada quantidade
                for _ in range(item['quantity']):
                    event = ET.SubElement(root, 'event')
                    event.set('name', f"Delivery_{delivery_id}_{item['code']}")
                    
                    ET.SubElement(event, 'nominal').text = '1'
                    ET.SubElement(event, 'min').text = '1'
                    ET.SubElement(event, 'max').text = '1'
                    ET.SubElement(event, 'lifetime').text = '3600'  # 1 hora
                    ET.SubElement(event, 'restock').text = '0'
                    ET.SubElement(event, 'saferadius').text = '0'
                    ET.SubElement(event, 'distanceradius').text = '0'
                    ET.SubElement(event, 'cleanupradius').text = '0'
                    
                    # Posição específica
                    pos = ET.SubElement(event, 'pos')
                    pos.set('x', str(coords['x']))
                    pos.set('z', str(coords['z']))
                    
                    # Tipo de item
                    ET.SubElement(event, 'type').text = item_class
            
            # Salva XML modificado
            xml_str = ET.tostring(root, encoding='utf-8')
            bio = io.BytesIO(xml_str)
            
            # Upload do arquivo
            try:
                ftp.storbinary(f"STOR {events_path}", bio)
                print(f"✅ Entrega {delivery_id} processada com sucesso!")
            except Exception as e:
                print(f"Erro ao fazer upload do events.xml: {e}")
                ftp.quit()
                return False
            
            ftp.quit()
            return True
            
        except Exception as e:
            print(f"Erro ao spawnar itens: {e}")
            return False
    
    def process_deliveries(self):
        """Processa todas as entregas pendentes"""
        pending = self.get_pending_deliveries()
        
        if not pending:
            return
        
        print(f"📦 Processando {len(pending)} entregas pendentes...")
        
        queue = self.load_queue()
        
        for delivery_id, delivery in pending:
            print(f"Processando entrega {delivery_id}...")
            
            # Atualiza status
            queue[delivery_id]['status'] = 'processing'
            self.save_queue(queue)
            
            # Tenta spawnar itens
            success = self.spawn_items(delivery_id, delivery)
            
            if success:
                queue[delivery_id]['status'] = 'completed'
                queue[delivery_id]['completed_at'] = datetime.now().isoformat()
                print(f"✅ Entrega {delivery_id} concluída!")
                # TODO: Enviar notificação Discord
            else:
                queue[delivery_id]['status'] = 'failed'
                queue[delivery_id]['error'] = 'Erro ao spawnar itens'
                print(f"❌ Falha na entrega {delivery_id}")
            
            self.save_queue(queue)

# Função para ser chamada pelo bot
def process_pending_deliveries():
    """Processa entregas pendentes (chamada pelo bot)"""
    from dotenv import load_dotenv
    load_dotenv()
    
    processor = DeliveryProcessor(
        ftp_host=os.getenv("FTP_HOST"),
        ftp_user=os.getenv("FTP_USER"),
        ftp_pass=os.getenv("FTP_PASS"),
        ftp_port=int(os.getenv("FTP_PORT", "21"))
    )
    
    processor.process_deliveries()

if __name__ == "__main__":
    # Teste
    process_pending_deliveries()
