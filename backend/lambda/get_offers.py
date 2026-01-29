import json
import boto3
import os
from datetime import datetime, timedelta
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
user_table = dynamodb.Table(os.environ['USER_ACTIVITY_TABLE'])

# Load offers and users data
with open('offers.json', 'r') as f:
    OFFERS = json.load(f)

with open('users.json', 'r') as f:
    USERS = {user['user_id']: user for user in json.load(f)}

def calculate_score(offer, connection_type):
    score = 0.0
    
    # Rule 1: wifi + online = +1
    if connection_type == 'wifi' and offer.get('offerType') == 'online':
        score += 1
    
    # Rule 2: mobile + not online = +1
    if connection_type == 'mobile' and offer.get('offerType') != 'online':
        score += 1
    
    # Rule 3: boost = +1
    if offer.get('boost', False):
        score += 1
    
    # Rule 4: expiry < 2 weeks - interleaved 0-1 score
    expiry_str = offer.get('expiry')
    if expiry_str:
        try:
            expiry_date = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
            now = datetime.now(expiry_date.tzinfo)
            days_left = (expiry_date - now).days
            
            if days_left < 14:
                # Interleave: 14 days = 1.0, 0 days = 0.0
                score += max(0, min(1, days_left / 14))
        except:
            pass
    
    # Rule 5: commission - interleaved 0-1 score (5 = 1.0, 0 = 0.0)
    commission = offer.get('commission', 0)
    score += commission / 5.0
    
    return round(score, 2)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        user_id = body.get('user_id')
        connection_type = body.get('connection_type')
        
        if not user_id or not connection_type:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id required'})
            }
        
        # Get user connection type
        user = USERS.get(user_id, {})
        
        # Calculate scores for all offers
        scored_offers = []
        for offer in OFFERS:
            score = calculate_score(offer, connection_type)
            scored_offers.append({
                'offer': offer,
                'score': score
            })
        
        # Sort by score descending and take top 20
        scored_offers.sort(key=lambda x: x['score'], reverse=True)
        top_offers = scored_offers[:20]
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'user_id': user_id,
                'connection_type': connection_type,
                'offers': [{
                    'offer': item['offer'],
                    'score': item['score']
                } for item in top_offers]
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
