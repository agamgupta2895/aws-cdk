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
from utils.code_build_project import CodeBuildProject as cbp


class PipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        project_name = self.node.try_get_context("project_name")
        env = self.node.try_get_context("env")
        code = cc.Repository.from_repository_name(self, "ImportedRepo-dev",'aws-cdk')
        
        #s3_build_project = cbp.build_pipeline_project(self,'s3-stack-dev','s3-stack')

        
        s3_build = cb.PipelineProject(self, "s3-dev",
                            build_spec=cb.BuildSpec.from_object(
                                dict(
                                    version="0.2",
                                    phases=dict(
                                        install=dict(
                                            commands=[
                                                "printenv",
                                                "echo $STAGE",
                                                "npm install aws-cdk",
                                                "npm update",
                                                "pip install -r requirements.txt"
                                            ]),
                                        build=dict(commands=[
                                            "cdk deploy s3_stack"
                                        ])
                                    ),
                                    artifacts={
                                        "files": ["**/*"]
                                    },
                                    environment=dict(buildImage=cb.LinuxBuildImage.STANDARD_2_0))
                            )
        )
        
        
        s3_build_output = cp.Artifact("s3-build-output")
        source_output = cp.Artifact()
        source_action = cpa.CodeCommitSourceAction(action_name="CodeCommit_Source",
                            repository=code,
                            output=source_output
        )
        cp.Pipeline(self, "Pipeline",
            stages=[
                cp.StageProps(stage_name="Source",
                    actions=[source_action]),
                cp.StageProps(stage_name="Build",
                    actions=[
                        cpa.CodeBuildAction(
                            action_name="s3-Build",
                            project=s3_build,
                            input=source_output,
                            outputs=[s3_build_output],
                            environment_variables={"STAGE":{"value":source_action.variables.branch_name}}
                        )
                    
                    ]
                )
            ]
        )
        
        
        # code = cc.Repository.from_repository_name(self, "ImportedRepo-dev",'aws-cdk')
        # source_action = cpa.CodeCommitSourceAction(action_name="CodeCommit_Source",
        #                     repository=code,
        #                     output=source_output
        # )
        # b = cbp.build_code_pipeline_action_project('s3-build-dev',s3_build_project,source_output,s3_build_output,source_action)
        # cp.Pipeline(self, "Pipeline",
        #     stages=[
        #         cp.StageProps(stage_name="Source",
        #             actions=[source_action]),
        #         cp.StageProps(stage_name="Build",
        #             actions=[b]
        #         )
        #     ]
        # )