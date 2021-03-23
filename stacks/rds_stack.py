from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_s3 as s3,
    aws_ssm as ssm,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_kms as kms,
    aws_secretsmanager as sm
)
import os
import json
class RDSStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, vpc: ec2.Vpc, lambdasg: ec2.SecurityGroup, bastionsg: ec2.SecurityGroup,kmskey, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        project_name = self.node.try_get_context("project_name")
        try:
            stage = os.environ['STAGE']
        except KeyError as err:
            print("Environment variable STAGE is not set") 
        json_template = {'user':'admin'}
        db_creds = sm.Secret(self,f'db-secret-{stage}',secret_name= f'{stage}-rds-secret',
                            generate_secret_string=sm.SecretStringGenerator(
                                include_space=False,
                                password_length=12,
                                generate_string_key=f'rds-password-{stage}',
                                exclude_punctuation=True,
                                secret_string_template=json.dumps(json_template)    
                            )
        )
        db_mysql = rds.DatabaseCluster(self, f'mysql{stage}', 
                                        default_database_name = f'rds{stage}',
                                        engine = rds.DatabaseClusterEngine.AURORA_MYSQL,
                                        instance_props = rds.InstanceProps(
                                            vpc = vpc,
                                            vpc_subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED),
                                            instance_type = ec2.InstanceType(instance_type_identifier="t3.small")
                                        ),
                                        instances = 1,
                                        removal_policy = cdk.RemovalPolicy.DESTROY
        )
        db_mysql.connections.allow_default_port_from(lambdasg, "Access from lambda function")
        db_mysql.connections.allow_default_port_from(bastionsg, "Access from bastion sg")

        ssm.StringParameter(self, f'db-host-{stage}', parameter_name=f"/{stage}/db-host-{stage}",string_value= db_mysql.cluster_endpoint.hostname)
