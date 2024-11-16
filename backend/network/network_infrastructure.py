import aws_cdk.aws_ec2 as ec2
from constructs import Construct
from aws_cdk import CfnOutput

class NetworkInfra(Construct):

    def __init__(self, scope: Construct, construct_id: str, *, network_infra_config: dict) -> None:
        super().__init__(scope, construct_id)

        # ------------------------------#
        # Define the VPC
        # ------------------------------#
        self.vpc = ec2.Vpc(
            self,
            network_infra_config["vpc"]["vpc_id"],
            ip_addresses=ec2.IpAddresses.cidr(network_infra_config["vpc"]["cidr"]),
            max_azs=network_infra_config["vpc"]["max_azs"],
            nat_gateways=network_infra_config["vpc"]["nat_gateways"],
            subnet_configuration=[
                # Public Subnets
                ec2.SubnetConfiguration(
                    name=network_infra_config["vpc"]["subnet_configuration"][0]["name"],
                    subnet_type=ec2.SubnetType[network_infra_config["vpc"]["subnet_configuration"][0]["subnet_type"]],
                    cidr_mask=network_infra_config["vpc"]["subnet_configuration"][0]["cidr_mask"]
                ),
                # Private Subnets
                ec2.SubnetConfiguration(
                    name=network_infra_config["vpc"]["subnet_configuration"][1]["name"],
                    subnet_type=ec2.SubnetType[network_infra_config["vpc"]["subnet_configuration"][1]["subnet_type"]],
                    cidr_mask=network_infra_config["vpc"]["subnet_configuration"][1]["cidr_mask"]
                ),
            ]
        )   

        # Output the VpcId
        vpc_id = network_infra_config["vpc"]["vpc_id"]
        CfnOutput(self, f"{vpc_id}Id", value=self.vpc.vpc_id, export_name=f"{vpc_id}Id")