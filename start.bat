@echo off
title Iniciando o Servidor Django - Provendas

REM Verifica se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python não foi encontrado no sistema. Por favor, instale o Python e adicione-o ao PATH.
    pause
    exit /b
)

REM Exibe a versão do Python
for /f "tokens=2 delims= " %%a in ('python --version') do set PYTHON_VERSION=%%a
echo Versão do Python detectada: %PYTHON_VERSION%

REM Configura permissões para ativar ambientes virtuais no Windows
echo Configurando permissões para ambientes virtuais...
powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force" >nul 2>&1

REM Exibe uma mensagem de progresso
echo Ativando o ambiente virtual...
call venv\Scripts\activate

REM Navega até o diretório do projeto
cd provendas

REM Inicia o servidor Django acessível na rede local em uma nova janela minimizada
start /min cmd /c "python manage.py runserver 0.0.0.0:8000"

REM Mantém a janela aberta para exibir mensagens
