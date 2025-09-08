#!/bin/bash

# Script de configuración inicial para Pulumi
# Uso: ./setup.sh

set -e

echo "🔧 Configurando proyecto Pulumi..."

# Verificar que Pulumi esté instalado
if ! command -v pulumi &> /dev/null; then
    echo "❌ Pulumi no está instalado. Instálalo desde: https://www.pulumi.com/docs/get-started/install/"
    exit 1
fi

# Verificar que AWS CLI esté instalado
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI no está instalado. Instálalo desde: https://aws.amazon.com/cli/"
    exit 1
fi

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Instálalo desde: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Todas las dependencias están instaladas"

# Crear entorno virtual de Python
echo "🐍 Creando entorno virtual de Python..."
python3 -m venv venv

# Activar entorno virtual
echo "🔌 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📦 Instalando dependencias de Pulumi..."
pip install -r requirements.txt

# Inicializar stack de Pulumi
echo "🏗️ Inicializando stack de Pulumi..."
pulumi stack init dev

# Hacer ejecutables los scripts
chmod +x deploy.sh
chmod +x destroy.sh
chmod +x docker-commands.sh

echo "✅ Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configura tus credenciales de AWS: aws configure"
echo "2. Ejecuta el despliegue: ./deploy.sh"
echo "3. Para ver logs: aws logs tail /ecs/fastapi --follow"
echo ""
echo "🔧 Comandos útiles:"
echo "  pulumi stack ls          - Ver stacks disponibles"
echo "  pulumi config            - Ver configuración actual"
echo "  pulumi preview           - Ver cambios antes de aplicar"
echo "  pulumi up                - Aplicar cambios"
echo "  pulumi destroy           - Destruir infraestructura"
