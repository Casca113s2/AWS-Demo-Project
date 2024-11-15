from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
)
from constructs import Construct


class AutoScalingGroup(Construct):

    def __init__(self, scope: Construct, construct_id: str, *, vpc: ec2.Vpc) -> None:
        super().__init__(scope, construct_id)

        # Define the IAM role for the EC2 instances to allow Session Manager access
        role = iam.Role(
            self, 
            "InstanceSSMRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")]
        )

        # Define the Auto Scaling Group
        self.asg = autoscaling.AutoScalingGroup(
            self,
            "DemoAutoScalingGroup",
            vpc=vpc,
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            desired_capacity=2,
            min_capacity=1,
            max_capacity=3,
            role=role
        )

        # Scaling policies
        self.asg.scale_on_cpu_utilization("CpuScaling", target_utilization_percent=50)

        # Add user data
        self.asg.add_user_data(
            """
#!/bin/bash

sudo su
yum update -y
yum install -y httpd

service httpd start
service httpd enable

echo "<h1>Hello World from $(hostname -f)</h1>" > /var/www/html/index.html             
            """
        )
