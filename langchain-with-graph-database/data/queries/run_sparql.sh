#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./run_sparql.sh <query-file>"
    exit 1
fi

QUERY_FILE=$1

if [ -z "$NEPTUNE_ENDPOINT" ]; then
    echo "Setting up environment..."
    STACK_NAME="NeptuneDevStack"
    REGION="us-east-1"
    
    NEPTUNE_ENDPOINT=$(aws neptune describe-db-clusters \
        --db-cluster-identifier db-neptune-1 \
        --region $REGION \
        --query 'DBClusters[0].Endpoint' \
        --output text)
    
    NEPTUNE_PORT=8182
    NEPTUNE_REGION=$REGION
fi

QUERY=$(cat "$QUERY_FILE")

# Create temp file with form data
TEMP_FILE=$(mktemp)
echo -n "query=" > "$TEMP_FILE"
echo -n "$QUERY" | python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.stdin.read()), end='')" >> "$TEMP_FILE"

awscurl --service neptune-db \
    --region $NEPTUNE_REGION \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d @"$TEMP_FILE" \
    "https://$NEPTUNE_ENDPOINT:$NEPTUNE_PORT/sparql"

rm "$TEMP_FILE"
