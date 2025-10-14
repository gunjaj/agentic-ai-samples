#!/bin/bash

set -e

echo "Provisioning and Deploying Strands Agent on AgentCore Runtime..."

# Variables
REGION=${AWS_REGION:-us-east-1}
STACK_NAME="strands-agent-infrastructure"
AGENT_NAME="strands_agent"
TAG_VALUE="agentcore-gateway-and-strands-agent"

echo "Deploying CloudFormation stack for standard AWS resources..."
aws cloudformation deploy \
    --template-file infrastructure.yaml \
    --stack-name "$STACK_NAME" \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides "TagValue=$TAG_VALUE" \
    --region "$REGION"

echo "CloudFormation stack deployed"

echo "Getting CloudFormation outputs..."
USER_POOL_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
    --output text)

CLIENT_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`ClientId`].OutputValue' \
    --output text)

GATEWAY_ROLE_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`GatewayRoleArn`].OutputValue' \
    --output text)

AGENT_EXECUTION_ROLE_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`AgentExecutionRoleArn`].OutputValue' \
    --output text)

BEDROCK_LOGGING_ROLE_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`BedrockLoggingRoleArn`].OutputValue' \
    --output text)

CALC_FUNCTION_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`CalculatorFunctionArn`].OutputValue' \
    --output text)

WEATHER_FUNCTION_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`WeatherFunctionArn`].OutputValue' \
    --output text)

echo "Setting up test user..."
# Create user with temporary password
aws cognito-idp admin-create-user \
    --user-pool-id $USER_POOL_ID \
    --username testuser \
    --temporary-password TempPass123! \
    --message-action SUPPRESS \
    --region $REGION 2>/dev/null || echo "User already exists"

# Immediately set the same password as permanent
aws cognito-idp admin-set-user-password \
    --user-pool-id $USER_POOL_ID \
    --username testuser \
    --password TempPass123! \
    --permanent \
    --region $REGION

echo "Test user configured"

echo "Creating CloudWatch log group for Bedrock..."
aws logs create-log-group \
    --log-group-name "/aws/bedrock/modelinvocations" \
    --region "$REGION" 2>/dev/null || echo "Log group already exists"

echo "Enabling Bedrock model invocation logging..."
aws bedrock put-model-invocation-logging-configuration \
    --logging-config "{
        \"cloudWatchConfig\": {
            \"logGroupName\":\"/aws/bedrock/modelinvocations\",
            \"roleArn\":\"$BEDROCK_LOGGING_ROLE_ARN\"
        },
        \"textDataDeliveryEnabled\": true,
        \"imageDataDeliveryEnabled\": false,
        \"embeddingDataDeliveryEnabled\": false
    }" \
    --region $REGION

echo "Creating AgentCore Gateway..."
python3 setup_gateway.py "$REGION" "$USER_POOL_ID" "$CLIENT_ID" "$GATEWAY_ROLE_ARN"

# Load gateway configuration
GATEWAY_ID=$(cat gateway_config.json | jq -r '.gateway_id')
GATEWAY_URL=$(cat gateway_config.json | jq -r '.gateway_url')

echo "AgentCore Gateway created: $GATEWAY_ID"

echo "Adding Lambda targets to Gateway..."
python3 add_targets.py "$REGION" "$GATEWAY_ID" "$CALC_FUNCTION_ARN" "$WEATHER_FUNCTION_ARN"

echo "Gateway targets registered"

echo "Deploying Strands Agent to AgentCore Runtime..."
cd ../agent

# Configure agent for deployment
agentcore configure \
    --entrypoint strands_agent.py \
    --name "$AGENT_NAME" \
    --region "$REGION" \
    --execution-role "$AGENT_EXECUTION_ROLE_ARN" \
    --requirements-file requirements.txt \
    --non-interactive

# Deploy agent to AgentCore Runtime
agentcore launch

# Get agent ARN from configuration file
AGENT_ARN=$(grep -A 10 "bedrock_agentcore:" .bedrock_agentcore.yaml | grep "arn:aws:bedrock-agentcore" | grep "runtime" | awk '{print $2}' | head -1)

cd ../deploy

echo "Agent deployed to AgentCore Runtime"
echo "Agent ARN: $AGENT_ARN"

echo "Storing configuration in Parameter Store..."
aws ssm put-parameter \
    --name "/strands-agent/gateway/gateway-url" \
    --value "$GATEWAY_URL" \
    --type "String" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/strands-agent/gateway/gateway-id" \
    --value "$GATEWAY_ID" \
    --type "String" \
    --region $REGION \
    --overwrite

aws ssm put-parameter \
    --name "/strands-agent/agent/agent-arn" \
    --value "$AGENT_ARN" \
    --type "String" \
    --region $REGION \
    --overwrite

echo "Deployment complete!"
echo "Configuration stored in Parameter Store and Secrets Manager"
echo "Client IAM policy: StrandsAgentClientPolicy"