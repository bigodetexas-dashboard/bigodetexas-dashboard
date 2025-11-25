# Guia de Hospedagem Local - Texas Bigode Bot

## Hospedagem Local (Windows)

### Passo 1: Configurar .env
```bash
# Copiar template
copy .env.example .env

# Editar .env com suas credenciais
notepad .env
```

### Passo 2: Atualizar .env
Certifique-se de que o `.env` tem o logo correto:
```env
FOOTER_ICON=https://cdn.discordapp.com/attachments/1442262893188878496/1442286419539394682/logo_texas.png
```

### Passo 3: Executar Bot
```bash
# Opção 1: Usar script automático
start_bot.bat

# Opção 2: Executar manualmente
python bot_main.py
```

### Passo 4: Manter Bot Online 24/7

#### Opção A: Deixar PC Ligado
- Desabilitar suspensão automática
- Configurar energia para "Alto Desempenho"
- Deixar terminal aberto

#### Opção B: Usar Task Scheduler (Windows)
1. Abrir "Agendador de Tarefas"
2. Criar Tarefa Básica
3. Configurar para executar no login
4. Ação: `python.exe`
5. Argumentos: `bot_main.py`
6. Diretório: `d:\dayz xbox\BigodeBot`

#### Opção C: Usar NSSM (Serviço Windows)
```bash
# Baixar NSSM de https://nssm.cc/download
nssm install TexasBigodeBot

# Configurar:
# Path: C:\Users\Wellyton\AppData\Local\Programs\Python\Python312\python.exe
# Startup directory: d:\dayz xbox\BigodeBot
# Arguments: bot_main.py
```

---

## Monitoramento

### Verificar Status
- Bot online: Aparece online no Discord
- Logs: Verificar terminal para erros
- Security Log: `security.log`
- Backups: Pasta `backups/`

### Comandos de Teste
```
!saldo - Testar economia
!loja - Testar paginação
!conquistas - Testar sistema de conquistas
```

---

## Troubleshooting

### Bot não inicia
1. Verificar `.env` configurado
2. Verificar token Discord válido
3. Verificar Python instalado
4. Verificar dependências: `pip install -r requirements.txt`

### Bot desconecta
1. Verificar conexão internet
2. Verificar token não expirado
3. Verificar logs para erros

### Comandos não funcionam
1. Verificar permissões do bot no Discord
2. Verificar `Intents` habilitados no Discord Developer Portal
3. Verificar logs de segurança

---

## Próximos Passos

### Para Hospedagem Profissional
Veja `hosting_guide.md` para opções de VPS e cloud.

### Recomendações
- ✅ Backup diário manual
- ✅ Monitorar `security.log`
- ✅ Atualizar senha admin periodicamente
- ✅ Revisar whitelist de admin
