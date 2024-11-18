import aws_cdk.aws_ec2 as ec2
from aws_cdk import aws_logs as logs
from aws_cdk import aws_iam as iam
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

        # Create a CloudWatch log group for the Flow Logs
        log_group = logs.LogGroup(
            self,
            network_infra_config["vpc"]["log_group_id"],
            retention=logs.RetentionDays.ONE_WEEK,
        )

        # Create an IAM Role for the Flow Logs
        log_role = iam.Role(
            self,
            network_infra_config["vpc"]["log_role_id"],
            assumed_by=iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
        )

        # Add the Flow Log to the VPC
        self.vpc.add_flow_log(
            network_infra_config["vpc"]["flow_log_id"],
            destination=ec2.FlowLogDestination.to_cloud_watch_logs(log_group, log_role)
        )

        # Output the VpcId
        vpc_id = network_infra_config["vpc"]["vpc_id"]
        CfnOutput(self, f"{vpc_id}Id", value=self.vpc.vpc_id, export_name=f"{vpc_id}Id")