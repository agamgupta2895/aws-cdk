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
        source_action = cpa.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="agamgupta2895",
            repo="aws-cdk",
            oauth_token=cdk.SecretValue.secrets_manager("github-token-dev",json_field='github-token-dev'),
            output=source_output,
            branch=stage
        )
        # code = cc.Repository.from_repository_name(self, "ImportedRepo-dev",'aws-cdk')
        # source_action = cpa.CodeCommitSourceAction(action_name="CodeCommit_Source",
        #                     repository=code,
        #                     output=source_output,
        #                     branch = stage
        # )
        
        print(stage)
        config = self.readConfig(stage)
        modules = config["modules"]
        regions = config["regions"]
        #iterating through the modules
        
        region_stack_rojects = {}
        for region in regions:
            stack_projects = []
            for project in modules:
                build_project = cbp.build_pipeline_project(self,f"{project['name']}-{stage}",f"{project['name']}",stage)
                build_project.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess'))
                build_output = cp.Artifact(f"{project['name']}-output")
                stack_project = cbp.build_code_pipeline_action_project(action_name = f"{project['name']}-{stage}",
                                                                        project = build_project,
                                                                        input = source_output,
                                                                        output = build_output,
                                                                        source_action = source_action,
                                                                        run_order= project['runOrder'],
                                                                        region=region,
                )
                stack_projects.append(stack_project)
            region_stack_rojects[region] = stack_projects
        
        stages = [cp.StageProps(stage_name="Source",actions=[source_action])]
        for region,stacks in region_stack_rojects.items():
            stages.append(cp.StageProps(stage_name=f"deploying-to-{stage}-{region}",actions=stacks))
            
            
        cp.Pipeline(self, "Pipeline",
            stages=stage, pipeline_name= f'deploying-to-{stage}'
        )
        

    def readConfig(self,stage):
        with open(f"config/{stage}.yml", 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)