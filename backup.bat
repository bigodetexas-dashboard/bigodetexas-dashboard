@echo off
echo ========================================
echo   BigodeTexas - Backup Automatico
echo ========================================
echo.

set BACKUP_DIR=backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
set BACKUP_DIR=%BACKUP_DIR: =0%

echo Criando diretorio de backup: %BACKUP_DIR%
mkdir %BACKUP_DIR%

echo.
echo Copiando arquivos JSON...
xcopy /Y *.json %BACKUP_DIR%\

echo Copiando logs...
if exist logs mkdir %BACKUP_DIR%\logs
xcopy /E /Y logs %BACKUP_DIR%\logs\

echo Copiando configuracoes...
if exist .env copy .env %BACKUP_DIR%\.env

echo.
echo ========================================
echo   Backup concluido!
echo   Local: %BACKUP_DIR%
echo ========================================
echo.

:: Limpar backups antigos (manter ultimos 7 dias)
forfiles /p backups /s /m *.* /d -7 /c "cmd /c if @isdir==TRUE rd /s /q @path" 2>nul

pause
