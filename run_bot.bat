@echo off
title BigodeTexas Bot 🤠
color 0A

echo ==========================================
echo      INICIANDO BIGODETEXAS - DIAGNOSTICO
echo ==========================================
echo.

:: Verificar se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale o Python em https://www.python.org/downloads/
    echo Marque a opcao "Add Python to PATH" na instalacao.
    echo.
    pause
    exit
)

echo [OK] Python encontrado.
echo.

:: Instalar dependencias
echo Verificando dependencias...
pip install discord.py requests >nul 2>&1
if %errorlevel% neq 0 (
    color 0E
    echo [AVISO] Nao foi possivel instalar dependencias automaticamente.
    echo Tentando rodar mesmo assim...
) else (
    echo [OK] Dependencias verificadas.
)

echo.
echo Iniciando bot_main.py...
echo ------------------------------------------
python bot_main.py
echo ------------------------------------------
echo.

color 0C
echo O BOT PAROU DE RODAR.
echo Verifique as mensagens de erro acima.
echo.
pause
