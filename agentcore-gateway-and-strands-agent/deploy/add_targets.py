"""
Script to add Lambda targets to existing Gateway
"""

from bedrock_agentcore_starter_toolkit.operations.gateway.client import GatewayClient
import json
import logging
import sys

def add_targets(region, gateway_id,calc_function_arn, weather_function_arn):
    print("Adding Lambda targets to Gateway...")
    print(f"Region: {region}")
    print(f"Gateway ID: {gateway_id}")

    # Initialize client
    client = GatewayClient(region_name=region)
    client.logger.setLevel(logging.INFO)

    # Load gateway configuration
    gateway = {
        "gatewayId": gateway_id
    }

    # Add calculator Lambda target
    print("Adding calculator Lambda target...")
    calc_target =client.create_mcp_gateway_target(
        gateway=gateway,
        name="calculator",
        target_type="lambda",
        target_payload={
            "lambdaArn": calc_function_arn,
            "toolSchema": {
                "inlinePayload": [{
                    "name": "calculate",
                    "description": "Perform mathematical calculations",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description":"Mathematical expression to evaluate"
                            }
                        },
                        "required": ["expression"]
                    }
                }]
            }
        }
    )
    print("Calculator target added")

    # Add weather Lambda target 
    print("Adding weather Lambda target...")
    weather_target =client.create_mcp_gateway_target(
        gateway=gateway,
        name="weather",
        target_type="lambda",
        target_payload={
            "lambdaArn": weather_function_arn,
            "toolSchema": {
                "inlinePayload": [{
                    "name": "get_weather",
                    "description": "Get current weather information. Returns general weather if no location specified.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description":"Location to get weather for (optional - defaults to general area)"
                            }
                        },
                    "required": []
                    }
                }]
            }
    }
    )
    print("Weather target added")

    print("All targets added successfully!")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python add_targets.py <region> <gateway_id> <calc_function_arn> <weather_function_arn>")
        sys.exit(1)

    region, gateway_id, calc_function_arn,weather_function_arn = sys.argv[1:5]
    add_targets(region, gateway_id,calc_function_arn, weather_function_arn)

