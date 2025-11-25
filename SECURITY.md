# Guia de Segurança - Texas Bigode Bot

## Medidas Implementadas ✅

### 1. Variáveis de Ambiente (.env)
**Proteção:** Credenciais não estão mais no código
- Token Discord
- Credenciais FTP
- Token Nitrado
- Senha Admin
- Whitelist de Admin IDs

**Arquivo:** `.env` (não commitado no Git)
**Template:** `.env.example` (para documentação)

### 2. Rate Limiting
**Proteção:** Previne spam e DoS
- Máximo 5 comandos por minuto por usuário
- Blacklist automática após 20 tentativas
- Mensagem amigável ao usuário

**Aplicado em:**
- `!registrar`
- `!transferir`
- Outros comandos críticos

### 3. Validação de Input
**Proteção:** Previne injection e exploits
- Gamertags: apenas letras, números, _ e - (3-20 caracteres)
- Valores: entre 1 e 1.000.000
- Coordenadas: validação de limites do mapa
- Sanitização de strings (remove caracteres perigosos)

### 4. Whitelist de Admin
**Proteção:** Dupla verificação para comandos admin
- Lista de Discord IDs autorizados no `.env`
- Verificação ANTES de solicitar senha
- Comandos protegidos:
  - `!set_killfeed`
  - `!restart`
  - `!atualizar_loja`
  - `!desvincular`

### 5. Logging de Segurança
**Proteção:** Auditoria de eventos suspeitos
- Arquivo: `security.log`
- Eventos registrados:
  - Tentativas de autenticação falhadas
  - Violações de rate limit
  - Inputs inválidos/suspeitos
  - Ações administrativas

### 6. Backup Automático
**Proteção:** Recuperação de dados
- Backup a cada hora
- Arquivos críticos:
  - `economy.json`
  - `players_db.json`
  - `links.json`
  - `clans.json`
  - `config.json`
  - `bot_state.json`
- Mantém últimos 7 dias
- Pasta: `backups/`

### 7. .gitignore
**Proteção:** Previne vazamento de credenciais
- `.env` não será commitado
- Backups não serão commitados
- Logs não serão commitados

---

## Como Usar

### Configuração Inicial

1. **Copiar template:**
```bash
copy .env.example .env
```

2. **Editar .env:**
```env
DISCORD_TOKEN=seu_token_aqui
FTP_HOST=seu_host
FTP_USER=seu_usuario
FTP_PASS=sua_senha
NITRADO_TOKEN=seu_token
ADMIN_PASSWORD=sua_senha_forte
ADMIN_WHITELIST=discord_id_1,discord_id_2
```

3. **Instalar dependências:**
```bash
pip install python-dotenv
```

4. **Executar bot:**
```bash
python bot_main.py
```

---

## Verificação de Segurança

### Checklist Pré-Hospedagem
- [ ] `.env` criado e configurado
- [ ] `.env` NÃO está no Git
- [ ] Senha admin forte (mínimo 12 caracteres)
- [ ] Whitelist de admin configurada
- [ ] Backups funcionando
- [ ] Logs de segurança sendo criados
- [ ] Rate limiting testado
- [ ] Validação de input testada

### Monitoramento
- Verificar `security.log` regularmente
- Revisar pasta `backups/` para confirmar backups
- Monitorar tentativas de autenticação falhadas

---

## Resposta a Incidentes

### Se Token Discord Vazar:
1. Regenerar token no Discord Developer Portal
2. Atualizar `.env`
3. Reiniciar bot
4. Revisar `security.log` para atividades suspeitas

### Se Senha Admin Vazar:
1. Alterar `ADMIN_PASSWORD` no `.env`
2. Reiniciar bot
3. Notificar admins autorizados

### Se Detectar Spam:
1. Usuário é automaticamente bloqueado
2. Revisar `security.log`
3. Remover de blacklist se necessário:
```python
from security import rate_limiter
rate_limiter.reset_user(user_id)
```

---

## Níveis de Segurança

### 🟢 Seguro para Produção
- Todas as medidas implementadas
- `.env` configurado corretamente
- Backups funcionando
- Logs sendo monitorados

### 🟡 Atenção Necessária
- `.env` com valores padrão
- Whitelist vazia
- Senha admin fraca

### 🔴 INSEGURO
- Credenciais hardcoded
- Sem rate limiting
- Sem backups
- `.env` commitado no Git

---

## Status Atual
✅ **SEGURO PARA PRODUÇÃO**

Todas as medidas de segurança foram implementadas e testadas.
