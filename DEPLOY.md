# 🚀 BigodeTexas Bot - Guia de Deploy e Produção

## 📋 Pré-requisitos

### Sistema

- Windows Server 2019+ ou Windows 10/11
- Python 3.10 ou superior
- 2GB RAM mínimo (4GB recomendado)
- 10GB espaço em disco

### Contas e Acessos

- [ ] Token do Discord Bot
- [ ] Credenciais FTP do servidor Nitrado
- [ ] Token da API Nitrado
- [ ] Servidor DayZ Xbox configurado

---

## 🔧 Configuração Inicial

### 1. Instalar Dependências

```bash
pip install discord.py aiohttp flask matplotlib pillow requests
```

### 2. Configurar Variáveis de Ambiente

Crie o arquivo `.env` na raiz do projeto:

```env
# Discord
DISCORD_TOKEN=seu_token_aqui
ADMIN_PASSWORD=sua_senha_admin

# FTP
FTP_HOST=seu_host.nitrado.net
FTP_PORT=21
FTP_USER=seu_usuario
FTP_PASS=sua_senha

# Nitrado API
NITRADO_TOKEN=seu_token_nitrado
SERVER_ID=seu_server_id

# Dashboard
DASHBOARD_PORT=5000
DASHBOARD_HOST=0.0.0.0

# Segurança
ADMIN_WHITELIST=123456789,987654321
RATE_LIMIT_ENABLED=true
```

### 3. Verificar Configurações

Execute o teste de configuração:

```bash
python test_suite.py
```

Resultado esperado: **28/28 testes passando (100%)**

---

## 🚀 Deploy em Produção

### Opção 1: Servidor Local/VPS

#### Passo 1: Preparar Ambiente

```bash
# Criar diretório de produção
mkdir C:\BigodeTexas
cd C:\BigodeTexas

# Copiar arquivos do projeto
xcopy /E /I "d:\dayz xbox\BigodeBot\*" "C:\BigodeTexas\"
```

#### Passo 2: Configurar Serviços

**Bot Discord (Serviço Windows):**

1. Criar `start_bot_service.bat`:

```batch
@echo off
cd C:\BigodeTexas
python bot_main.py
```

2. Usar NSSM para criar serviço:

```bash
nssm install BigodeTexasBot "C:\BigodeTexas\start_bot_service.bat"
nssm set BigodeTexasBot AppDirectory "C:\BigodeTexas"
nssm start BigodeTexasBot
```

**Dashboard Web:**

1. Criar `start_dashboard_service.bat`:

```batch
@echo off
cd C:\BigodeTexas
python web_dashboard.py
```

2. Criar serviço:

```bash
nssm install BigodeTexasDashboard "C:\BigodeTexas\start_dashboard_service.bat"
nssm set BigodeTexasDashboard AppDirectory "C:\BigodeTexas"
nssm start BigodeTexasDashboard
```

---

## 📊 Monitoramento

### 1. Logs

Criar pasta de logs:

```bash
mkdir C:\BigodeTexas\logs
```

Configurar logging no `bot_main.py`:

```python
import logging
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

### 2. Health Check

Criar `health_check.py`:

```python
import requests
import time

def check_bot():
    # Verificar se bot está respondendo
    pass

def check_dashboard():
    try:
        r = requests.get('http://localhost:5000/api/stats', timeout=5)
        return r.status_code == 200
    except:
        return False

while True:
    if not check_dashboard():
        print("ALERT: Dashboard offline!")
    time.sleep(300)  # Check every 5 minutes
```

### 3. Uptime Monitoring

Use ferramentas como:

- **UptimeRobot** (gratuito)
- **Pingdom**
- **StatusCake**

Configure para monitorar:

- `http://seu-ip:5000` (Dashboard)
- Discord Bot status (via webhook)

---

## 💾 Backup Automático

### Script de Backup Diário

Criar `backup_daily.bat`:

```batch
@echo off
set BACKUP_DIR=C:\BigodeTexas\backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%
mkdir %BACKUP_DIR%

echo Criando backup...
xcopy /E /I C:\BigodeTexas\*.json %BACKUP_DIR%\
xcopy /E /I C:\BigodeTexas\logs %BACKUP_DIR%\logs\

echo Backup concluido: %BACKUP_DIR%
```

