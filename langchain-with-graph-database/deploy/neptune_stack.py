from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_neptune as neptune,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct


class NeptuneStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "NeptuneVPC", max_azs=2, nat_gateways=0)

        subnet_group = neptune.CfnDBSubnetGroup(
            self,
            "NeptuneSubnetGroup",
            db_subnet_group_description="Neptune subnet group",
            subnet_ids=[subnet.subnet_id for subnet in vpc.public_subnets]
        )

        sg = ec2.SecurityGroup(self, "NeptuneSG", vpc=vpc)
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(8182))

        bucket = s3.Bucket(
            self, 
            "NeptuneBulkLoadBucket",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY
        )

        neptune_role = iam.Role(
            self,
            "NeptuneS3Role",
            assumed_by=iam.ServicePrincipal("rds.amazonaws.com")
        )
        bucket.grant_read(neptune_role)

        cluster = neptune.CfnDBCluster(
            self,
            "NeptuneCluster",
            db_cluster_identifier="db-neptune-1",
            engine_version="1.4.6.2",
            serverless_scaling_configuration=neptune.CfnDBCluster.ServerlessScalingConfigurationProperty(
                min_capacity=1,
                max_capacity=10
            ),
            db_subnet_group_name=subnet_group.ref,
            vpc_security_group_ids=[sg.security_group_id],
            iam_auth_enabled=True,
            storage_encrypted=False,
            availability_zones=[vpc.availability_zones[0]],
            deletion_protection=False,
            associated_roles=[neptune.CfnDBCluster.DBClusterRoleProperty(
                role_arn=neptune_role.role_arn
            )]
        )

        neptune.CfnDBInstance(
            self,
            "NeptuneInstance",
            db_instance_identifier="db-neptune-1-instance-1",
            db_instance_class="db.serverless",
            db_cluster_identifier=cluster.ref
        )
