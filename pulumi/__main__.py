"""
FastAPI Students API Infrastructure on AWS ECS Fargate
Deployed using Pulumi
"""
import json
import pulumi
import pulumi_aws as aws

# Configuración del proveedor AWS (idiomático, sin prefijo)
aws_config = pulumi.Config("aws")
region = aws_config.require("region")

# Configuración de tu proyecto
config = pulumi.Config()
account_id = config.require("account_id")
iam_role_arn = config.require("iam_role_arn")
repo_name = config.require("repo_name")
image_tag = config.get("image_tag") or "latest"
app_port = int(config.get("app_port") or 8080)

# Tags comunes
common_tags = {
    "Name": "FastAPI ECS",
    "Environment": "dev",
    "Project": "fastapi-ecs",
    "ManagedBy": "Pulumi"
}

# --- Data Sources (VPC y Subnets por defecto) ---
default_vpc = aws.ec2.get_vpc(default=True)
default_subnets = aws.ec2.get_subnets(filters=[{
    "name": "vpc-id",
    "values": [default_vpc.id],
}])

# --- ECR Repository ---
ecr_repo = aws.ecr.Repository(
    "api-repo",
    name=repo_name,
    force_delete=True,
    tags=common_tags
)

# ECR Lifecycle Policy
ecr_lifecycle_policy = aws.ecr.LifecyclePolicy(
    "api-repo-policy",
    repository=ecr_repo.name,
    policy=json.dumps({
        "rules": [
            {
                "rulePriority": 1,
                "description": "Eliminar imágenes viejas",
                "selection": {
                    "tagStatus": "untagged",
                    "countType": "imageCountMoreThan",
                    "countNumber": 5
                },
                "action": {
                    "type": "expire"
                }
            }
        ]
    })
)

# --- Security Groups ---
# ALB Security Group
alb_sg = aws.ec2.SecurityGroup(
    "alb-sg",
    name="alb-fastapi-sg",
    description="Allow HTTP inbound traffic",
    vpc_id=default_vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            description="HTTP from anywhere",
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            ipv6_cidr_blocks=["::/0"]
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
            ipv6_cidr_blocks=["::/0"]
        )
    ],
    tags={**common_tags, "Name": "ALB Security Group"}
)

# ECS Security Group
ecs_sg = aws.ec2.SecurityGroup(
    "ecs-sg",
    name="ecs-fastapi-sg",
    description="Allow traffic from ALB to ECS task",
    vpc_id=default_vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            from_port=app_port,
            to_port=app_port,
            protocol="tcp",
            security_groups=[alb_sg.id],
            description="From ALB only"
        )
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
            ipv6_cidr_blocks=["::/0"]
        )
    ],
    tags={**common_tags, "Name": "ECS Security Group"}
)

# --- Application Load Balancer ---
alb = aws.lb.LoadBalancer(
    "fastapi-alb",
    name="fastapi-alb",
    load_balancer_type="application",
    security_groups=[alb_sg.id],
    subnets=default_subnets.ids,
    tags={**common_tags, "Name": "FastAPI ALB"}
)

# Target Group
target_group = aws.lb.TargetGroup(
    "fastapi-tg",
    name="fastapi-tg",
    port=app_port,
    protocol="HTTP",
    vpc_id=default_vpc.id,
    target_type="ip",
    health_check=aws.lb.TargetGroupHealthCheckArgs(
        path="/health",
        protocol="HTTP",
        matcher="200",
        interval=30,
        healthy_threshold=2,
        unhealthy_threshold=3
    )
)

# ALB Listener
listener = aws.lb.Listener(
    "http-listener",
    load_balancer_arn=alb.arn,
    port=80,
    protocol="HTTP",
    default_actions=[
        aws.lb.ListenerDefaultActionArgs(
            type="forward",
            target_group_arn=target_group.arn
        )
    ]
)

# --- ECS Cluster ---
ecs_cluster = aws.ecs.Cluster(
    "fastapi-cluster",
    name="fastapi-cluster",
    tags={**common_tags, "Name": "FastAPI ECS Cluster"}
)

# --- CloudWatch Log Group ---
log_group = aws.cloudwatch.LogGroup(
    "fastapi-logs",
    name="/ecs/fastapi",
    retention_in_days=7,
    tags={**common_tags, "Name": "FastAPI ECS Logs"}
)

# --- ECS Task Definition ---
task_definition = aws.ecs.TaskDefinition(
    "fastapi-task",
    family="fastapi-task",
    network_mode="awsvpc",
    requires_compatibilities=["FARGATE"],
    cpu="256",
    memory="512",
    task_role_arn=iam_role_arn,
    execution_role_arn=iam_role_arn,
    container_definitions=pulumi.Output.all(
        ecr_repo.repository_url, 
        log_group.name
    ).apply(lambda args: json.dumps([
        {
            "name": "api",
            "image": f"{args[0]}:{image_tag}",
            "essential": True,
            "portMappings": [
                {
                    "containerPort": app_port,
                    "protocol": "tcp"
                }
            ],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": args[1],
                    "awslogs-region": region,
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
    ]))
)

# --- ECS Service ---
ecs_service = aws.ecs.Service(
    "fastapi-service",
    name="fastapi-service",
    cluster=ecs_cluster.arn,
    task_definition=task_definition.arn,
    desired_count=1,
    launch_type="FARGATE",
    force_new_deployment=True,
    network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
        subnets=default_subnets.ids,
        security_groups=[ecs_sg.id],
        assign_public_ip=True
    ),
    load_balancers=[
        aws.ecs.ServiceLoadBalancerArgs(
            target_group_arn=target_group.arn,
            container_name="api",
            container_port=app_port
        )
    ],
    opts=pulumi.ResourceOptions(depends_on=[listener])
)

# --- Outputs ---
pulumi.export("ecr_repository_url", ecr_repo.repository_url)
pulumi.export("alb_dns_name", alb.dns_name)
pulumi.export("alb_url", pulumi.Output.concat("http://", alb.dns_name))
pulumi.export("ecs_cluster_name", ecs_cluster.name)
pulumi.export("ecs_service_name", ecs_service.name)
pulumi.export("log_group_name", log_group.name)
