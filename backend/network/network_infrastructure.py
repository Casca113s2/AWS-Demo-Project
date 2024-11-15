import aws_cdk.aws_ec2 as ec2
from constructs import Construct
from aws_cdk import CfnOutput

class Network(Construct):

    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)

        # ------------------------------#
        # Define the VPC
        # ------------------------------#
        self.vpc = ec2.Vpc(
            self,
            "DemoVPC",
            cidr="10.0.0.0/16",
            max_azs=1,
            nat_gateways=1,
            subnet_configuration=[
                # Public Subnets
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                # Private Subnets
                ec2.SubnetConfiguration(
                    name="PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=24
                ),
            ]
        )   

        # Output the VpcId
        CfnOutput(self, "DemoVpcId", value=self.vpc.vpc_id, export_name="DemoVpcId")