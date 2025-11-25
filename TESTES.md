# Guia de Testes - Novas Funcionalidades

## 🧪 Como Testar as Novas Funcionalidades

### Pré-requisitos

1. **Bot principal deve estar rodando**
   ```bash
   python bot_main.py
   ```

2. **Configure o canal de teste no `.env`**
   ```
   TEST_CHANNEL_ID=1384336968736837712
   ```
   *(Já configurado para o canal KILLFEED)*

### Opção 1: Teste Automatizado (Recomendado)

Execute o script de teste:
```bash
python test_new_features.py
```

**O que será testado:**
- ✅ Leaderboard (4 testes)
- ✅ Admin Spawner (1 teste)
- ✅ Editor Gameplay (4 testes)

**Resultado esperado:**
- Script envia comandos automaticamente
- Verifica respostas do bot
- Mostra resumo no console e Discord

### Opção 2: Teste Manual

Digite os comandos diretamente no Discord:

#### Leaderboard
```
!top                    # Menu principal
!top kills              # Top matadores
!top kd                 # Top K/D
!top coins              # Mais rico
!top playtime           # Mais tempo jogado
```

#### Admin Spawner
```
!spawn_list             # Ver fila (não requer admin)
```

#### Editor Gameplay
```
!gameplay               # Menu principal
!gameplay ajuda         # Ver comandos
!gameplay view          # Ver categorias
!gameplay view Buffs    # Ver parâmetros de Buffs
```

### Testes Avançados (Apenas Admin)

**Admin Spawner:**
```
!spawn M4A1 1 PlayerName
!spawn_coords AK74 1 7500 7500
!process_spawns
```

**Editor Gameplay:**
```
!gameplay edit HealthRegen 5.0
!gameplay backup
!gameplay upload
!gameplay restore
```

## 📊 Resultados Esperados

### Leaderboard
- **Dados vazios**: Mensagem "❌ Ainda não há dados..."
- **Com dados**: Embed com ranking e medalhas 🥇🥈🥉

### Admin Spawner
- **Fila vazia**: "✅ Nenhum spawn pendente"
- **Com spawns**: Lista de spawns pendentes

### Editor Gameplay
- **Menu**: Embed com comandos disponíveis
- **View**: Lista de categorias ou parâmetros
- **Edit**: Confirmação de modificação (requer senha)

## ⚠️ Problemas Comuns

**Bot não responde:**
- Verifique se bot_main.py está rodando
- Confirme que o bot está online no Discord
- Verifique permissões do bot no canal

**Erro de compilação:**
- Execute: `python -m py_compile bot_main.py`
- Verifique imports dos novos módulos

**Comandos não encontrados:**
- Reinicie o bot (CTRL+C e `python bot_main.py`)
- Verifique se os módulos foram importados corretamente

## ✅ Checklist de Testes

- [ ] Bot principal está rodando
- [ ] TEST_CHANNEL_ID configurado
- [ ] Teste automatizado executado
- [ ] Leaderboard testado manualmente
- [ ] Spawner testado (lista)
- [ ] Editor testado (view)
- [ ] Testes admin executados (opcional)
- [ ] Todos os comandos responderam

## 📝 Reportar Problemas

Se encontrar erros, anote:
1. Comando executado
2. Resposta recebida (ou falta dela)
3. Mensagem de erro no console do bot
4. Screenshot do Discord (se aplicável)
