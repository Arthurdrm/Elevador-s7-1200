@echo off
chcp 65001 > nul
echo =====================================================================
echo  Gerando Executavel Standalone: Simulador_Elevador_S7_1200.exe
echo  Compativel com Windows 10 e Windows 11 (64-bit)
echo =====================================================================

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Python nao encontrado no PATH do sistema.
    pause
    exit /b 1
)

echo [1/3] Instalando / Atualizando dependencias...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

echo [2/3] Compilando via PyInstaller...
pyinstaller simulador_elevador.spec --noconfirm --clean

if %ERRORLEVEL% equ 0 (
    echo.
    echo =====================================================================
    echo [SUCESSO] Executavel gerado em: dist\Simulador_Elevador_S7_1200.exe
    echo =====================================================================
) else (
    echo.
    echo [FALHA] Erro durante a compilacao do executavel.
)

pause
