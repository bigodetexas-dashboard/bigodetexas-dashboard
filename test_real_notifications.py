"""
Teste REAL de Push Notifications com webhook configurado
"""

import os
import sys

# Adicionar o webhook URL temporariamente para teste
os.environ['NOTIFICATION_WEBHOOK_URL'] = "https://discord.com/api/webhooks/1442958211513585714/VQJUqwLq7jnYbiyFoVqVGEx7jM4HA5wAHh-uReBn-E0xh2fj6_qrb7Yyer0o1de4iRIT"

# Importar o sistema de notificações
from push_notifications import PushNotificationManager

def test_real_notifications():
    """Testa notificações reais no Discord"""
    
    print("\n" + "="*60)
    print("TESTE REAL DE PUSH NOTIFICATIONS")
    print("="*60)
    print("\nEnviando notificacoes para o Discord...")
    print("Verifique o canal configurado!\n")
    
    # Criar gerenciador com webhook real
    notifier = PushNotificationManager(
        webhook_url=os.environ['NOTIFICATION_WEBHOOK_URL']
    )
    
    # Teste 1: Kill
    print("[1/3] Enviando notificacao de Kill...")
    success1 = notifier.notify_player_kill("TestPlayer", "Target123", "M4A1", 450)
    print(f"      {'OK' if success1 else 'FALHOU'}")
    
    # Teste 2: Guerra
    print("[2/3] Enviando atualizacao de Guerra...")
    success2 = notifier.notify_war_update("WOLVES", "BEARS", 7, 5)
    print(f"      {'OK' if success2 else 'FALHOU'}")
    
    # Teste 3: Missão
    print("[3/3] Enviando missao completa...")
    success3 = notifier.notify_mission_complete("TestPlayer", "Cacador (5 kills)", 500)
    print(f"      {'OK' if success3 else 'FALHOU'}")
    
    print("\n" + "="*60)
    if all([success1, success2, success3]):
        print("SUCESSO! Todas as 3 notificacoes foram enviadas!")
        print("Verifique o canal do Discord para ver as mensagens.")
    else:
        print("ATENCAO: Algumas notificacoes falharam.")
        print("Verifique se o webhook URL esta correto.")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_real_notifications()
    except Exception as e:
        print(f"\n[ERRO] Falha no teste: {e}")
        sys.exit(1)
