import json
from datetime import datetime, timedelta
import os

# Load data from files
def load_data():
    base_path = os.path.dirname(__file__)
    with open(os.path.join(base_path, 'data', 'offers.json'), 'r') as f:
        offers = json.load(f)
    with open(os.path.join(base_path, 'data', 'users.json'), 'r') as f:
        users = json.load(f)
    
    # Load personalize recommendations
    try:
        with open(os.path.join(base_path, 'data', 'personalize_recommendations.json'), 'r') as f:
            personalize_data = json.load(f)
    except:
        personalize_data = None
    
    return offers, {u['user_id']: u for u in users}, personalize_data

OFFERS, USERS, PERSONALIZE_DATA = load_data()

def calculate_expiry_score(expiry_str):
    """Calculate 0-1 score based on expiry date (tiered)"""
    try:
        expiry = datetime.fromisoformat(expiry_str.replace('Z', '+00:00'))
        now = datetime.now(expiry.tzinfo)
        days_left = (expiry - now).days
        
        if days_left < 7:
            return 1  # Critical urgency
        elif days_left < 14:
            return 0.5  # Urgent
        else:
            return 0  # No urgency
    except:
        return 0

def calculate_commission_score(commission):
    """Calculate 0-1 score based on commission (tiered)"""
    if commission >= 4:
        return 1  # High value
    elif commission >= 2:
        return 0.5  # Medium value
    else:
        return 0  # Low value

def calculate_inventory_scarcity_score(inventory_count):
    """Calculate 0-0.3 score based on inventory scarcity"""
    if inventory_count is None or inventory_count > 100:
        return 0
    elif inventory_count <= 10:
        # Linear interpolation: 10 = 0 points, 1 = 0.3 points
        return 0.3 * (1 - (inventory_count - 1) / 9)
    else:
        # Linear interpolation: 11-100
        return 0.3 * (1 - (inventory_count - 10) / 90)

def calculate_coffee_penalty(offer_name, current_hour):
    """Calculate penalty/boost for coffee offers based on time of day"""
    coffee_keywords = ['coffee', 'café', 'cafe', 'espresso', 'cappuccino', 'latte']
    is_coffee = any(keyword in offer_name.lower() for keyword in coffee_keywords)
    
    if not is_coffee:
        return 0
    
    # Boost coffee 7-9AM
    if 7 <= current_hour < 9:
        return 2
    
    # Penalty after 2PM (linear)
    if current_hour >= 14:
        return -((current_hour - 14) / 10)
    
    return 0

def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', {})
        user_id = body.get('user_id')
        connection_type_override = body.get('connection_type')
        current_time_str = body.get('current_time')  # Format: "HH:MM"
        
        # Parse current time or use actual time
        if current_time_str:
            try:
                hour, minute = map(int, current_time_str.split(':'))
                is_lunch_time = (12 <= hour < 14)
                current_hour = hour
            except:
                is_lunch_time = False
                current_hour = datetime.now().hour
        else:
            now = datetime.now()
            is_lunch_time = (12 <= now.hour < 14)
            current_hour = now.hour
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id required'})
            }
        
        # Get user data
        user = USERS.get(user_id)
        if not user:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'User not found'})
            }
        
        # Use override or stored connection type
        connection_type = connection_type_override or user.get('connection_type', 'mobile')
        
        # Load personalize scores for this user
        personalize_scores = {}
        if PERSONALIZE_DATA and PERSONALIZE_DATA.get('user_id') == user_id:
            for rec in PERSONALIZE_DATA.get('personalize_recommendations', []):
                personalize_scores[rec['offer_id']] = rec['personalize_score']
        
        # Pre-filter: Remove offers with zero inventory and expired offers
        now = datetime.now()
        available_offers = []
        for offer in OFFERS:
            # Check inventory
            if offer.get('inventory_count') is not None and offer.get('inventory_count', 0) <= 0:
                continue
            
            # Check expiry
            try:
                expiry = datetime.fromisoformat(offer['expiry'].replace('Z', '+00:00'))
                expiry_naive = expiry.replace(tzinfo=None)
                if expiry_naive <= now:
                    continue
            except:
                pass
            
            available_offers.append(offer)
        
        # Score offers based on business rules
        scored_offers = []
        for offer in available_offers:
            base_score = 0
            
            # Rule: wifi + online = +1
            if connection_type == 'wifi' and offer['offerType'] == 'online':
                base_score += 1
            
            # Rule: mobile + not online = +1
            if connection_type == 'mobile' and offer['offerType'] != 'online':
                base_score += 1
            
            # Rule: boost = +1
            if offer.get('boost', False):
                base_score += 1
            
            # Rule: expiry < 2 weeks = 0-1 interleaved score
            base_score += calculate_expiry_score(offer['expiry'])
            
            # Rule: commission 0-5 = 0-1 interleaved score
            base_score += calculate_commission_score(offer['commission'])
            
            # Rule: inventory scarcity = 0-0.3 points
            if 'inventory_count' in offer:
                base_score += calculate_inventory_scarcity_score(offer['inventory_count'])
            
            # Rule: gift card penalty = -0.5 points
            if offer.get('offerType') == 'gift-card':
                base_score -= 0.5
            
            # Rule: coffee time adjustment = +2 (7-9AM) or 0 to -1 (after 2PM)
            coffee_adjustment = calculate_coffee_penalty(offer['name'], current_hour)
            base_score += coffee_adjustment
            
            # Add personalize score if available
            personalize_score = personalize_scores.get(offer['id'], 0)
            final_score = base_score + personalize_score
            
            # Lunch time boost: +3 if lunch time and offer.lunch == true
            if is_lunch_time and offer.get('lunch', False):
                final_score += 3
            
            scored_offers.append({
                'id': offer['id'],
                'name': offer['name'],
                'offerType': offer['offerType'],
                'boost': offer.get('boost', False),
                'commission': offer['commission'],
                'expiry': offer['expiry'],
                'inventory_count': offer.get('inventory_count'),
                'lunch': offer.get('lunch', False),
                'image': offer.get('image'),
                'redemptionType': offer.get('redemptionType'),
                'base_score': round(base_score, 2),
                'personalize_score': round(personalize_score, 2),
                'final_score': round(final_score, 2)
            })
        
        # Sort by score
        scored_offers.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Apply diversity: ensure balanced mix of offer types
        # Select top 20 with diversity constraint
        top_offers = []
        offer_type_counts = {}
        max_per_type = 12  # Max 60% of any single type
        
        # First pass: add offers respecting diversity
        for offer in scored_offers:
            offer_type = offer['offerType']
            current_count = offer_type_counts.get(offer_type, 0)
            
            if current_count < max_per_type:
                top_offers.append(offer)
                offer_type_counts[offer_type] = current_count + 1
                
                if len(top_offers) >= 20:
                    break
        
        # If we don't have 20 offers yet, fill remaining slots
        if len(top_offers) < 20:
            for offer in scored_offers:
                if offer not in top_offers:
                    top_offers.append(offer)
                    if len(top_offers) >= 20:
                        break
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'user_id': user_id,
                'connection_type': connection_type,
                'offers': top_offers
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
