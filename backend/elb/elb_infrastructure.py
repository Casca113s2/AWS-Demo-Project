from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct
from backend.asg.asg_infrastructure import AutoScalingGroupInfra


class LoadBalancerInfra(Construct):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        load_balancer_config: dict,
        vpc: ec2.Vpc,
    ) -> None:
        super().__init__(scope, construct_id)

        # Create a security group for a web server that only allows HTTP (80) and HTTPS (443) traffic
        security_group = ec2.SecurityGroup(
            self,
            load_balancer_config["security_group_id"],
            vpc=vpc,
            allow_all_outbound=True,
        )

        # Allow inbound 
        security_group.add_ingress_rule(
            ec2.Peer.ipv4(
                "116.110.74.83/32"
            ),  # For cdk_nag requirement AwsSolutions-EC23 The Security Group allows for 0.0.0.0/0 or ::/0 inbound access.
            ec2.Port.tcp(80),
            "Allow HTTP traffic",
        )

        security_group.add_ingress_rule(
            ec2.Peer.ipv4(
                "116.110.74.83/32"
            ),  # For cdk_nag requirement AwsSolutions-EC23 The Security Group allows for 0.0.0.0/0 or ::/0 inbound access.
            ec2.Port.tcp(443),
            "Allow HTTPS traffic",
        )

        # Create the load balancer in the DemoVPC
        self.load_balancer = elbv2.ApplicationLoadBalancer(
            self,
            load_balancer_config["load_balancer_id"],
            vpc=vpc,
            internet_facing=True,
            security_group=security_group,
        )

        # Create the target bucket for server access logs
        elb_log_bucket = s3.Bucket.from_bucket_arn(
            self,
            "LogBucket",
            "arn:aws:s3:::demo-elb-access-log-bucket",
        )

        self.load_balancer.log_access_logs(elb_log_bucket)

        # Add listener and open up the load balancer's security group to the world.
        listener = self.load_balancer.add_listener(
            load_balancer_config["listener_id"],
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            open=False,
        )

        # Create an AutoScaling group and add it to the load balancing
        asg = AutoScalingGroupInfra(
            self,
            load_balancer_config["asg_infra"]["asg_infra_id"],
            asg_config=load_balancer_config["asg_infra"]["asg_infra_config"],
            vpc=vpc,
        )

        listener.add_targets(
            load_balancer_config["target_group_id"],
            port=8080,
            targets=[asg.asg],
            health_check=elbv2.HealthCheck(
                path="/helloworld/",
                healthy_http_codes="200",
                port="8080",
            ),
        )
