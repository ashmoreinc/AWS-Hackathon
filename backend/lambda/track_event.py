import json
import boto3
import os
import time
import uuid

kinesis = boto3.client('kinesis')
dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table(os.environ['USER_ACTIVITY_TABLE'])

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        
        user_id = body.get('user_id')
        offer_id = body.get('offer_id')
        event_type = body.get('event_type', 'CLICK')
        
        if not all([user_id, offer_id]):
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id and offer_id required'})
            }
        
        timestamp = int(time.time())
        event_id = str(uuid.uuid4())
        
        # Store in DynamoDB for indefinite retention
        user_table.put_item(Item={
            'user_id': user_id,
            'timestamp': timestamp,
            'event_id': event_id,
            'offer_id': offer_id,
            'event_type': event_type
        })
        
        # Send to Kinesis for real-time processing (24h retention)
        kinesis.put_record(
            StreamName=os.environ['KINESIS_STREAM'],
            Data=json.dumps({
                'user_id': user_id,
                'offer_id': offer_id,
                'event_type': event_type,
                'timestamp': timestamp,
                'event_id': event_id
            }),
            PartitionKey=user_id
        )
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'Event tracked successfully',
                'event_id': event_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
