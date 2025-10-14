import json

def lambda_handler(event, context):
    """
    Calculator Lambda - performs mathematical calculations
    """
    try:
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
            expression = body.get('expression', '')

        if not expression:
            return {
                'statusCode': 400,
                'body': json.dumps({'error':'Missing expression parameter'})
            }

        # Safe calculation
        result = eval(expression, {"__builtins__": {}}, {})

        return {
            'statusCode': 200,
            'body': json.dumps({
                'result': f"The result of {expression} is {result}"
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error':f"Calculation error: {str(e)}"})
        }