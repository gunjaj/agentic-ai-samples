from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.streamable_http import streamablehttp_client
import json
import boto3

app = BedrockAgentCoreApp()

def create_streamable_http_transport(mcp_url:str, access_token: str):
    return streamablehttp_client(mcp_url, headers={"Authorization": f"Bearer {access_token}"})

def get_full_tools_list(client):
    """Get all tools with pagination support"""
    more_tools = True
    tools = []
    pagination_token = None
    while more_tools:
        tmp_tools = client.list_tools_sync(pagination_token=pagination_token)
        tools.extend(tmp_tools)
        if tmp_tools.pagination_token is None:
            more_tools = False
        else:
            more_tools = True
            pagination_token = tmp_tools.pagination_token
    return tools

@app.entrypoint
def invoke(payload):
    """AI agent function with MCP tools from Gateway"""
    user_message = payload.get("prompt", "Hello! How can I help you today?")

    # Auto-handle weather questions
    if "weather" in user_message.lower():
        user_message = "What's the weather like?"

    try:
    # Get configuration from Parameter Store
        ssm = boto3.client('ssm')

        gateway_url = ssm.get_parameter(Name="/strands-agent/gateway/gateway-url")['Parameter']['Value']
        region = ssm.get_parameter(Name="/strands-agent/config/region")['Parameter']['Value']
        user_pool_id = ssm.get_parameter(Name="/strands-agent/cognito/user-pool-id")['Parameter']['Value']
        client_id = ssm.get_parameter(Name="/strands-agent/cognito/client-id")['Parameter']['Value']

        # Get credentials from Secrets Manager
        secrets = boto3.client('secretsmanager')
        credentials = json.loads(secrets.get_secret_value(SecretId="strands-agent/test-user")['SecretString'])

        # Get access token using Cognito
        cognito = boto3.client('cognito-idp', region_name=region)
        auth_response = cognito.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': credentials['username'],
                'PASSWORD': credentials['password']
            }
        )
        access_token = auth_response['AuthenticationResult']['AccessToken']

        # Setup Bedrock model
        model = BedrockModel(model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0")

        # Setup MCP client
        mcp_client = MCPClient(lambda: create_streamable_http_transport(gateway_url, access_token))

        with mcp_client:
            # Get MCP tools from gateway
            tools = get_full_tools_list(mcp_client)

            # Create agent with tools
            agent = Agent(model=model, tools=tools)

            # Invoke agent
            result = agent(user_message)
            return {"result": result.message}

    except Exception as e:
    # Return error details instead of silent fallback
        model = BedrockModel(model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0")
        agent = Agent(model=model)
        result = agent(user_message)
        return {"result": f"Agent error (no tools): {str(e)} | Response: {result.message}"}

if __name__ == "__main__":
    app.run()


