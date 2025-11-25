"""
Módulo de Segurança - Texas Bigode Bot
Funções para proteger o bot contra hackers e ataques
"""

import time
import re
import os
import json
import shutil
from datetime import datetime
from collections import defaultdict
from typing import Optional, Dict, List

# --- RATE LIMITING ---
class RateLimiter:
    """Limita comandos por usuário para prevenir spam/DoS"""
    
    def __init__(self, max_calls: int = 5, period: int = 60):
        self.max_calls = max_calls
        self.period = period
        self.calls: Dict[int, List[float]] = defaultdict(list)
        self.blacklist: set = set()
    
    def is_allowed(self, user_id: int) -> bool:
        """Verifica se usuário pode executar comando"""
        if user_id in self.blacklist:
            return False
        
        now = time.time()
        user_calls = self.calls[user_id]
        
        # Remove chamadas antigas
        user_calls[:] = [t for t in user_calls if now - t < self.period]
        
        # Verifica limite
        if len(user_calls) >= self.max_calls:
            # Blacklist se spam excessivo (>20 tentativas)
            if len(user_calls) > 20:
                self.blacklist.add(user_id)
                print(f"[SECURITY] User {user_id} blacklisted for spam")
            return False
        
        # Registra chamada
        user_calls.append(now)
        return True
    
    def reset_user(self, user_id: int):
        """Remove usuário do rate limiter"""
        if user_id in self.calls:
            del self.calls[user_id]
        if user_id in self.blacklist:
            self.blacklist.remove(user_id)

# --- VALIDAÇÃO DE INPUT ---
class InputValidator:
    """Valida e sanitiza inputs de usuários"""
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 100) -> str:
        """Remove caracteres perigosos e limita tamanho"""
        if not text:
            return ""
        
        # Remove caracteres especiais perigosos
        text = re.sub(r'[<>\"\'\\;]', '', text)
        
        # Limita tamanho
        text = text[:max_length]
        
        return text.strip()
    
    @staticmethod
    def validate_gamertag(gamertag: str) -> bool:
        """Valida formato de gamertag"""
        if not gamertag or len(gamertag) < 3 or len(gamertag) > 20:
            return False
        
        # Apenas letras, números, underscore e hífen
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', gamertag))
    
    @staticmethod
    def validate_amount(amount: str) -> Optional[int]:
        """Valida e converte valor numérico"""
        try:
            value = int(amount)
            if value < 0 or value > 1000000:  # Limite de 1 milhão
                return None
            return value
        except ValueError:
            return None
    
    @staticmethod
    def validate_coordinates(x: str, z: str) -> Optional[tuple]:
        """Valida coordenadas do mapa"""
        try:
            x_val = float(x)
            z_val = float(z)
            
            # Limites do mapa Chernarus (aproximado)
            if not (0 <= x_val <= 15360 and 0 <= z_val <= 15360):
                return None
            
            return (x_val, z_val)
        except ValueError:
            return None

# --- LOGGING DE SEGURANÇA ---
class SecurityLogger:
    """Registra eventos de segurança"""
    
    def __init__(self, log_file: str = "security.log"):
        self.log_file = log_file
    
    def log(self, event_type: str, user_id: int, details: str):
        """Registra evento de segurança"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {event_type} | User: {user_id} | {details}\n"
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"[ERROR] Failed to write security log: {e}")
    
    def log_failed_auth(self, user_id: int, command: str):
        """Registra tentativa de autenticação falhada"""
        self.log("FAILED_AUTH", user_id, f"Command: {command}")
    
    def log_rate_limit(self, user_id: int):
        """Registra violação de rate limit"""
        self.log("RATE_LIMIT", user_id, "Too many requests")
    
    def log_invalid_input(self, user_id: int, input_data: str):
        """Registra input inválido/suspeito"""
        self.log("INVALID_INPUT", user_id, f"Input: {input_data[:50]}")
    
    def log_admin_action(self, user_id: int, action: str):
        """Registra ação administrativa"""
        self.log("ADMIN_ACTION", user_id, action)

# --- BACKUP AUTOMÁTICO ---
class BackupManager:
    """Gerencia backups automáticos dos dados"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def backup_file(self, file_path: str) -> bool:
        """Cria backup de um arquivo"""
        if not os.path.exists(file_path):
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.basename(file_path)
            backup_path = os.path.join(self.backup_dir, f"{filename}.{timestamp}.bak")
            
            shutil.copy2(file_path, backup_path)
            print(f"[BACKUP] Created: {backup_path}")
            
            # Limpa backups antigos (mantém últimos 7 dias)
            self.cleanup_old_backups(filename, days=7)
            
            return True
        except Exception as e:
            print(f"[ERROR] Backup failed: {e}")
            return False
    
    def cleanup_old_backups(self, filename: str, days: int = 7):
        """Remove backups mais antigos que X dias"""
        try:
            cutoff_time = time.time() - (days * 86400)
            
            for backup_file in os.listdir(self.backup_dir):
                if not backup_file.startswith(filename):
                    continue
                
                backup_path = os.path.join(self.backup_dir, backup_file)
                if os.path.getmtime(backup_path) < cutoff_time:
                    os.remove(backup_path)
                    print(f"[BACKUP] Removed old backup: {backup_file}")
        except Exception as e:
            print(f"[ERROR] Cleanup failed: {e}")
    
    def backup_all(self, files: List[str]):
        """Cria backup de múltiplos arquivos"""
        for file_path in files:
            self.backup_file(file_path)

# --- WHITELIST DE ADMIN ---
class AdminWhitelist:
    """Gerencia whitelist de administradores"""
    
    def __init__(self, whitelist_ids: List[int]):
        self.whitelist = set(whitelist_ids)
    
    def is_admin(self, user_id: int) -> bool:
        """Verifica se usuário está na whitelist"""
        return user_id in self.whitelist
    
    def add_admin(self, user_id: int):
        """Adiciona usuário à whitelist"""
        self.whitelist.add(user_id)
    
    def remove_admin(self, user_id: int):
        """Remove usuário da whitelist"""
        self.whitelist.discard(user_id)

# --- INSTÂNCIAS GLOBAIS ---
rate_limiter = RateLimiter(max_calls=5, period=60)
input_validator = InputValidator()
security_logger = SecurityLogger()
backup_manager = BackupManager()

# Será inicializado no bot_main.py com IDs do .env
admin_whitelist = None
