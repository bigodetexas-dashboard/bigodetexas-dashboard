# -*- coding: utf-8 -*-
# Script para adicionar dinheiro infinito para testes
import database

# Seu Discord ID
USER_ID = "847456652253069382"

# Buscar dados atuais ou criar novo
current_data = database.get_economy(USER_ID) or {}

# Atualizar saldo para 999,999,999 DZCoins
current_data['balance'] = 999999999
database.save_economy(USER_ID, current_data)

# Também adicionar para o usuário de teste do dashboard
TEST_USER_ID = "test_user_123"
test_data = database.get_economy(TEST_USER_ID) or {}
test_data['balance'] = 999999999
test_data['gamertag'] = "Jogador de Teste"
database.save_economy(TEST_USER_ID, test_data)

print(f"Adicionado 999,999,999 DZCoins para {USER_ID} e {TEST_USER_ID}")
print("Novo saldo:", database.get_economy(TEST_USER_ID).get('balance', 0), "DZCoins")
