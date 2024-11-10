@echo off

REM Ativa o ambiente virtual
call venv\Scripts\activate

REM Inicia o servidor Django acessível na rede local
cd provendas
python manage.py runserver 0.0.0.0:8000
pause