### Agendar no Windows Task Scheduler

```bash
schtasks /create /tn "BigodeTexas Backup" /tr "C:\BigodeTexas\backup_daily.bat" /sc daily /st 03:00
```

---

## 🔒 Segurança em Produção

### 1. Firewall

Abrir apenas portas necessárias:

```bash
# Dashboard (se público)
netsh advfirewall firewall add rule name="BigodeTexas Dashboard" dir=in action=allow protocol=TCP localport=5000

# Bloquear acesso externo se local
netsh advfirewall firewall add rule name="Block Dashboard External" dir=in action=block protocol=TCP localport=5000 remoteip=0.0.0.0-255.255.255.255
```

### 2. Rate Limiting

Já implementado no `security.py`. Verificar configuração:

- Max 5 comandos por minuto por usuário
- Cooldown de 60 segundos em caso de spam

### 3. Validação de Inputs

Todas as entradas são validadas via `security.py`:

- Sanitização de SQL injection
- Validação de tipos
- Whitelist de comandos admin

---

## 📈 Otimização de Performance

### 1. Banco de Dados

Considerar migrar de JSON para SQLite para melhor performance:

```python
# Futuro: Migração para SQLite
import sqlite3
conn = sqlite3.connect('bigodetexas.db')
```

### 2. Cache

Implementar cache para API:

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=128)
def get_stats_cached():
    return load_json('players_db.json')
```

### 3. CDN para Assets

Se dashboard for público, usar CDN para:

- Chart.js
- Fontes Google
- Imagens estáticas

---

## 🔄 Atualização e Manutenção

### Processo de Atualização

1. **Backup antes de atualizar:**

```bash
backup_daily.bat
```

2. **Parar serviços:**

```bash
nssm stop BigodeTexasBot
nssm stop BigodeTexasDashboard
```

3. **Atualizar código:**

```bash
git pull origin main
# ou copiar novos arquivos
```

4. **Executar testes:**

```bash
python test_suite.py
```

5. **Reiniciar serviços:**

```bash
nssm start BigodeTexasBot
nssm start BigodeTexasDashboard
```

### Rollback

Se algo der errado:

```bash
# Parar serviços
nssm stop BigodeTexasBot
nssm stop BigodeTexasDashboard

# Restaurar backup
xcopy /E /Y C:\BigodeTexas\backups\YYYYMMDD\*.json C:\BigodeTexas\

# Reiniciar
nssm start BigodeTexasBot
nssm start BigodeTexasDashboard
```

---

## 📞 Suporte e Troubleshooting

### Problemas Comuns

**Bot não inicia:**

- Verificar TOKEN no `.env`
- Verificar logs em `logs/bot.log`
- Testar conexão: `python -c "import discord; print('OK')"`

**Dashboard não carrega:**

- Verificar porta 5000 disponível: `netstat -an | findstr 5000`
- Verificar firewall
- Testar: `curl http://localhost:5000`

**API não responde:**

- Verificar arquivos JSON existem
- Executar `test_suite.py`
- Verificar permissões de arquivo

### Comandos Úteis

```bash
# Ver status dos serviços
nssm status BigodeTexasBot
nssm status BigodeTexasDashboard

# Ver logs em tempo real
tail -f logs/bot.log

# Reiniciar tudo
nssm restart BigodeTexasBot
nssm restart BigodeTexasDashboard
```

---

## ✅ Checklist de Deploy

- [ ] Dependências instaladas
- [ ] `.env` configurado
- [ ] Testes passando (28/28)
- [ ] Serviços Windows criados
- [ ] Backup automático configurado
- [ ] Monitoramento ativo
- [ ] Firewall configurado
- [ ] Logs funcionando
- [ ] Health check rodando
- [ ] Documentação revisada

---

## 🎉 Deploy Completo

Após seguir todos os passos, seu BigodeTexas Bot estará rodando em produção de forma estável e segura!

**Próximos passos:**

- Monitorar logs nas primeiras 24h
- Ajustar rate limits conforme necessário
- Configurar alertas de uptime
- Fazer backup manual semanal

---

*BigodeTexas Bot - Production Ready! 🚀*
