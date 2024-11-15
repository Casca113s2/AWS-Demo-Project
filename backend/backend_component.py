import aws_cdk as cdk
from constructs import Construct
from backend.network.network_infrastructure import Network
from backend.elb.elb_infrastructure import LoadBalancer

class Backend(cdk.Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)

        # Create network (VPC, NACL, SG, ...etc)
        network = Network(self, "DemoNetwork")

        # Create a load balancer
        load_balancer = LoadBalancer(self, "DemoLoadBalancer", vpc=network.vpc)
        