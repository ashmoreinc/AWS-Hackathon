import boto3
from decimal import Decimal
import time
import sys
import os

os.environ['AWS_PROFILE'] = 'AdministratorAccess-851311377237'
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def seed_offers():
    table = dynamodb.Table('Offers')
    
    offers = [
        {"offer_id": "OFF001", "offer_name": "Starbucks Coffee", "offer_type": "high_street", "discount_type": "PERCENTAGE", "discount_value": 20, "priority": 90, "inventory_count": 100, "expiration_timestamp": int(time.time()) + 86400, "status": "ACTIVE"},
        {"offer_id": "OFF002", "offer_name": "Amazon Prime Deal", "offer_type": "online", "discount_type": "PERCENTAGE", "discount_value": 30, "priority": 95, "inventory_count": 200, "expiration_timestamp": int(time.time()) + 172800, "status": "ACTIVE"},
        {"offer_id": "OFF003", "offer_name": "Tesco In-Store", "offer_type": "high_street", "discount_type": "FIXED_AMOUNT", "discount_value": 10, "priority": 85, "inventory_count": 150, "expiration_timestamp": int(time.time()) + 259200, "status": "ACTIVE"},
        {"offer_id": "OFF004", "offer_name": "ASOS Online Sale", "offer_type": "online", "discount_type": "PERCENTAGE", "discount_value": 40, "priority": 88, "inventory_count": 300, "expiration_timestamp": int(time.time()) + 432000, "status": "ACTIVE"},
        {"offer_id": "OFF005", "offer_name": "Costa Coffee", "offer_type": "high_street", "discount_type": "PERCENTAGE", "discount_value": 15, "priority": 80, "inventory_count": 120, "expiration_timestamp": int(time.time()) + 86400, "status": "ACTIVE"},
        {"offer_id": "OFF006", "offer_name": "Deliveroo Discount", "offer_type": "online", "discount_type": "FIXED_AMOUNT", "discount_value": 5, "priority": 92, "inventory_count": 250, "expiration_timestamp": int(time.time()) + 172800, "status": "ACTIVE"},
    ]
    
    with table.batch_writer() as batch:
        for offer in offers:
            item = {
                "PK": f"OFFER#{offer['offer_id']}",
                "SK": "METADATA",
                "created_at": int(time.time()),
                **{k: Decimal(str(v)) if isinstance(v, (int, float)) else v for k, v in offer.items()}
            }
            batch.put_item(Item=item)
    
    print(f"✓ Seeded {len(offers)} offers")

def seed_users():
    table = dynamodb.Table('UserActivity')
    
    users = [
        {"user_id": "USER001", "connection_type": "wifi"},
        {"user_id": "USER002", "connection_type": "mobile"},
        {"user_id": "USER003", "connection_type": "wifi"},
    ]
    
    for user in users:
        table.put_item(Item={
            'PK': f"USER#{user['user_id']}",
            'SK': 'PROFILE',
            'user_id': user['user_id'],
            'connection_type': user['connection_type'],
            'created_at': int(time.time())
        })
    
    print(f"✓ Seeded {len(users)} users")

if __name__ == "__main__":
    try:
        print("🌱 Seeding database...")
        seed_offers()
        seed_users()
        print("✅ Database seeded successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
