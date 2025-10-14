#!/usr/bin/env python3

import json
import sys
from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient

def cleanup_gateway(region):
    """Clean up AgentCore Gateway and all targets"""
    try:
        client = GatewayClient(region_name=region)

        with open('gateway_config.json', 'r') as f:
            config = json.load(f)
            gateway_id = config.get('gateway_id')

        if gateway_id:
            print(f'Gateway ID: {gateway_id}')
            
            # Use the built-in cleanup method
            try:
                print('Cleaning up gateway and all targets...')
                client.cleanup_gateway(gateway_id=gateway_id)
                print('Gateway cleanup completed successfully!')
            except Exception as e:
                print(f'Gateway cleanup failed: {e}')
        else:
            print('No gateway ID found')
      
    except FileNotFoundError:
        print('No gateway config found')
    except Exception as e:
        print(f'Gateway cleanup failed: {e}')

if __name__ == "__main__":
    region = sys.argv[1] if len(sys.argv) > 1 else 'us-east-1'
    cleanup_gateway(region)