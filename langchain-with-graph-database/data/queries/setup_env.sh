#!/bin/bash
set -e

STACK_NAME="NeptuneDevStack"
REGION="us-east-1"

echo "Getting Neptune cluster endpoint..."
NEPTUNE_ENDPOINT=$(aws neptune describe-db-clusters \
    --db-cluster-identifier db-neptune-1 \
    --region $REGION \
    --query 'DBClusters[0].Endpoint' \
    --output text)

export NEPTUNE_ENDPOINT
export NEPTUNE_PORT=8182
export NEPTUNE_REGION=$REGION

echo "Environment configured:"
echo "  NEPTUNE_ENDPOINT=$NEPTUNE_ENDPOINT"
echo "  NEPTUNE_PORT=$NEPTUNE_PORT"
echo "  NEPTUNE_REGION=$NEPTUNE_REGION"
echo ""
echo "Run SPARQL queries with:"
echo "  ./run_sparql.sh <query-file>"
