import json
import time
from typing import List, Dict
from collections import defaultdict

def lambda_handler(event, context):
    user_profile = event['user_profile']
    available_offers = event['available_offers']
    
    current_time = int(time.time())
    scored_offers = []
    
    for offer in available_offers:
        # Relevance: User category affinity match
        category_affinity = user_profile.get('category_affinity', {})
        relevance_score = category_affinity.get(offer['category'], 0.3) * 100
        
        # Urgency: Exponential decay based on time remaining
        time_remaining = offer['expiration_timestamp'] - current_time
        urgency_score = 100 * (1 - min(time_remaining / 86400, 1)) if time_remaining > 0 else 0
        
        # Inventory: Boost high stock items (normalize by max inventory)
        inventory_score = min(offer['inventory_count'] / 10, 100)
        
        # Epsilon-greedy exploration factor
        exploration_bonus = offer.get('priority', 50) * 0.2
        
        # Combined score with weights
        total_score = (
            relevance_score * 0.4 +
            urgency_score * 0.25 +
            inventory_score * 0.2 +
            exploration_bonus * 0.15
        )
        
        scored_offers.append({
            **offer,
            'score': total_score,
            'relevance': relevance_score,
            'urgency': urgency_score,
            'inventory': inventory_score
        })
    
    # Sort by score descending
    scored_offers.sort(key=lambda x: x['score'], reverse=True)
    
    # Diversity filter: Ensure no single category dominates top 3
    top_offers = []
    category_count = defaultdict(int)
    
    for offer in scored_offers:
        category = offer['category']
        # Allow max 2 offers from same category in top 3
        if len(top_offers) < 3 and category_count[category] < 2:
            top_offers.append(offer)
            category_count[category] += 1
        if len(top_offers) == 3:
            break
    
    # If less than 3 offers after diversity filter, fill remaining slots
    if len(top_offers) < 3:
        for offer in scored_offers:
            if offer not in top_offers:
                top_offers.append(offer)
                if len(top_offers) == 3:
                    break
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'optimized_offers': top_offers,
            'total_evaluated': len(available_offers)
        })
    }
