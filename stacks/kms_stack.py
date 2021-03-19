from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_kms as kms,
    aws_ssm as ssm
)


class KmsStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        project_name = self.node.try_get_context("project_name")
        env = self.node.try_get_context("env")
        self.kms_rds = kms.Key(self,f'rds-key-{env}',description=f'{project_name} rds key {env}',enable_key_rotation=True)
        self.kms_rds.add_alias(alias_name=f'alias/{project_name}-key-rds-{env}')

        ssm.StringParameter(self,f'rds-key-param-{env}',string_value=self.kms_rds.key_id,parameter_name=f"/{env}/rds")