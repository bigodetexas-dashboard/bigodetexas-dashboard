"""
Push Notification System for BigodeTexas Bot
Envia notificações em tempo real via Discord Webhooks
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class PushNotificationManager:
    """Gerenciador de notificações push"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.notification_queue = []
        
    def send_notification(self, title: str, message: str, color: int = 0xf59e0b, 
                         fields: List[Dict] = None, urgent: bool = False):
        """
        Envia notificação push via Discord Webhook
        
        Args:
            title: Título da notificação
            message: Mensagem principal
            color: Cor do embed (hex)
            fields: Campos adicionais
            urgent: Se True, menciona @everyone
        """
        if not self.webhook_url:
            print("[WARN] Webhook URL not configured")
            return False
            
        embed = {
            "title": f"🔔 {title}",
            "description": message,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "BigodeTexas Notifications"
            }
        }
        
        if fields:
            embed["fields"] = fields
            
        payload = {
            "embeds": [embed]
        }
        
        if urgent:
            payload["content"] = "@everyone"
            
        try:
            response = requests.post(self.webhook_url, json=payload)
            return response.status_code == 204
        except Exception as e:
            print(f"[ERROR] Failed to send notification: {e}")
            return False
    
    def notify_player_kill(self, killer: str, victim: str, weapon: str, distance: int):
        """Notificação de kill importante"""
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
        """Notificação de atualização de guerra"""
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
        """Notificação de missão completa"""
        self.send_notification(
            title="Missão Completa!",
            message=f"**{player}** completou: {mission}",
            color=0x10b981,
            fields=[
                {"name": "Recompensa", "value": f"{reward} DZ Coins", "inline": True}
            ]
        )
    
    def notify_server_restart(self, minutes: int):
        """Notificação de reinício do servidor"""
        self.send_notification(
            title="⚠️ REINÍCIO DO SERVIDOR",
            message=f"O servidor será reiniciado em **{minutes} minutos**!",
            color=0xef4444,
            urgent=True
        )
    
    def notify_achievement(self, player: str, achievement: str):
        """Notificação de conquista desbloqueada"""
        self.send_notification(
            title="🏆 Nova Conquista!",
            message=f"**{player}** desbloqueou: {achievement}",
            color=0x8b5cf6
        )
    
    def notify_clan_war_started(self, clan1: str, clan2: str):
        """Notificação de início de guerra"""
        self.send_notification(
            title="⚔️ GUERRA DECLARADA!",
            message=f"**{clan1}** vs **{clan2}**\nA guerra começou!",
            color=0xef4444,
            urgent=True
        )
    
    def notify_leaderboard_change(self, player: str, position: int, category: str):
        """Notificação de mudança no ranking"""
        self.send_notification(
            title="📊 Novo Líder!",
            message=f"**{player}** agora é #{position} em {category}!",
            color=0xf59e0b
        )

# Exemplo de uso
if __name__ == "__main__":
    # Configurar com seu webhook
    notifier = PushNotificationManager(webhook_url="SEU_WEBHOOK_URL_AQUI")
    
    # Testar notificações
    notifier.notify_player_kill("Player1", "Player2", "M4A1", 350)
    notifier.notify_war_update("CLAN1", "CLAN2", 5, 3)
    notifier.notify_mission_complete("Player1", "Caçador", 500)
    
    print("Notificações de teste enviadas!")
