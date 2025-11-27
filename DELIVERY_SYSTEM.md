# Sistema de Processamento de Entregas - BigodeTexas

Este módulo processa entregas pendentes e spawna itens no servidor DayZ automaticamente.

## Funcionamento

1. **Compra**: Usuário finaliza compra no site e escolhe coordenadas
2. **Fila**: Pedido é adicionado à fila de entregas com timestamp de entrega (5 minutos)
3. **Processamento**: Task loop verifica a cada minuto se há entregas prontas
4. **Spawn**: Itens são spawnados no servidor via modificação do `events.xml`
5. **Notificação**: Usuário recebe notificação Discord quando itens são entregues

## Arquivo de Fila

`delivery_queue.json`:

```json
{
  "delivery_123456": {
    "user_id": "discord_id",
    "items": [
      {"code": "ak74", "name": "KA-74", "quantity": 1},
      {"code": "556", "name": "Cx. 5.56x45mm", "quantity": 5}
    ],
    "coordinates": {"x": 7500, "z": 5500},
    "total_paid": 2000,
    "status": "pending",
    "created_at": "2025-11-27T10:00:00",
    "delivery_at": "2025-11-27T10:05:00"
  }
}
```

## Status de Entrega

- `pending`: Aguardando tempo de entrega
- `processing`: Sendo processada
- `completed`: Itens spawnados com sucesso
- `failed`: Erro no spawn

## Mapeamento de Itens

O sistema mapeia os códigos de itens da loja para os nomes de classe do DayZ:

```python
ITEM_CLASS_MAP = {
    "ak74": "AK74",
    "akm": "AKM",
    "m4a1": "M4A1",
    # ... etc
}
```
