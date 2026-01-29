import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
offers_table = dynamodb.Table(os.environ['OFFERS_TABLE'])
user_table = dynamodb.Table(os.environ.get('USER_ACTIVITY_TABLE', 'UserActivity'))

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        user_id = body.get('user_id')
        connection_type = body.get('connection_type')
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id required'})
            }
        
        # Get user profile if connection_type not provided
        if not connection_type:
            try:
                user_response = user_table.get_item(Key={'PK': f'USER#{user_id}', 'SK': 'PROFILE'})
                user_profile = user_response.get('Item', {})
                connection_type = user_profile.get('connection_type', 'mobile')
            except:
                connection_type = 'mobile'
        
        # Determine preferred offer type
        preferred_type = 'online' if connection_type == 'wifi' else 'high_street'
        
        # Get all active offers
        offers_response = offers_table.scan(
            FilterExpression='#status = :active AND inventory_count > :zero',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':active': 'ACTIVE', ':zero': 0}
        )
        
        offers = offers_response.get('Items', [])
        
        # Score offers
        scored_offers = []
        for offer in offers:
            base_score = float(offer.get('priority', 50))
            type_boost = 50 if offer.get('offer_type') == preferred_type else 0
            total_score = base_score + type_boost
            
            scored_offers.append({
                'offer_id': offer.get('offer_id'),
                'offer_name': offer.get('offer_name'),
                'offer_type': offer.get('offer_type'),
                'discount_type': offer.get('discount_type'),
                'discount_value': float(offer.get('discount_value', 0)),
                'priority': float(offer.get('priority', 0)),
                'inventory_count': int(offer.get('inventory_count', 0)),
                'score': round(total_score, 2)
            })
        
        # Sort and return top 3
        scored_offers.sort(key=lambda x: x['score'], reverse=True)
        top_offers = scored_offers[:3]
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'user_id': user_id,
                'connection_type': connection_type,
                'preferred_offer_type': preferred_type,
                'recommended_offers': top_offers,
                'total_available': len(offers)
            }, default=decimal_default)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
