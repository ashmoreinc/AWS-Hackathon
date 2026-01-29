import json
import redis
import os
from typing import List, Dict

redis_client = redis.Redis(
    host=os.environ['REDIS_ENDPOINT'],
    port=6379,
    decode_responses=True,
    socket_connect_timeout=2
)

def lambda_handler(event, context):
    """
    Decision Engine: Queries Redis trending data to boost offer rankings
    Combines static offer scores with real-time trending signals
    """
    
    user_id = event['user_id']
    candidate_offers = event['offers']
    
    # Fetch trending categories from Redis (last 1 hour)
    trending_1h = redis_client.zrevrange('trending:categories:1h', 0, -1, withscores=True)
    trending_map = {cat: score for cat, score in trending_1h}
    max_trending_score = max(trending_map.values()) if trending_map else 1
    
    # Fetch user's personal category affinity
    user_affinity = redis_client.zrevrange(f"user:affinity:{user_id}", 0, -1, withscores=True)
    affinity_map = {cat: score for cat, score in user_affinity}
    max_affinity_score = max(affinity_map.values()) if affinity_map else 1
    
    ranked_offers = []
    
    for offer in candidate_offers:
        category = offer['category']
        offer_id = offer['offer_id']
        
        # Base score from offer priority
        base_score = offer.get('priority', 50)
        
        # Trending boost (0-30 points)
        trending_score = (trending_map.get(category, 0) / max_trending_score) * 30
        
        # Personal affinity boost (0-25 points)
        affinity_score = (affinity_map.get(category, 0) / max_affinity_score) * 25
        
        # Velocity boost: Check if category is accelerating
        current_minute = int(event.get('timestamp', 0)) // 60
        velocity_key = f"trending:velocity:{category}:{current_minute}"
        velocity = int(redis_client.get(velocity_key) or 0)
        velocity_boost = min(velocity * 2, 15)
        
        # Offer-specific engagement
        engagement = redis_client.hgetall(f"offer:engagement:{offer_id}")
        engagement_score = (
            int(engagement.get('CLICK', 0)) * 1 +
            int(engagement.get('REDEMPTION', 0)) * 5 +
            int(engagement.get('ADD_TO_CART', 0)) * 3
        ) / 10
        engagement_score = min(engagement_score, 20)
        
        # Final weighted score
        final_score = (
            base_score * 0.3 +
            trending_score * 0.25 +
            affinity_score * 0.25 +
            velocity_boost * 0.1 +
            engagement_score * 0.1
        )
        
        ranked_offers.append({
            **offer,
            'final_score': round(final_score, 2),
            'trending_boost': round(trending_score, 2),
            'affinity_boost': round(affinity_score, 2),
            'velocity_boost': round(velocity_boost, 2)
        })
    
    # Sort and return top offers
    ranked_offers.sort(key=lambda x: x['final_score'], reverse=True)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'ranked_offers': ranked_offers[:5],
            'trending_categories': list(trending_map.keys())[:5]
        })
    }
