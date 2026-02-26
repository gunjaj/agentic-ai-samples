#!/usr/bin/env python3
import aws_cdk as cdk
from neptune_stack import NeptuneStack

app = cdk.App()
NeptuneStack(app, "NeptuneDevStack")
app.synth()
