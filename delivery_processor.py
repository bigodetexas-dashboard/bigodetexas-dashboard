# Sistema de Processamento de Entregas
import json
import asyncio
from datetime import datetime
import os

def load_json(filename):
    if not os.path.exists(filename):
        return {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def process_pending_deliveries():
    """Processa entregas pendentes e spawna itens no servidor"""
    while True:
        try:
            pending = load_json('pending_deliveries.json')
            now = datetime.now()
            
            deliveries_to_process = []
            
            for delivery_id, delivery in pending.items():
                if delivery['status'] != 'pending':
                    continue
                
                delivery_time = datetime.fromisoformat(delivery['delivery_at'])
                
                # Se já passou o tempo de entrega
                if now >= delivery_time:
                    deliveries_to_process.append((delivery_id, delivery))
            
            # Processar entregas
            for delivery_id, delivery in deliveries_to_process:
                success = await spawn_items_on_server(delivery)
                
                if success:
                    pending[delivery_id]['status'] = 'delivered'
                    pending[delivery_id]['delivered_at'] = now.isoformat()
                    print(f"[DELIVERY] ✅ Entrega {delivery_id} concluída!")
                else:
                    pending[delivery_id]['status'] = 'failed'
                    print(f"[DELIVERY] ❌ Falha na entrega {delivery_id}")
            
            # Salvar atualizações
            if deliveries_to_process:
                save_json('pending_deliveries.json', pending)
            
        except Exception as e:
            print(f"[DELIVERY] Erro ao processar entregas: {e}")
        
        # Verificar a cada 30 segundos
        await asyncio.sleep(30)

async def spawn_items_on_server(delivery):
    """Spawna itens no servidor DayZ via FTP"""
    try:
        import ftplib
        from ftplib import FTP
        
        # Conectar ao servidor FTP
        ftp_host = os.getenv('FTP_HOST')
        ftp_user = os.getenv('FTP_USER')
        ftp_pass = os.getenv('FTP_PASS')
        
        if not all([ftp_host, ftp_user, ftp_pass]):
            print("[DELIVERY] Credenciais FTP não configuradas")
            return False
        
        ftp = FTP(ftp_host)
        ftp.login(ftp_user, ftp_pass)
        
        # Navegar para o diretório de eventos
        ftp.cwd('/config')
        
        # Carregar events.xml
        events_xml = download_events_xml(ftp)
        
        # Adicionar eventos de spawn para cada item
        coords = delivery['coordinates']
        x = coords['x']
        y = coords['y']
        z = 0  # Altura padrão (chão)
        
        for item in delivery['items']:
            code = item['code']
            quantity = item['quantity']
            
            # Adicionar múltiplos spawns se quantidade > 1
            for _ in range(quantity):
                events_xml = add_spawn_event(events_xml, code, x, y, z)
        
        # Upload events.xml atualizado
        upload_events_xml(ftp, events_xml)
        
        ftp.quit()
        
        print(f"[DELIVERY] Itens spawnados em X:{x}, Y:{y}")
        return True
        
    except Exception as e:
        print(f"[DELIVERY] Erro ao spawnar itens: {e}")
        return False

def download_events_xml(ftp):
    """Baixa events.xml do servidor"""
    import io
    bio = io.BytesIO()
    ftp.retrbinary('RETR events.xml', bio.write)
    return bio.getvalue().decode('utf-8')

def upload_events_xml(ftp, content):
    """Upload events.xml para o servidor"""
    import io
    bio = io.BytesIO(content.encode('utf-8'))
    ftp.storbinary('STOR events.xml', bio)

def add_spawn_event(xml_content, item_code, x, y, z):
    """Adiciona evento de spawn ao events.xml"""
    # Criar evento de spawn único
    event = f'''
    <event name="StaticDelivery_{item_code}_{int(datetime.now().timestamp())}">
        <nominal>1</nominal>
        <min>1</min>
        <max>1</max>
        <lifetime>300</lifetime>
        <restock>0</restock>
        <saferadius>0</saferadius>
        <distanceradius>0</distanceradius>
        <cleanupradius>0</cleanupradius>
        <flags deletable="1" init_random="0" remove_damaged="0"/>
        <position>fixed</position>
        <limit>child</limit>
        <active>1</active>
        <children>
            <child lootmax="1" lootmin="1" max="1" min="1" type="{item_code}"/>
        </children>
    </event>
    '''
    
    # Inserir antes do fechamento de </events>
    xml_content = xml_content.replace('</events>', f'{event}\n</events>')
    
    return xml_content

# Iniciar loop de processamento
if __name__ == '__main__':
    asyncio.run(process_pending_deliveries())
