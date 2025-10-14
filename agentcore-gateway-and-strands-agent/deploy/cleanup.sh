#!/bin/bash

set -e

echo "Cleaning up Strands Agent resources..."

# Variables
REGION=${AWS_REGION:-us-east-1}
STACK_NAME="strands-agent-infrastructure"
AGENT_NAME="strands_agent"

echo "Getting resource IDs from Parameter Store..."
GATEWAY_ID=$(aws ssm get-parameter --name "/strands-agent/gateway/gateway-id" --region $REGION --query 'Parameter.Value' --output text 2>/dev/null || echo "")

echo "Deleting AgentCore Runtime agent..."
cd ../agent
agentcore destroy --force 2>/dev/null || echo "Agent not found or already deleted"
cd ../deploy

echo "Deleting AgentCore Gateway targets and gateway..."
python3 cleanup_gateway.py "$REGION" 2>/dev/null || echo "Gateway cleanup failed"

# Remove config files
rm -f gateway_config.json agent_result.json 2>/dev/null || echo "Config files not found"

echo "Deleting Parameter Store entries..."
aws ssm delete-parameter --name "/strands-agent/agent/agent-arn" --region $REGION 2>/dev/null || echo "Agent ARN parameter not found"
aws ssm delete-parameter --name "/strands-agent/gateway/gateway-id" --region $REGION 2>/dev/null || echo "Gateway ID parameter not found"
aws ssm delete-parameter --name "/strands-agent/gateway/gateway-url" --region $REGION 2>/dev/null || echo "Gateway URL parameter not found"

echo "Cleaning up IAM roles created by AgentCore..."
# Delete roles that may have been created by the starter toolkit
aws iam delete-role-policy --role-name "AgentCoreGatewayRole-GWforLambda" --policy-name "GatewayPolicy" --region $REGION 2>/dev/null || echo "Gateway role policy not found"
aws iam delete-role --role-name "AgentCoreGatewayRole-GWforLambda" --region $REGION 2>/dev/null || echo "Gateway role not found"

aws iam delete-role-policy --role-name "AgentCoreAgentRole-$AGENT_NAME" --policy-name "AgentPolicy" --region $REGION 2>/dev/null || echo "Agent role policy not found" 
aws iam delete-role --role-name "AgentCoreAgentRole-$AGENT_NAME" --region $REGION 2>/dev/null || echo "Agent role not found"

echo "Removing Lambda resource policies..."
aws lambda remove-permission \
    --function-name "strands-calculator" \
    --statement-id "AllowAgentCoreGateway" \
    --region $REGION 2>/dev/null || echo "Calculator permission not found"

aws lambda remove-permission \
    --function-name "strands-weather" \
    --statement-id "AllowAgentCoreGateway" \
    --region $REGION 2>/dev/null || echo "Weather permission not found"

echo "Verifying Parameter Store cleanup..."
aws ssm delete-parameter --name "/strands-agent/agent/agent-url" --region $REGION 2>/dev/null || echo "✓ Agent URL parameter already removed"
aws ssm delete-parameter --name "/strands-agent/gateway/gateway-id" --region $REGION 2>/dev/null || echo "✓ Gateway ID parameter already removed"
aws ssm delete-parameter --name "/strands-agent/gateway/gateway-url" --region $REGION 2>/dev/null || echo "✓ Gateway URL parameter already removed"

echo "Disabling Bedrock model invocation logging..."
aws bedrock delete-model-invocation-logging-configuration --region $REGION 2>/dev/null || echo "Bedrock logging not configured"

echo "Deleting CloudFormation stack..."
aws cloudformation delete-stack \
    --stack-name $STACK_NAME \
    --region $REGION

echo "Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete \
    --stack-name $STACK_NAME \
    --region $REGION

echo "Cleanup complete!"
echo "All resources have been deleted."