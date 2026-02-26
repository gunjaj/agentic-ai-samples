#!/bin/bash
set -e

echo "Deploying Neptune Serverless stack..."
cdk deploy --app "python3 app.py" --require-approval never

echo "Enabling public access on Neptune instance..."
aws neptune modify-db-instance \
    --region us-east-1 \
    --db-instance-identifier db-neptune-1-instance-1 \
    --publicly-accessible \
    --apply-immediately

echo "Deployment complete!"
