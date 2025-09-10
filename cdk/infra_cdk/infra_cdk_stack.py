from aws_cdk import (
    Stack, Duration, CfnOutput
)
from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_logs as logs,
)

class InfraCdkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1) VPC 
        vpc = ec2.Vpc.from_lookup(self, "DefaultVpc", is_default=True)

        # 2) ECS
        cluster = ecs.Cluster(
            self, "Cluster",
            vpc=vpc,
            cluster_name="api-trabajoinvestigacion-cluster"
        )

        # 3) ECR 
        repo = ecr.Repository.from_repository_name(
            self, "Repo",
            repository_name="api-trabajoinvestigacioncdk"
        )

        # 4) Roles
        lab_role = iam.Role.from_role_arn(
            self, "LabRole",
            "arn:aws:iam::064912661622:role/LabRole",
            mutable=False
        )

        # 5) Task Definition 
        task_def = ecs.FargateTaskDefinition(
            self, "TaskDef",
            cpu=256,
            memory_limit_mib=512,
            execution_role=lab_role,
            task_role=lab_role
        )

        # 6) Logs
        log_group = logs.LogGroup(
            self, "LogGroup",
            log_group_name="/ecs/api-trabajoinvestigacion",
            retention=logs.RetentionDays.ONE_WEEK
        )

        # 7) Contenedor
        container = task_def.add_container(
            "web",
            image=ecs.ContainerImage.from_ecr_repository(repo, tag="latest"),
            logging=ecs.LogDriver.aws_logs(stream_prefix="web", log_group=log_group),
            environment={
                "PORT": "8000",
                "DB_PATH": "/data/students.db"
            },
        )
        container.add_port_mappings(ecs.PortMapping(container_port=8000))

        # 8) Fargate con ALB público 
        service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "Service",
            cluster=cluster,
            task_definition=task_def,
            desired_count=1,
            public_load_balancer=True,
            listener_port=80,
            service_name="api-trabajoinvestigacion-service"
        )

        # Health check
        service.target_group.configure_health_check(
            path="/health",
            healthy_http_codes="200-399",
            interval=Duration.seconds(30),
            healthy_threshold_count=2,
            unhealthy_threshold_count=3
        )

        # 9) Outputs útiles
        CfnOutput(self, "AlbDNS", value=service.load_balancer.load_balancer_dns_name)
        CfnOutput(self, "EcrRepoUri", value=repo.repository_uri)
        CfnOutput(self, "ClusterName", value=cluster.cluster_name)
        CfnOutput(self, "ServiceName", value=service.service.service_name)
