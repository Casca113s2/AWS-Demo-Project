from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    aws_ssm as ssm,
    Duration,
)
from constructs import Construct


class AutoScalingGroupInfra(Construct):

    def __init__(
        self, scope: Construct, construct_id: str, *, asg_config: dict, vpc: ec2.Vpc
    ) -> None:
        super().__init__(scope, construct_id)

        # Define the IAM role for the EC2 instances to allow Session Manager access
        role = iam.Role(
            self,
            asg_config["role_id"],
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonSSMManagedInstanceCore"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3FullAccess"),
            ],
        )

        # Define the Auto Scaling Group
        self.asg = autoscaling.AutoScalingGroup(
            self,
            asg_config["asg_id"],
            vpc=vpc,
            instance_type=ec2.InstanceType(asg_config["instance_type"]),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            desired_capacity=asg_config["desired_capacity"],
            min_capacity=asg_config["min_capacity"],
            max_capacity=asg_config["max_capacity"],
            role=role,
            update_policy=autoscaling.UpdatePolicy.replacing_update(),
            health_check=autoscaling.HealthCheck.elb(grace=Duration.seconds(150)),
            block_devices=[autoscaling.BlockDevice(device_name="/dev/xvda", volume=autoscaling.BlockDeviceVolume.ebs(encrypted=True, volume_size=8))],
        )

        # Scaling policies
        self.asg.scale_on_cpu_utilization("CpuScaling", target_utilization_percent=50)

        ssm_parameter = ssm.StringParameter.value_for_string_parameter(
            self,
            asg_config["ssm_parameter"]
        )
        # Add user data
        self.asg.add_user_data(
            f"""
#!/bin/bash

sudo yum install tomcat10.noarch -y

aws s3 cp s3://demo-appplication-artifact-bucket/artifacts/{ssm_parameter} /home/ec2-user/

mv /home/ec2-user/{ssm_parameter} /var/lib/tomcat10/webapps/helloworld.war

sudo systemctl start tomcat10
            """
        )
