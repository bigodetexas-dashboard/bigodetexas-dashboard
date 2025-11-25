"""
Script de teste para Push Notifications
Versão simplificada para teste sem webhook
"""

import json
from datetime import datetime

class MockNotificationManager:
    """Versão de teste sem webhook real"""
    
    def __init__(self):
        self.notifications_sent = []
        
    def send_notification(self, title: str, message: str, color: int = 0xf59e0b, 
                         fields: list = None, urgent: bool = False):
        """Simula envio de notificação"""
        notification = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "color": hex(color),
            "urgent": urgent,
            "fields": fields or []
        }
        
        self.notifications_sent.append(notification)
        
        print(f"\n{'='*60}")
        print(f"NOTIFICACAO: {title}")
        print(f"{'='*60}")
        print(f"Mensagem: {message}")
        if fields:
            print("\nDetalhes:")
            for field in fields:
                print(f"  - {field['name']}: {field['value']}")
        if urgent:
            print("\nURGENTE - @everyone mencionado")
        print(f"{'='*60}\n")
        
        return True
    
    def notify_player_kill(self, killer: str, victim: str, weapon: str, distance: int):
        """Notificação de kill"""
        self.send_notification(
            title="PvP Kill",
            message=f"**{killer}** eliminou **{victim}**",
            color=0xef4444,
            fields=[
                {"name": "Arma", "value": weapon, "inline": True},
                {"name": "Distância", "value": f"{distance}m", "inline": True}
            ]
        )
    
    def notify_war_update(self, clan1: str, clan2: str, score1: int, score2: int):
        """Notificação de guerra"""
        self.send_notification(
            title="Guerra de Clãs - Atualização",
            message=f"**{clan1}** vs **{clan2}**",
            color=0xf59e0b,
            fields=[
                {"name": clan1, "value": str(score1), "inline": True},
                {"name": clan2, "value": str(score2), "inline": True}
            ]
        )
    
    def notify_mission_complete(self, player: str, mission: str, reward: int):
        """Notificação de missão"""
        self.send_notification(
            title="Missão Completa!",
            message=f"**{player}** completou: {mission}",
            color=0x10b981,
            fields=[
                {"name": "Recompensa", "value": f"{reward} DZ Coins", "inline": True}
            ]
        )
    
    def save_report(self):
        """Salva relatório de notificações"""
        with open('notifications_test_report.json', 'w', encoding='utf-8') as f:
            json.dump({
                'total_sent': len(self.notifications_sent),
                'notifications': self.notifications_sent
            }, f, indent=4, ensure_ascii=False)
        
        print(f"\nRelatorio salvo em: notifications_test_report.json")
        print(f"Total de notificacoes testadas: {len(self.notifications_sent)}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTE DE PUSH NOTIFICATIONS - BigodeTexas Bot")
    print("="*60)
    print("\nModo: SIMULACAO (sem webhook real)")
    print("Para usar webhook real, configure NOTIFICATION_WEBHOOK_URL no .env\n")
    
    # Criar gerenciador de teste
    notifier = MockNotificationManager()
    
    # Teste 1: Kill
    print("\n[TESTE 1] Notificacao de Kill")
    notifier.notify_player_kill("JogadorPro", "Noob123", "M4A1", 350)
    
    # Teste 2: Guerra
    print("\n[TESTE 2] Atualizacao de Guerra")
    notifier.notify_war_update("WOLVES", "BEARS", 5, 3)
    
    # Teste 3: Missão
    print("\n[TESTE 3] Missao Completa")
    notifier.notify_mission_complete("JogadorPro", "Cacador (5 kills)", 500)
    
    # Salvar relatório
    notifier.save_report()
    
    print("\n" + "="*60)
    print("TODOS OS TESTES CONCLUIDOS!")
    print("="*60)
    print("\nProximos passos:")
    print("1. Configure NOTIFICATION_WEBHOOK_URL no .env")
    print("2. Execute: python push_notifications.py")
    print("3. Verifique as notificacoes no Discord\n")
