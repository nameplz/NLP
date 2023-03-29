import json
import openai
import os


model = "gpt-3.5-turbo"
openai.api_key = os.environ['openai_api_key']

def lambda_handler(event, context):
    
    request_body = json.loads(event['body'])
    U_message = request_body['userRequest']['utterance'].strip()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": U_message}
    ]
        
    response = openai.ChatCompletion.create(
        model = model,
        messages = messages
    )
        
    answer = response['choices'][0]['message']['content'].strip()
        
    response_body = {
            'version': '2.0',
            'template': {
                'outputs': [
                {
                    'simpleText': {
                        'text': answer
                    }
                }
            ]
        }
    }

        
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response_body)
        }