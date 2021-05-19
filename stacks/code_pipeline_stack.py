from aws_cdk import core as cdk

# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_codebuild as cb,
    aws_codepipeline as cp,
    aws_codecommit as cc,
    aws_codepipeline_actions as cpa,
    aws_iam as iam

)
from aws_cdk.pipelines import CdkPipeline,SimpleSynthAction

from stages import Stages

from utils.code_build_project import CodeBuildProject as cbp
import yaml
import os

class PipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        project_name = self.node.try_get_context("project_name")
        try:
            stage = os.environ['STAGE']
        except KeyError as err:
            print("Environment variable STAGE is not set") 

        source_output = cp.Artifact()
        cloud_assembly_artifact = cp.Artifact()

        source_action = cpa.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="agamgupta2895",
            repo="aws-cdk",
            oauth_token=cdk.SecretValue.secrets_manager("github-token-dev",json_field='github-token-dev'),
            output=source_output,
            branch="dev"
        )
        synth_action=SimpleSynthAction(
                source_artifact=source_output,
                cloud_assembly_artifact=cloud_assembly_artifact,
                install_commands=["npm install -g aws-cdk", "pip install -r requirements.txt"],
                synth_command="npx cdk synth"
        )
        
        pipeline = CdkPipeline(self, "pipeline-devvv",source_action=source_action,cross_account_keys=False,synth_action=synth_action,cloud_assembly_artifact=cloud_assembly_artifact)
        
        pipeline.add_application_stage(
            Stages(self,
                'deploying-stage-us-2',
                env = cdk.Environment(account="298397199672",region = "us-east-2")
            )
        )
        pipeline.add_application_stage(
            Stages(self,
                'deploying-stage-us-1',
                env = cdk.Environment(account="298397199672",region = "us-east-1")
            )
        )