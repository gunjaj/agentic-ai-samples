#!/usr/bin/env python3
import json
import boto3
import uuid

class StrandsAgentClient:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.ssm = boto3.client('ssm',region_name=self.region)
        self.secrets =boto3.client('secretsmanager',region_name=self.region)

        # Load configuration from AWS services  
        self.agent_arn =self._get_parameter("/strands-agent/agent/agent-arn")

        # Initialize AgentCore client
        self.agentcore_client =boto3.client('bedrock-agentcore',region_name=self.region)

    def _get_parameter(self, name: str) -> str:
        """Get parameter from Parameter Store"""
        try:
            response =self.ssm.get_parameter(Name=name)
            return response['Parameter']['Value']
        except Exception as e:
            print(f"Failed to get parameter {name}: {str(e)}")
            return None

    def invoke_agent(self, prompt: str) -> str:
        """Invoke the AgentCore Runtime agent"""
        if not self.agent_arn:
            return "No agent ARN configured"

        try:
        # Prepare payload
            payload = json.dumps({"prompt":prompt}).encode()

        # Invoke the agent via AgentCoreRuntime
            response =self.agentcore_client.invoke_agent_runtime(
                agentRuntimeArn=self.agent_arn,
                runtimeSessionId=str(uuid.uuid4()),
                payload=payload,
                qualifier="DEFAULT"
            )

            # Process response
            content = []
            for chunk in response.get("response", []):
                content.append(chunk.decode('utf-8'))

                result = json.loads(''.join(content))
                return result.get('result', 'No result')

        except Exception as e:
            return f"Error: {str(e)}"

def main():
    print("Strands Agent Client (AgentCoreRuntime)")
    print("=" * 40)

    client = StrandsAgentClient(region='us-east-1')

    if not client.agent_arn:
        print("Missing agent ARN configuration")
        return
    
    print(f"Connected to agent: {client.agent_arn}")

    # Extract and print the agent URL
    if client.agent_arn:
        # AgentCore Runtime ARN format: arn:aws:bedrock-agentcore:region:account:runtime/agent-id
        # URL format: https://bedrock-agentcore.region.amazonaws.com/runtime/agent-id
        arn_parts = client.agent_arn.split(':')
        if len(arn_parts) >= 6:
            region = arn_parts[3]
            agent_id = arn_parts[5].split('/')[-1]
            agent_url = f"https://bedrock-agentcore.{region}.amazonaws.com/runtime/{agent_id}"
            print(f"Agent URL: {agent_url}")

    while True:
        print("\nOptions:")
        print("1. Ask for weather")
        print("2. Ask for calculation")
        print("3. Exit")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            location = input("Enter location (or press Enter for general): ").strip()
            prompt = f"What's the weather like{' in ' + location if location else ''}?"
            print("\nAsking for weather...")
            result = client.invoke_agent(prompt)
            print(f"Response: {result}")

        elif choice == "2":
            expression = input("Enter calculation (e.g., 2+2*3): ").strip()
            if expression:
                prompt = f"Calculate:{expression}"
                print("\nCalculating...")
                result =client.invoke_agent(prompt)
                print(f"Response: {result}")

        elif choice == "3":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()