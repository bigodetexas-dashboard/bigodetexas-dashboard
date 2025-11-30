# 🗺️ Heatmap PvP - Guia de Uso Completo

## Arquitetura Implementada (100% ChatGPT)

Este sistema implementa **exatamente** a arquitetura sugerida pelo ChatGPT para um Heatmap PvP profissional.

### Componentes

1. **Banco de Dados** (`database.py`)
   - SQLite com tabela `events`
   - Índices otimizados para performance
   - Grid Clustering (agregação inteligente)
   - Parser de logs RPT

2. **Backend API** (`new_dashboard/app.py`)
   - `/api/heatmap` - Retorna dados agregados
   - `/api/parse_log` - Recebe logs via POST

3. **Frontend** (`new_dashboard/templates/heatmap.html` + `static/js/heatmap.js`)
   - Leaflet + Heatmap.js
   - Conversão precisa de coordenadas
   - Filtros de tempo (24h, 7d, all)

4. **Integração Nitrado** (`nitrado_to_heatmap.py`)
   - Lê logs RPT via FTP
   - Envia para API automaticamente

---

## Como Usar

### 1. Testar com Dados Simulados (Já Funciona)

O banco de dados já foi criado com 150 eventos de teste.

```bash
# Iniciar o servidor Flask
cd "d:/dayz xbox/BigodeBot/new_dashboard"
python app.py
```

Acesse: `http://localhost:5001/heatmap`

Você verá manchas de calor em:

- **NWAF** (100 mortes)
- **Cherno** (50 mortes)

---

### 2. Testar a API Manualmente

#### Buscar dados do heatmap

```bash
curl "http://localhost:5001/api/heatmap?range=24h&grid=50"
```

#### Enviar logs manualmente

```bash
curl -X POST http://localhost:5001/api/parse_log \
  -H "Content-Type: application/json" \
  -d '{"text": "PlayerKill: Killer=John, Victim=Mike, Pos=<4500, 0, 10000>, Weapon=M4A1, Distance=120m"}'
```

---

### 3. Integrar com Nitrado (Dados Reais)

#### Passo 1: Configurar credenciais FTP

Adicione no arquivo `.env`:

```env
NITRADO_FTP_HOST=ftp.nitrado.net
NITRADO_FTP_USER=seu_usuario
NITRADO_FTP_PASS=sua_senha
```

#### Passo 2: Ajustar caminho do log

Edite `nitrado_to_heatmap.py` linha 15:

```python
NITRADO_LOG_PATH = '/games/ni123456_1/noftp/dayzxb/config-1/profiles/'
```

Substitua `ni123456_1` pelo ID do seu servidor.

#### Passo 3: Rodar o integrador

```bash
python nitrado_to_heatmap.py
```

Ele vai:

1. Conectar no FTP da Nitrado
2. Baixar o arquivo `.rpt` mais recente
3. Extrair eventos de morte
4. Enviar para `/api/parse_log`
5. Repetir a cada 60 segundos

---

## Formatos de Log Suportados

O parser reconhece estes formatos:

### Formato 1 (Detalhado)

```text
PlayerKill: Killer=John, Victim=Mike, Pos=<4500, 0, 10000>, Weapon=M4A1, Distance=120m
```

### Formato 2 (Simplificado)

```text
Kill: John killed Mike at [4500, 0, 10000] with AKM
```

**Se seus logs tiverem outro formato**, cole 3 linhas reais aqui e eu ajusto o regex.

---

## Performance e Escalabilidade

### Grid Clustering

O sistema **não envia milhares de pontos** para o navegador.

Exemplo:

- **Sem clustering:** 10.000 mortes = 10.000 pontos no mapa (LENTO)
- **Com clustering (grid=50):** 10.000 mortes = ~200 pontos agregados (RÁPIDO)

### Filtros de Tempo

- `24h` - Últimas 24 horas
- `7d` - Últimos 7 dias
- `all` - Todos os dados

---

## Próximos Passos (Opcionais)

### 1. Migrar para PostgreSQL (Produção)

SQLite é ótimo para testes, mas para produção:

```bash
pip install psycopg2
```

Edite `database.py` para usar PostgreSQL.

### 2. Deploy no Render

O heatmap já está integrado ao dashboard. Basta fazer deploy normalmente.

### 3. Adicionar Alertas Discord

Quando uma zona ultrapassar X mortes em Y minutos, enviar webhook:

```python
if intensity > 20:
    send_discord_alert("🔥 Zona Quente em NWAF!")
```

---

## Troubleshooting

### Problema: "Nenhum ponto no mapa"

**Solução:** Verifique se o banco tem dados:

```bash
python database.py
```

### Problema: "Coordenadas erradas"

**Solução:** Ajuste os limites do mapa em `heatmap.js`:

```javascript
const MAP_CONFIG = {
    minX: 0,
    maxX: 15360,  // Ajustar conforme seu mapa
    minZ: 0,
    maxZ: 15360
};
```

### Problema: "Parser não encontra eventos"

**Solução:** Cole uma linha real do seu log RPT e eu ajusto o regex.

---

## Créditos

Arquitetura baseada nas recomendações do ChatGPT para sistemas de heatmap profissionais.
Implementado por Antigravity AI.
