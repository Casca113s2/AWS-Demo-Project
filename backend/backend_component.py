import aws_cdk as cdk
from constructs import Construct
from backend.network.network_infrastructure import NetworkInfra
from backend.elb.elb_infrastructure import LoadBalancerInfra


class Backend(cdk.Stack):
    def __init__(self, scope: Construct, id_: str, *, backend_config: dict, **kwargs):
        super().__init__(scope, id_, **kwargs)

        # Create network
        network_infra = NetworkInfra(
            self,
            backend_config["network_infra"]["network_infra_id"],
            network_infra_config=backend_config["network_infra"]["network_infra_config"],
        )

        # Create a load balancer
        LoadBalancerInfra(
            self,
            backend_config["load_balancer_infra"]["load_balancer_infra_id"],
            load_balancer_config=backend_config["load_balancer_infra"][
                "load_balancer_infra_config"
            ],
            vpc=network_infra.vpc,
        )
