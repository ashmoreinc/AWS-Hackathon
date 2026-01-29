import json
import base64
import redis
import os
from datetime import datetime

# Redis connection (reuse across invocations)
redis_client = redis.Redis(
    host=os.environ['REDIS_ENDPOINT'],
    port=6379,
    decode_responses=True,
    socket_connect_timeout=2,
    socket_keepalive=True
)

def lambda_handler(event, context):
    """
    Processes Kinesis stream records of user offer clicks
    Updates trending category scores in Redis with time-decay
    """
    
    for record in event['Records']:
        # Decode Kinesis data
        payload = json.loads(base64.b64decode(record['kinesis']['data']))
        
        category = payload['category']
        offer_id = payload['offer_id']
        user_id = payload['user_id']
        event_type = payload.get('event_type', 'CLICK')
        timestamp = payload.get('timestamp', int(datetime.now().timestamp()))
        
        # Weight different event types
        event_weights = {'CLICK': 1.0, 'REDEMPTION': 5.0, 'ADD_TO_CART': 3.0, 'VIEW': 0.5}
        weight = event_weights.get(event_type, 1.0)
        
        # Update trending categories with sorted set (score = weighted clicks)
        redis_client.zincrby('trending:categories:1h', weight, category)
        redis_client.zincrby('trending:categories:24h', weight, category)
        redis_client.expire('trending:categories:1h', 3600)
        redis_client.expire('trending:categories:24h', 86400)
        
        # Track category velocity (clicks per minute)
        minute_key = f"trending:velocity:{category}:{timestamp // 60}"
        redis_client.incr(minute_key)
        redis_client.expire(minute_key, 300)
        
        # Track offer-specific engagement
        redis_client.hincrby(f"offer:engagement:{offer_id}", event_type, 1)
        redis_client.expire(f"offer:engagement:{offer_id}", 86400)
        
        # User-category interaction tracking
        redis_client.zincrby(f"user:affinity:{user_id}", weight, category)
        redis_client.expire(f"user:affinity:{user_id}", 2592000)  # 30 days
    
    return {'statusCode': 200, 'processed': len(event['Records'])}
