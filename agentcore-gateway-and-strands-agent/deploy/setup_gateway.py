"""
Setup script to create Gateway only
Based on AWS documentation example
"""

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import json
import logging
import time
import sys

def setup_gateway(region, user_pool_id, client_id, gateway_role_arn):
    print("Setting up AgentCore Gateway...")
    print(f"Region: {region}")

    # Initialize client
    client = GatewayClient(region_name=region)
    client.logger.setLevel(logging.INFO)

    # Use existing Cognito configuration
    print("Using existing Cognito authorization...")
    authorizer_config = {
        "customJWTAuthorizer": {
            "allowedClients": [client_id],
            "discoveryUrl": f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/openid-configuration"
        }
    }

    # Create Gateway
    print("Creating Gateway...")
    gateway = client.create_mcp_gateway(
        name="GWforLambda",
        role_arn=gateway_role_arn,
        authorizer_config=authorizer_config,
        enable_semantic_search=True,
    )
    print(f"Gateway created: {gateway['gatewayUrl']}")

    # Fix IAM permissions
    client.fix_iam_permissions(gateway)
    print("Waiting 30s for IAM propagation...")
    time.sleep(30)
    print("IAM permissions configured")

    # Save configuration
    config = {
        "gateway_url": gateway["gatewayUrl"],
        "gateway_id": gateway["gatewayId"],
        "region": region
    }

    with open("gateway_config.json", "w") as f:
        json.dump(config, f, indent=2)

    print("Gateway setup complete!")
    print(f"Gateway URL: {gateway['gatewayUrl']}")
    print(f"Gateway ID: {gateway['gatewayId']}")
    print("Configuration saved to: gateway_config.json")

    return config

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python setup_gateway.py <region> <user_pool_id> <client_id> <gateway_role_arn>")
        sys.exit(1)

    region, user_pool_id, client_id, gateway_role_arn = sys.argv[1:5]
    setup_gateway(region, user_pool_id, client_id, gateway_role_arn)