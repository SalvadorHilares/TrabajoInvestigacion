# 🚀 Instrucciones de Despliegue en Ubuntu AWS

## 📋 Instalación de Dependencias

Ejecuta estos comandos en tu instancia Ubuntu de AWS:

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y pip
sudo apt install python3 python3-pip python3-venv -y

# Instalar Docker
sudo apt install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Instalar AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip -y
unzip awscliv2.zip
sudo ./aws/install

# Instalar Pulumi
curl -fsSL https://get.pulumi.com | sh
source ~/.bashrc

# Limpiar archivos temporales
rm -rf awscliv2.zip aws/

# Reiniciar sesión para aplicar cambios de grupo Docker
exit
# (volver a conectarse por SSH)
```

## 🔧 Configuración Inicial

```bash
# Navegar al directorio del proyecto
cd /ruta/a/tu/proyecto/pulumi

# Configurar credenciales AWS
aws configure
# Ingresa:
# - Access Key ID: tu_access_key
# - Secret Access Key: tu_secret_key  
# - Default region: us-east-1
# - Default output format: json

# Ejecutar configuración de Pulumi
chmod +x setup.sh
./setup.sh
```

## 🐳 Despliegue

### Opción 1: Automático (Recomendado)

```bash
./deploy.sh
```

### Opción 2: Manual

```bash
# 1. Configurar variables de Pulumi
pulumi config set aws:region us-east-1
pulumi config set account_id 938209751559
pulumi config set iam_role_arn arn:aws:iam::938209751559:role/LabRole
pulumi config set repo_name fastapi-ecs
pulumi config set image_tag latest
pulumi config set app_port 8080

# 2. Login a ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 938209751559.dkr.ecr.us-east-1.amazonaws.com

# 3. Construir imagen usando tu Dockerfile
docker build -t fastapi-students:latest ..

# 4. Taggear para ECR
docker tag fastapi-students:latest 938209751559.dkr.ecr.us-east-1.amazonaws.com/fastapi-ecs:latest

# 5. Subir imagen
docker push 938209751559.dkr.ecr.us-east-1.amazonaws.com/fastapi-ecs:latest

# 6. Desplegar infraestructura
pulumi up
```

## 🧪 Pruebas

```bash
# Obtener URL de la aplicación
ALB_URL=$(pulumi stack output alb_url)
echo "URL de la aplicación: $ALB_URL"

# Probar endpoints
curl $ALB_URL/
curl $ALB_URL/health
curl $ALB_URL/test

# Crear un estudiante
curl -X POST $ALB_URL/students/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Juan Pérez", "age": 25}'

# Listar estudiantes
curl $ALB_URL/students/
```

## 📊 Monitoreo

```bash
# Ver logs en tiempo real
aws logs tail /ecs/fastapi --follow

# Ver estado del servicio ECS
aws ecs describe-services --cluster fastapi-cluster --services fastapi-service
```

## 🗑️ Limpieza

```bash
# Destruir toda la infraestructura
./destroy.sh

# O manualmente
pulumi destroy
```

## 🔍 Troubleshooting

### Error de permisos Docker
```bash
# Verificar que estás en el grupo docker
groups $USER

# Si no aparece docker, ejecutar:
sudo usermod -aG docker $USER
# Y reiniciar sesión
```

### Error de ECR
```bash
# Verificar que el repositorio existe
aws ecr describe-repositories --repository-names fastapi-ecs

# Si no existe, crearlo manualmente
aws ecr create-repository --repository-name fastapi-ecs --region us-east-1
```

### Error de Pulumi
```bash
# Verificar configuración
pulumi config

# Ver logs detallados
pulumi up --logtostderr -v=9
```

## 📝 Comandos Útiles

```bash
# Ver stacks de Pulumi
pulumi stack ls

# Ver outputs
pulumi stack output

# Ver configuración
pulumi config

# Preview de cambios
pulumi preview

# Ver logs de ECS
aws logs describe-log-streams --log-group-name /ecs/fastapi
```
