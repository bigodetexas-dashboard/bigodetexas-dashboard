@echo off
echo ========================================
echo   TEXAS BIGODE BOT - INICIANDO
echo ========================================
echo.

REM Verificar se .env existe
if not exist .env (
    echo [ERRO] Arquivo .env nao encontrado!
    echo.
    echo Por favor, copie .env.example para .env e configure suas credenciais.
    echo Comando: copy .env.example .env
    echo.
    pause
    exit /b 1
)

echo [OK] Arquivo .env encontrado
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Instale Python 3.11+ de https://python.org
    echo.
    pause
    exit /b 1
)

echo [OK] Python instalado
echo.

REM Instalar dependências
echo [INFO] Instalando dependencias...
pip install -q discord.py aiohttp python-dotenv flask

if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo [OK] Dependencias instaladas
echo.

REM Iniciar bot
echo ========================================
echo   BOT INICIANDO...
echo ========================================
echo.
echo Pressione Ctrl+C para parar o bot
echo.

python bot_main.py

REM Se o bot parar
echo.
echo ========================================
echo   BOT ENCERRADO
echo ========================================
pause
