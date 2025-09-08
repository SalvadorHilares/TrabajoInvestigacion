#!/bin/bash

# Comandos útiles para Docker y ECR
# Uso: source docker-commands.sh

# Variables
REGION="us-east-1"
ACCOUNT_ID="938209751559"
REPO_NAME="fastapi-ecs"
IMAGE_TAG="latest"

echo "🐳 Comandos Docker y ECR configurados:"
echo ""

# Función para login a ECR
ecr_login() {
    echo "🔐 Haciendo login a ECR..."
    aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
}

# Función para construir imagen
build_image() {
    echo "🔨 Construyendo imagen Docker desde la raíz del proyecto..."
    docker build -t fastapi-students:latest ..
}

# Función para taggear imagen
tag_image() {
    echo "🏷️ Taggeando imagen para ECR..."
    docker tag fastapi-students:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG
}

# Función para subir imagen
push_image() {
    echo "⬆️ Subiendo imagen a ECR..."
    docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO_NAME:$IMAGE_TAG
}

# Función para proceso completo
build_and_push() {
    ecr_login
    build_image
    tag_image
    push_image
    echo "✅ Imagen construida y subida exitosamente!"
}

# Función para ver logs
view_logs() {
    echo "📊 Viendo logs de ECS..."
    aws logs tail /ecs/fastapi --follow
}

echo "Comandos disponibles:"
echo "  ecr_login        - Login a ECR"
echo "  build_image      - Construir imagen Docker"
echo "  tag_image        - Taggear imagen para ECR"
echo "  push_image       - Subir imagen a ECR"
echo "  build_and_push   - Proceso completo (build + push)"
echo "  view_logs        - Ver logs de ECS"
echo ""
echo "Ejemplo de uso:"
echo "  build_and_push"
