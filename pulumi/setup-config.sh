#!/bin/bash
# Script para configurar todas las variables de Pulumi para el stack 'dev'

set -e

echo "🔧 Configurando el stack 'dev' de Pulumi..."

# --- Configuración del Proveedor AWS ---
# Esta es la configuración específica del proveedor, como la región.
echo "📋 Estableciendo configuración del proveedor AWS..."
pulumi config set aws:region us-east-1

# --- Configuración del Proyecto ---
# Estas son las variables que tu programa __main__.py necesita.
echo "📋 Estableciendo configuración del proyecto..."
pulumi config set account_id "938209751559"
pulumi config set iam_role_arn "arn:aws:iam::938209751559:role/LabRole"
pulumi config set repo_name "fastapi-ecs"
pulumi config set image_tag "latest"
pulumi config set app_port "8080"

echo "✅ Configuración completada."
echo "🔎 Puedes verificar los valores con el comando: pulumi config"
echo "🚀 Ahora puedes ejecutar 'pulumi up' para desplegar tu infraestructura."
