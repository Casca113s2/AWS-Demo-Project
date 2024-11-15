#!/usr/bin/env python3
import os
import aws_cdk as cdk
from backend.backend_component import Backend

app = cdk.App()

env = cdk.Environment(account="259642033136", region="ap-southeast-1")

Backend(app, "Backend", env=env)

app.synth()
