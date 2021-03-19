from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_iam as iam
)


class SecurityStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        project_name = self.node.try_get_context("project_name")
        env = self.node.try_get_context("env")
        self.lambda_sg = ec2.SecurityGroup(self, f'lambda-sg-{env}',vpc=vpc,description='Security group for lambda function', allow_all_outbound=True)
        self.bastion_sg = ec2.SecurityGroup(self, f'bastion-sg-{env}', vpc= vpc, description= 'Security group for bastion', allow_all_outbound=True)
        self.bastion_sg.add_ingress_rule(ec2.Peer.any_ipv4(),ec2.Port.tcp(22), "SSH access")
        lambda_role = iam.Role(self, f'lambda-role-{env}', assumed_by=iam.ServicePrincipal(service='lambda.amazonaws.com'), role_name=f'lambda-role-{env}',
                                managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name='service-role/AWSLambdaBasicExecutionRole')]
        )
        lambda_role.add_to_policy(statement=iam.PolicyStatement(actions=['s3:*','rds:*'], resources=["*"]))

        ssm.StringParameter(self, f'lambda-param-{env}', parameter_name=f"/{env}/lambda-sg",string_value=self.lambda_sg.security_group_id)
        ssm.StringParameter(self,f'lambda-role-arn-{env}',parameter_name=f"/{env}/lambda-role-arn",string_value=lambda_role.role_arn)
        ssm.StringParameter(self,f'lambda-role-param-name-{env}',parameter_name=f"/{env}/lambda-role-name",string_value=lambda_role.role_name)
