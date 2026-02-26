#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./bulk_load.sh <data-file>"
    exit 1
fi

DATA_FILE=$1
STACK_NAME="NeptuneDevStack"
REGION="us-east-1"

echo "Getting Neptune cluster endpoint..."
NEPTUNE_ENDPOINT=$(aws neptune describe-db-clusters \
    --db-cluster-identifier db-neptune-1 \
    --region $REGION \
    --query 'DBClusters[0].Endpoint' \
    --output text)

echo "Getting S3 bucket name..."
BUCKET_NAME=$(aws cloudformation describe-stack-resources \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query "StackResources[?ResourceType=='AWS::S3::Bucket'].PhysicalResourceId" \
    --output text)

echo "Getting IAM role ARN..."
ROLE_NAME=$(aws cloudformation describe-stack-resources \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query "StackResources[?LogicalResourceId=='NeptuneS3Role8D81371E'].PhysicalResourceId" \
    --output text)

# Get full ARN
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/$ROLE_NAME"

echo "Uploading data to S3..."
aws s3 cp $DATA_FILE s3://$BUCKET_NAME/ --region $REGION

FILE_NAME=$(basename $DATA_FILE)
S3_URI="s3://$BUCKET_NAME/$FILE_NAME"

echo "Starting bulk load..."
aws neptunedata start-loader-job \
    --endpoint-url "https://$NEPTUNE_ENDPOINT:8182" \
    --source "$S3_URI" \
    --format turtle \
    --s3-bucket-region "$REGION" \
    --iam-role-arn "$ROLE_ARN" \
    --region "$REGION"

echo "Bulk load initiated successfully"
