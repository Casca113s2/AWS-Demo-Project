#!/usr/bin/env python3
import json
import os
import sys
import aws_cdk as cdk
from backend.backend_component import Backend
import cdk_nag

# Get the environment from an argument or default to 'dev'
env = os.getenv("environment", "dev")

# Load the appropriate config file
config_file = f"config/{env}.json"
try:
    with open(config_file) as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"Configuration file for environment '{env}' not found.")
    sys.exit(1)

app = cdk.App()

Backend(
    app,
    config["backend"]["backend_id"],
    backend_config=config["backend"]["backend_config"],
    env=cdk.Environment(
        account=config["environment"]["account"], region=config["environment"]["region"]
    ),
)

cdk.Aspects.of(app).add(cdk_nag.AwsSolutionsChecks(verbose=True))

app.synth()
