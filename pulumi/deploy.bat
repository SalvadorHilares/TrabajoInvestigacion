@echo off
REM Script de despliegue completo para FastAPI con Pulumi (Windows)
REM Uso: deploy.bat

echo 🚀 Iniciando despliegue de FastAPI con Pulumi...

REM Variables (ajusta según tu configuración)
set REGION=us-east-1
set ACCOUNT_ID=938209751559
set IAM_ROLE_ARN=arn:aws:iam::938209751559:role/LabRole
set REPO_NAME=fastapi-ecs
set IMAGE_TAG=latest
set APP_PORT=8080

echo 📋 Configurando variables de Pulumi...
pulumi config set aws:region %REGION%
pulumi config set account_id %ACCOUNT_ID%
pulumi config set iam_role_arn %IAM_ROLE_ARN%
pulumi config set repo_name %REPO_NAME%
pulumi config set image_tag %IMAGE_TAG%
pulumi config set app_port %APP_PORT%

echo 🐳 Construyendo y subiendo imagen Docker...
REM Login a ECR
aws ecr get-login-password --region %REGION% | docker login --username AWS --password-stdin %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com

REM Construir imagen
docker build -t fastapi-students:latest ../app/

REM Tag para ECR
docker tag fastapi-students:latest %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%REPO_NAME%:%IMAGE_TAG%

REM Subir imagen
docker push %ACCOUNT_ID%.dkr.ecr.%REGION%.amazonaws.com/%REPO_NAME%:%IMAGE_TAG%

echo 🏗️ Desplegando infraestructura con Pulumi...
pulumi up --yes

echo ✅ Despliegue completado!
echo 🌐 URL de la aplicación:
pulumi stack output alb_url

echo 📊 Para ver logs:
echo aws logs tail /ecs/fastapi --follow

pause
