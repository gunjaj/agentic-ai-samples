# Agentcore Gateway and Strands Agent

This directory contains a comprehensive sample implementation of an agentic AI system using the Agentcore Gateway and Strands Agent. The project demonstrates how to deploy, manage, and clean up a multi-component AI agent system on AWS, integrating Lambda functions, IAM roles, Parameter Store, and Bedrock model invocation logging.

## Directory Structure

- `agent/` — Contains the Strands Agent code, including the main agent logic and dependencies.
- `client/` — Example client code to interact with the Strands Agent.
- `deploy/` — Deployment and cleanup scripts, CloudFormation templates, and helper utilities for managing AWS resources.
- `external_services/` — Example external service integrations (e.g., calculator, weather) that can be invoked by the agent.

## Key Components

### 1. Strands Agent (`agent/`)
- Implements the core agent logic in Python (`strands_agent.py`).
- Includes a `Dockerfile` and `requirements.txt` for containerized deployment.

### 2. Client (`client/`)
- Provides a sample client (`strands_client.py`) to interact with the agent, demonstrating request/response flows.

### 3. Deployment (`deploy/`)
- `deploy.sh`: Script to deploy the full stack, including Lambda functions, IAM roles, and Parameter Store entries.
- `cleanup.sh`: Script to clean up all AWS resources created by the deployment, including Lambda permissions, IAM roles, Parameter Store entries, Bedrock logging, and the CloudFormation stack.
- `infrastructure.yaml`: CloudFormation template defining the AWS infrastructure.
- Helper scripts for managing gateway targets and setup.

### 4. External Services (`external_services/`)
- Example Lambda functions (e.g., `calculator.py`, `weather.py`) that the agent can invoke as part of its reasoning and action-taking process. For now the code is part of infrastructure.yaml to avoid creating a S3 bucket for uploading zip files

## Usage

1. **Deployment**: Use the `deploy.sh` script to provision all necessary AWS resources and deploy the agent and its supporting services.
2. **Interaction**: Use the client code to interact with the deployed agent, sending requests and receiving responses.
3. **Cleanup**: Run `cleanup.sh` to remove all AWS resources, including Lambda permissions, IAM roles, Parameter Store entries, Bedrock logging configuration, and the CloudFormation stack. Some of the files are implemented via SDK. Cloudformation/CLI is not yet released.

## Prerequisites
- AWS CLI configured with appropriate permissions
- Python 3.11+
- Docker (for containerized agent deployment)

## Notes
- The scripts are designed to be idempotent and safe to run multiple times.
- Error handling is included to gracefully handle missing resources during cleanup.
- The sample demonstrates best practices for managing cloud resources in an agentic AI system.

## License
See the root `LICENSE` file for license information.

## Support
For questions or issues, please refer to the main repository or open an issue.
