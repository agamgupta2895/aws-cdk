from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_kms as kms,
    aws_ssm as ssm
)
import os

class KmsStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        project_name = self.node.try_get_context("project_name")
        try:
            stage = os.environ['STAGE']
        except KeyError as err:
            print("Environment variable STAGE is not set") 
        self.kms_rds = kms.Key(self,f'rds-key-{stage}',description=f'{project_name} rds key {stage}',enable_key_rotation=True)
        self.kms_rds.add_alias(alias_name=f'alias/{project_name}-key-rds-{stage}')

        ssm.StringParameter(self,f'rds-key-param-{stage}',string_value=self.kms_rds.key_id,parameter_name=f"/{stage}/rds")