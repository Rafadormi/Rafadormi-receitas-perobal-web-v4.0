@echo off
title ReceitasPerobal v4.0 - Iniciando Sistema
echo.
echo ===============================================
echo    ReceitasPerobal v4.0
echo    Sistema de Receitas Medicas - SMS Perobal
echo ===============================================
echo.
echo Sistema iniciando...
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.8+ antes de continuar.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Navegar para o diretório do projeto
cd /d "%~dp0"

REM Verificar se o ambiente virtual existe
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)

REM Ativar ambiente virtual
call venv\Scripts\activate.bat

REM Instalar dependências se necessário
echo Verificando dependencias...
pip install -q flask flask-sqlalchemy flask-cors reportlab pandas

REM Iniciar o servidor Flask em segundo plano
echo Iniciando servidor...
start /B python src\main.py

REM Aguardar o servidor inicializar
timeout /t 3 /nobreak >nul

REM Abrir o navegador automaticamente
echo Abrindo navegador...
start http://localhost:5001

echo.
echo ===============================================
echo Sistema iniciado com sucesso!
echo Acesse: http://localhost:5001
echo.
echo Para fechar o sistema, use o botao X no canto
echo superior direito da interface web.
echo ===============================================
echo.
echo Pressione qualquer tecla para minimizar esta janela...
pause >nul

REM Minimizar a janela do prompt
powershell -command "(New-Object -ComObject Shell.Application).MinimizeAll()"

