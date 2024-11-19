@echo off
REM Verificar se o Python está instalado
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Python nao encontrado! Instalando o Python...
    REM Baixar e instalar o Python silenciosamente
    powershell -Command "Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe -OutFile python_installer.exe"
    
    REM Instalando Python silenciosamente
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1

    REM Remover o instalador
    del python_installer.exe
    
    REM Verificar novamente se o Python foi instalado corretamente
    where python >nul 2>nul
    IF %ERRORLEVEL% NEQ 0 (
        echo Erro ao instalar o Python. Finalizando o script...
        exit /b 1
    )
    echo Python instalado com sucesso!
) ELSE (
    echo Python ja esta instalado.
)

REM Verificar se o Git está instalado
where git >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo Git nao encontrado! Instalando o Git...
    REM Baixar e instalar o Git silenciosamente
    powershell -Command "Invoke-WebRequest -Uri https://git-scm.com/download/win -OutFile git_installer.exe"
    
    REM Instalando Git silenciosamente
    start /wait git_installer.exe /VERYSILENT

    REM Remover o instalador
    del git_installer.exe
    
    REM Verificar novamente se o Git foi instalado corretamente
    where git >nul 2>nul
    IF %ERRORLEVEL% NEQ 0 (
        echo Erro ao instalar o Git. Finalizando o script...
        exit /b 1
    )
    echo Git instalado com sucesso!
) ELSE (
    echo Git ja esta instalado.
)

REM Clonar o repositório do GitHub
echo Clonando o repositório do GitHub...
git clone https://github.com/Dragonxt022/ProVendas.git

REM Navegar até o diretório do projeto
cd ProVendas

REM Criar o ambiente virtual
python -m venv venv

REM Ativar o ambiente virtual
call venv\Scripts\activate

REM Instalar as bibliotecas a partir do arquivo requirements.txt
pip install -r requirements.txt

REM Navegar até o diretório do projeto
cd provendas

REM Rodar as migrações do banco de dados
python manage.py migrate

REM Criar um superusuário padrão
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', '12345678') | python manage.py shell

REM Criar dados fake para Empresa e Cliente
python manage.py shell << EOF

from app.models import Empresa, Cliente
from django.contrib.auth.models import User

# Criando uma empresa
empresa = Empresa.objects.create(
    nome_empresa="Provendas",
    telefone="0000000000",  # Telefone com vários zeros
    cnpj="00000000000000",  # CNPJ fictício
    cidade="Cidade Fictícia",
    cep="00000000",
    estado="RO",  # Rondônia
    endereco="Rua Fictícia, 123, Bairro Fictício",
    status="ativo"
)

# Criando um cliente padrão
cliente = Cliente.objects.create(
    nome="Cliente Padão",
    email="cliente@provendas.com",
    cpf="00000000000",  # CPF fictício
    telefone="0000000000",
    data_nascimento="1990-01-01",  # Data fictícia
    endereco="Rua Fictícia, 123",
    cidade="Cidade Fictícia",
    estado="RO",  # Rondônia
    cep="00000000",
    status="ativo"
)


EOF

REM Finalizar
echo Ambiente configurado com sucesso!
pause
