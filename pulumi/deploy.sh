#!/bin/bash

# Script de despliegue completo para FastAPI con Pulumi
# Uso: ./deploy.sh

set -e

echo "🚀 Iniciando despliegue de FastAPI con Pulumi..."

# Variables (ajusta según tu configuración)
REGION="us-east-1"
ACCOUNT_ID="938209751559"
IAM_ROLE_ARN="arn:aws:iam::938209751559:role/LabRole"
REPO_NAME="fastapi-ecs"
IMAGE_TAG="latest"
APP_PORT="8080"

echo "📋 Configurando variables de Pulumi..."
pulumi config set aws:region $REGION
pulumi config set account_id $ACCOUNT_ID
pulumi config set iam_role_arn $IAM_ROLE_ARN
pulumi config set repo_name $REPO_NAME
pulumi config set image_tag $IMAGE_TAG
pulumi config set app_port $APP_PORT

echo "🐳 Construyendo y subiendo imagen Docker..."
# Login a ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Construir imagen desde la raíz del proyecto (donde está el Dockerfile)
docker build -t fastapi-students:latest ..

# Tag para ECR
docker tag fastapi-students:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

# Subir imagen
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG

echo "🏗️ Desplegando infraestructura con Pulumi..."
pulumi up --yes

echo "✅ Despliegue completado!"
echo "🌐 URL de la aplicación:"
pulumi stack output alb_url

echo "📊 Para ver logs:"
echo "aws logs tail /ecs/fastapi --follow"
