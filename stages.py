from stacks.s3_stack import S3Stack
from aws_cdk import core as cdk
class Stages(cdk.Stage):
    def __init__(self, scope, id, *, env=None, outdir=None):
        super().__init__(scope, id, env=env, outdir=outdir)
        s3_stack = S3Stack(self,f's3-stack-dev')

