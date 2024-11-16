from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_sns as sns,
    Duration,
)
from constructs import Construct


class AutoScalingGroupInfra(Construct):

    def __init__(
        self, scope: Construct, construct_id: str, *, asg_config: dict, vpc: ec2.Vpc
    ) -> None:
        super().__init__(scope, construct_id)

        role = iam.Role.from_role_arn(
            self, asg_config["role_id"], "arn:aws:iam::259642033136:role/S3GetPut"
        )

        topic = sns.Topic(
            self,
            asg_config["sns_topic"],
            display_name=asg_config["display_name"],
            enforce_ssl=True,
        )

        topic.add_to_resource_policy(
            iam.PolicyStatement(
                principals=[iam.ServicePrincipal("autoscaling.amazonaws.com")],
                actions=["sns:Publish"],
                resources=[topic.topic_arn],
            )
        )

        notification_configuration = autoscaling.NotificationConfiguration(
            topic=topic,
            scaling_events=autoscaling.ScalingEvents.ALL,
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
            health_check=autoscaling.HealthCheck.elb(grace=Duration.seconds(200)),
            block_devices=[
                autoscaling.BlockDevice(
                    device_name="/dev/xvda",
                    volume=autoscaling.BlockDeviceVolume.ebs(
                        encrypted=True, volume_size=8
                    ),
                )
            ],
            notifications=[notification_configuration],
        )

        # Scaling policies
        self.asg.scale_on_cpu_utilization("CpuScaling", target_utilization_percent=50)

        ssm_parameter = ssm.StringParameter.value_for_string_parameter(
            self, asg_config["ssm_parameter"]
        )
        # Add user data
        self.asg.add_user_data(
            f"""
#!/bin/bash

sudo yum install tomcat10.noarch -y
sudo yum install ruby -y
sudo yum install wget -y

cd /home/ec2-user
wget https://{asg_config["cds_bucket_name"]}.s3.{asg_config["region_identifier"]}.amazonaws.com/latest/install
chmod +x ./install
sudo ./install auto
sudo systemctl start codedeploy-agent
sudo systemctl start tomcat10
            """
        )
