#!/usr/bin/env python3
import os
os.environ['WANDB_API_KEY'] = 'fbd5089fe8ff8a2f6dfc053ad7ac625ab10a7a2f'

import wandb
api = wandb.Api()
user = api.viewer
username = "ir2023"
print(username)
