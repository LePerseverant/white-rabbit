from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_fn,
    aws_iam as iam,
    aws_rekognition as rekognition,
    aws_lambda_event_sources as lambda_event_sources
)
from constructs import Construct
import os

class AwsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ########################################################################################
        #                                       S3BUCKET                                       #
        ########################################################################################
        bucket = s3.Bucket(
            self, 
            "the-white-rabbit-s3", 
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY
        ) 

        ########################################################################################
        #                                       DYNAMODB                                       #
        ########################################################################################
        table = dynamodb.TableV2(
            self,
            "the-white-rabbit-table",
            partition_key=dynamodb.Attribute(name="images", type=dynamodb.AttributeType.STRING),
            removal_policy=RemovalPolicy.DESTROY
        )

        ########################################################################################
        #                                       IAM ROLE                                       #
        ########################################################################################
        role = iam.Role(self, "the-white-rabbit-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )
        role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "s3:Get*",
                "s3:List*",
                "s3:Describe*",
                "s3-object-lambda:Get*",
                "s3-object-lambda:List*"
            ],
            resources=[bucket.bucket_arn + "/*"]
        ))

        ########################################################################################
        #                                       LAMBDA                                         #
        ########################################################################################
        fn = lambda_fn.Function(
            self,
            "the-white-rabbit-lambda", 
            runtime=lambda_fn.Runtime.PROVIDED_AL2023,
            handler="handler.lambda_handler",
            code=lambda_fn.Code.from_asset(os.path.join(os.getcwd(), "lambda")),
            role=role,
            environment= {
                "DYNAMODB_TABLE": table.table_name,
                "S3_BUCKET": bucket.bucket_name
            }
        )
        fn.add_event_source(lambda_event_sources.S3EventSource(
            bucket=bucket,
            events=[s3.EventType.OBJECT_CREATED]
        ))
        bucket.grant_write(fn)
        table.grant_full_access(fn)
