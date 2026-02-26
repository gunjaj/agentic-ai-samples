#!/bin/bash
set -e

echo "Emptying S3 bucket..."
BUCKET_NAME=$(aws cloudformation describe-stack-resources --stack-name NeptuneDevStack --region us-east-1 --query "StackResources[?ResourceType=='AWS::S3::Bucket'].PhysicalResourceId" --output text 2>/dev/null || echo "")
if [ ! -z "$BUCKET_NAME" ]; then
    aws s3 rm s3://$BUCKET_NAME --recursive --region us-east-1 || true
fi

echo "Destroying Neptune Serverless stack..."
cdk destroy --app "python3 app.py" --force
