@echo off
REM Obter o diretório onde o script está localizado
set SCRIPT_DIR=%~dp0

REM Entrar no diretório do projeto (considerando que a pasta "provendas" esteja no mesmo diretório do script)
cd /d %SCRIPT_DIR%provendas

REM Verificar se há atualizações no repositório remoto e puxar as atualizações
echo Verificando atualizações no repositório...
git fetch origin

REM Verificar se há atualizações no repositório remoto
git status | find "up to date"
if %errorlevel% neq 0 (
    echo Atualizações encontradas, realizando pull...
    git pull origin main
) else (
    echo O repositório está atualizado.
)

REM Ativar o ambiente virtual
call venv\Scripts\activate

REM Verificar se há novas migrações pendentes e rodar makemigrations e migrate
echo Verificando migrações...
python manage.py makemigrations
python manage.py migrate

REM Verificar se há novas dependências e instalar as bibliotecas do requirements.txt
echo Verificando e instalando as dependências...
pip install -r requirements.txt

echo Atualização concluída com sucesso!
pause
