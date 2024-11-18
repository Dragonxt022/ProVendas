@echo off

REM Ativa o ambiente virtual
call venv\Scripts\activate

REM Exibe o horário atual do servidor
echo Hora do Servidor: %TIME%

REM Inicia o servidor Django acessível na rede local
cd provendas
python manage.py runserver 0.0.0.0:8000
pause
