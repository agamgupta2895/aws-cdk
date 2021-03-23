#!/usr/bin/env python3

from aws_cdk import core as cdk

# For consistency with TypeScript code, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import core

from stacks.vpc_stack import VPCStack
from stacks.security_stack import SecurityStack
from stacks.bastion_stack import BastionStack
from stacks.kms_stack import KmsStack
from stacks.s3_stack import S3Stack
from stacks.rds_stack import RDSStack
from stacks.code_pipeline_stack import PipelineStack
import yaml
import os

try:
    stage = os.environ['STAGE']
except KeyError as err:
    print("Environment variable STAGE is not set") 

app = core.App()



pipeline_stack = PipelineStack(app,f'pipeline-stack-{stage}')
vpc_stack = VPCStack(app, f"vpc-stack-{stage}")
security_stack = SecurityStack(app, f'security-stack-{stage}', vpc=vpc_stack.vpc)
bastion_stack = BastionStack(app,f'bastion-stack-{stage}',vpc = vpc_stack.vpc,sg = security_stack.bastion_sg)
kms_stack = KmsStack(app,f'kms-stack-{stage}')
s3_stack = S3Stack(app,f's3-stack-{stage}')
rds_stack = RDSStack(app, f'rds-stack-{stage}', vpc=vpc_stack.vpc, lambdasg=security_stack.lambda_sg, bastionsg=security_stack.bastion_sg, kmskey= kms_stack.kms_rds)




app.synth()
