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

)



class CodeBuildProject():
    
    @staticmethod
    def build_pipeline_project(self, id, module_name):

        return cb.PipelineProject(self, id,
                            build_spec=cb.BuildSpec.from_object(
                                dict(
                                    version="0.2",
                                    phases=dict(
                                        install=dict(
                                            commands=[
                                                "echo $STAGE",
                                                "npm install aws-cdk",
                                                "npm update",
                                                "pip install -r requirements.txt"
                                            ]),
                                        build=dict(commands=[
                                            f"npx cdk deploy {module_name}"
                                        ])
                                    ),
                                    artifacts={
                                        "files": ["**/*"],
                                        "enable-symlinks": "yes"
                                    },
                                    environment=dict(buildImage=cb.LinuxBuildImage.STANDARD_2_0))
                            )
        )
    
    @staticmethod
    def build_code_pipeline_action_project(action_name,project,input,output,source_action):
        return cpa.CodeBuildAction(
                            action_name=action_name,
                            project=project,
                            input=input,
                            outputs=[output],
                            environment_variables={"STAGE":{"value":source_action.variables.branch_name}}
                        )