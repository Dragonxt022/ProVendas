@echo off
REM Criação do ambiente virtual
python -m venv venv

REM Ativar o ambiente virtual
call venv\Scripts\activate

REM Instalar bibliotecas a partir do arquivo requirements.txt
pip install -r requirements.txt

REM Rodar as migrações do banco de dados
python manage.py migrate

REM Criar um superusuário padrão
REM Utilize o comando de migração com opções de configuração para o usuário
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', '12345678') | python manage.py shell

REM Finalizar
echo Ambiente configurado com sucesso!
pause
