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


class PipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        project_name = self.node.try_get_context("project_name")
        env = self.node.try_get_context("env")
        code = cc.Repository.from_repository_name(self, "ImportedRepo",'aws-cdk')
        vpc_build = cb.PipelineProject(self, "vpc-build",
                            build_spec=cb.BuildSpec.from_object(
                                dict(
                                    version="0.2",
                                    phases=dict(
                                        install=dict(
                                            commands=[
                                                "npm install aws-cdk",
                                                "npm update",
                                                "python -m pip install -r ../requirements.txt"
                                            ]),
                                        build=dict(commands=[
                                            "cd ..",
                                            "npx cdk deploy vpc"
                                        ])
                                    ),
                                    artifacts={
                                        "files": ["**/*"]
                                    },
                                    environment=dict(buildImage=cb.LinuxBuildImage.STANDARD_2_0))
                            )
        )
        source_output = cp.Artifact()
        vpc_build_output = cp.Artifact("vpc-build-output")
        cp.Pipeline(self, "Pipeline",
            stages=[
                cp.StageProps(stage_name="Source",
                    actions=[
                        cpa.CodeCommitSourceAction(
                            action_name="CodeCommit_Source",
                            repository=code,
                            output=source_output)]),
                cp.StageProps(stage_name="Build",
                    actions=[
                        cpa.CodeBuildAction(
                            action_name="Vpc-Build",
                            project=vpc_build,
                            input=source_output,
                            outputs=[vpc_build_output])])
                ]
            )

        
