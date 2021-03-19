from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_s3 as s3,
    aws_ssm as ssm
)


class S3Stack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        project_name = self.node.try_get_context("project_name")
        env = self.node.try_get_context("env")
        account_id = cdk.Aws.ACCOUNT_ID
        lambda_bucket = s3.Bucket(self,f'lambda-bucket-{env}',access_control=s3.BucketAccessControl.BUCKET_OWNER_FULL_CONTROL,
                                    encryption=s3.BucketEncryption.S3_MANAGED,
                                    bucket_name=f'{account_id}-{env}-lambda-deploy-package',
                                    block_public_access=s3.BlockPublicAccess(block_public_acls=True,block_public_policy=True,ignore_public_acls=True,restrict_public_buckets=True),
                                    removal_policy=cdk.RemovalPolicy.RETAIN
        )
        ssm.StringParameter(self,f'ssm-lambda-bucket-{env}',parameter_name=f'/{env}/lambda-s3-bucket',string_value=lambda_bucket.bucket_name)