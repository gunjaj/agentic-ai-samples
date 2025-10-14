import json

def lambda_handler(event, context):
    """
    Weather Lambda - provides weather information
    """
    try:
        # Parse request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        location = body.get('location','general')

        # Mock weather data
        weather_data = {
            'location': location,
            'temperature': '72°F',
            'condition': 'Partly cloudy',
            'humidity': '45%'
        }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'result': f"Weather for {location}: {weather_data['temperature']},{weather_data['condition']}, Humidity: {weather_data['humidity']}"
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error':f"Weather error: {str(e)}"})
        }