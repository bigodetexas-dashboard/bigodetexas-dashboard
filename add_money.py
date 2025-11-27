# -*- coding: utf-8 -*-
# Script para adicionar dinheiro infinito para testes
import database

# Seu Discord ID
USER_ID = "847456652253069382"

# Buscar dados atuais ou criar novo
current_data = database.get_economy(USER_ID) or {}

# Atualizar saldo para 999,999,999 DZCoins
current_data['balance'] = 999999999

# Salvar
database.save_economy(USER_ID, current_data)

print("Adicionado 999,999,999 DZCoins para o usuario", USER_ID)
print("Novo saldo:", database.get_economy(USER_ID).get('balance', 0), "DZCoins")
