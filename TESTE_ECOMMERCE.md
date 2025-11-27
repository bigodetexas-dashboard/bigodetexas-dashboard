# Guia de Teste - Sistema E-commerce BigodeTexas

## ✅ Problema Corrigido

**Erro**: Função `api_user_balance` duplicada causando erro de endpoint
**Solução**: Removida a duplicata do `web_dashboard.py`
**Status**: ✅ Site funcionando corretamente

## 🧪 Como Testar Localmente

### 1. Iniciar o Bot

```bash
cd "d:\dayz xbox\BigodeBot"
python bot_main.py
```

### 2. Acessar o Site

Abra o navegador em: `http://localhost:3000/shop`

### 3. Testar Fluxo Completo

#### Passo 1: Login

- Faça login com Discord OAuth
- Verifique se o saldo aparece no header

#### Passo 2: Navegar Categorias

- Clique nas abas de categorias
- Verifique se os itens aparecem corretamente
- Teste todas as 11 categorias

#### Passo 3: Adicionar ao Carrinho

- Clique em "Adicionar" em alguns itens
- Verifique se o contador do carrinho aumenta
- Abra o carrinho (ícone no header)
- Teste os botões +/- de quantidade
- Teste remover item

#### Passo 4: Checkout

- Clique em "Finalizar Compra"
- Verifique o resumo do pedido
- Clique no mapa para selecionar coordenadas
- OU digite coordenadas manualmente (ex: X: 7500, Z: 5500)
- Verifique se o marcador aparece no mapa
- Clique em "Confirmar Pedido"

#### Passo 5: Confirmação

- Verifique a animação de sucesso
- Veja a contagem regressiva de 5 minutos
- Verifique o mini-mapa com o marcador

### 4. Verificar Entrega

Após 5 minutos, verifique o arquivo de fila:

```bash
cat delivery_queue.json
```

Para processar manualmente (teste):

```bash
python delivery_processor.py
```

## 📋 Checklist de Verificação

- [ ] Site carrega sem erros
- [ ] Login OAuth funciona
- [ ] Saldo aparece corretamente
- [ ] Todas as 11 categorias funcionam
- [ ] Carrinho adiciona/remove itens
- [ ] Contador do carrinho atualiza
- [ ] Checkout mostra resumo correto
- [ ] Mapa permite selecionar coordenadas
- [ ] Marcador aparece no mapa
- [ ] Compra deduz saldo
- [ ] Pedido é salvo na fila
- [ ] Página de confirmação aparece
- [ ] Contagem regressiva funciona

## 🐛 Possíveis Problemas

### Site não carrega

```bash
# Verificar se o bot está rodando
# Verificar porta 3000 não está em uso
netstat -ano | findstr :3000
```

### Erro 404 nas rotas

```bash
# Verificar se o Blueprint está registrado
python -c "from web_dashboard import dashboard_bp; print('OK')"
```

### Itens não aparecem

```bash
# Verificar items.json
python -c "import json; print(len(json.load(open('items.json'))))"
```

### Erro de autenticação

- Verificar se `DISCORD_CLIENT_ID` e `DISCORD_CLIENT_SECRET` estão no `.env`
- Verificar se `DISCORD_REDIRECT_URI` está correto

## 🚀 Deploy no Render

Após testar localmente, faça commit e push:

```bash
git add .
git commit -m "Sistema de e-commerce completo implementado"
git push origin main
```

No Render:

1. Aguarde o deploy automático
2. Acesse: `https://seu-app.onrender.com/shop`
3. Teste o fluxo completo

## 📝 Notas Importantes

- **Tempo de Entrega**: Fixo em 5 minutos após compra
- **Coordenadas**: Devem estar entre 0-15360 (limites de Chernarus)
- **Saldo**: Verificado automaticamente antes da compra
- **Fila**: Processada a cada minuto pelo bot (quando integrado)
