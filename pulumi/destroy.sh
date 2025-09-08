#!/bin/bash

# Script para destruir la infraestructura
# Uso: ./destroy.sh

set -e

echo "🗑️ Destruyendo infraestructura de FastAPI..."

# Confirmar antes de destruir
read -p "¿Estás seguro de que quieres destruir toda la infraestructura? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Operación cancelada"
    exit 1
fi

echo "🏗️ Destruyendo recursos con Pulumi..."
pulumi destroy --yes

echo "✅ Infraestructura destruida exitosamente!"
