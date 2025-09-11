from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_elasticloadbalancingv2 as elbv2,
    aws_logs as logs,
)
from constructs import Construct
from aws_cdk import LegacyStackSynthesizer


class InfraCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, synthesizer=LegacyStackSynthesizer(), **kwargs)

        # VPC
        vpc = ec2.Vpc.from_lookup(self, "DefaultVPC", is_default=True)

        # ECS
        cluster = ecs.Cluster(
            self, "ApiCluster",
            vpc=vpc,
            cluster_name="api-trabajoinvestigacion-cluster"
        )

        # ECR
        repository = ecr.Repository.from_repository_name(
            self, "ApiRepo", "api-trabajoinvestigacioncdk"
        )

        # Rol IAM 
        lab_role = iam.Role.from_role_arn(
            self, "LabRole",
            role_arn=f"arn:aws:iam::{self.account}:role/LabRole"
        )

        # Logs 
        log_group = logs.LogGroup(
            self, "ApiLogs",
            log_group_name="/ecs/api-trabajoinvestigacion",
            retention=logs.RetentionDays.ONE_WEEK
        )

        # Task
        task_def = ecs.FargateTaskDefinition(
            self, "ApiTaskDef",
            cpu=256,
            memory_limit_mib=512,
            execution_role=lab_role,
            task_role=lab_role
        )

        container = task_def.add_container(
            "web",
            image=ecs.ContainerImage.from_ecr_repository(repository, tag="latest"),
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="ecs",
                log_group=log_group
            ),
            environment={
                "PORT": "8000",
                "DB_PATH": "/data/students.db"
            }
        )
        container.add_port_mappings(
            ecs.PortMapping(container_port=8000, protocol=ecs.Protocol.TCP)
        )

        # Balancer
        lb = elbv2.ApplicationLoadBalancer(
            self, "ApiALB",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name="api-trabajoinvestigacion-alb"
        )

        listener = lb.add_listener("Listener", port=80, open=True)

        # Servicio ECS
        service = ecs.FargateService(
            self, "ApiService",
            cluster=cluster,
            task_definition=task_def,
            desired_count=1,
            assign_public_ip=True
        )

        # HealthCheck
        listener.add_targets(
            "ECS",
            port=80,
            targets=[service],
            health_check=elbv2.HealthCheck(
                path="/health",
                healthy_http_codes="200-399"
            )
        )

        # Outputs
        self.add_output("AlbDNS", lb.load_balancer_dns_name)
        self.add_output("RepoUri", repository.repository_uri)

    def add_output(self, name: str, value: str) -> None:
        from aws_cdk import CfnOutput
        CfnOutput(self, name, value=value)
