from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
)
from constructs import Construct
from backend.asg.asg_infrastructure import AutoScalingGroup

class LoadBalancer(Construct):

    def __init__(self, scope: Construct, construct_id: str, *, vpc: ec2.Vpc) -> None:
        super().__init__(scope, construct_id)

        # Create the load balancer in the DemoVPC
        load_balancer = elbv2.ApplicationLoadBalancer(
            self,
            "DemoLoadBalancer",
            vpc=vpc,
            internet_facing=True,
        )

        # Add listener and open up the load balancer's security group to the world.
        listener = load_balancer.add_listener(
            "Listener",
            port=80,
            protocol= elbv2.ApplicationProtocol.HTTP,
            open=True,
        )

        # Create an AutoScaling group and add it to the load balancing
        asg = AutoScalingGroup(self, "DemoASG", vpc=vpc)
        listener.add_targets("ApplicationFleet", port=80, targets=[asg.asg])
