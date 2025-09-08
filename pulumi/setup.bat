@echo off
REM Script de configuración inicial para Pulumi (Windows)
REM Uso: setup.bat

echo 🔧 Configurando proyecto Pulumi...

REM Verificar que Pulumi esté instalado
pulumi version >nul 2>&1
if errorlevel 1 (
    echo ❌ Pulumi no está instalado. Instálalo desde: https://www.pulumi.com/docs/get-started/install/
    pause
    exit /b 1
)

REM Verificar que AWS CLI esté instalado
aws --version >nul 2>&1
if errorlevel 1 (
    echo ❌ AWS CLI no está instalado. Instálalo desde: https://aws.amazon.com/cli/
    pause
    exit /b 1
)

REM Verificar que Docker esté instalado
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker no está instalado. Instálalo desde: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

echo ✅ Todas las dependencias están instaladas

REM Crear entorno virtual de Python
echo 🐍 Creando entorno virtual de Python...
python -m venv venv

REM Activar entorno virtual
echo 🔌 Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📦 Instalando dependencias de Pulumi...
pip install -r requirements.txt

REM Inicializar stack de Pulumi
echo 🏗️ Inicializando stack de Pulumi...
pulumi stack init dev

echo ✅ Configuración completada!
echo.
echo 📋 Próximos pasos:
echo 1. Configura tus credenciales de AWS: aws configure
echo 2. Ejecuta el despliegue: deploy.bat
echo 3. Para ver logs: aws logs tail /ecs/fastapi --follow
echo.
echo 🔧 Comandos útiles:
echo   pulumi stack ls          - Ver stacks disponibles
echo   pulumi config            - Ver configuración actual
echo   pulumi preview           - Ver cambios antes de aplicar
echo   pulumi up                - Aplicar cambios
echo   pulumi destroy           - Destruir infraestructura

pause
