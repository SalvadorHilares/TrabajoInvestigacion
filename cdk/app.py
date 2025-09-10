#!/usr/bin/env python3
import aws_cdk as cdk
from infra_cdk.infra_cdk_stack import InfraCdkStack

app = cdk.App()

InfraCdkStack(
    app, "InfraCdkStack",
    env=cdk.Environment(
        account="064912661622",
        region="us-east-1",
    ),
)

app.synth()
