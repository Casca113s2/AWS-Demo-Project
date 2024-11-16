from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
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
        vpc: ec2.Vpc
    ) -> None:
        super().__init__(scope, construct_id)

        # Create the load balancer in the DemoVPC
        load_balancer = elbv2.ApplicationLoadBalancer(
            self,
            load_balancer_config["load_balancer_id"],
            vpc=vpc,
            internet_facing=True,
        )

        # Add listener and open up the load balancer's security group to the world.
        listener = load_balancer.add_listener(
            load_balancer_config["listener_id"],
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            open=True,
        )

        # Create an AutoScaling group and add it to the load balancing
        asg = AutoScalingGroupInfra(
            self,
            load_balancer_config["asg_infra"]["asg_infra_id"],
            asg_config=load_balancer_config["asg_infra"]["asg_infra_config"],
            vpc=vpc,
        )
        listener.add_targets(
            load_balancer_config["target_group_id"], port=8080, targets=[asg.asg]
        )
