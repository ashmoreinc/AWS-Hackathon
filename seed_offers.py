import boto3
from decimal import Decimal
import time

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Offers')

offers = [
    {"offer_id": "OFF001", "offer_name": "Premium Laptop Deal", "category": "electronics", "discount_type": "PERCENTAGE", "discount_value": 25, "priority": 95, "inventory_count": 50, "expiration_timestamp": int(time.time()) + 86400, "min_purchase_amount": 800, "max_discount_cap": 300, "target_segments": ["premium", "standard"], "margin_impact": 15.5, "status": "ACTIVE"},
    {"offer_id": "OFF002", "offer_name": "Fashion Flash Sale", "category": "fashion", "discount_type": "PERCENTAGE", "discount_value": 40, "priority": 88, "inventory_count": 200, "expiration_timestamp": int(time.time()) + 3600, "min_purchase_amount": 50, "max_discount_cap": 100, "target_segments": ["premium", "standard", "new_user"], "margin_impact": 22.0, "status": "ACTIVE"},
    {"offer_id": "OFF003", "offer_name": "Grocery Essentials", "category": "food", "discount_type": "FIXED_AMOUNT", "discount_value": 15, "priority": 70, "inventory_count": 500, "expiration_timestamp": int(time.time()) + 172800, "min_purchase_amount": 75, "max_discount_cap": 15, "target_segments": ["standard", "new_user"], "margin_impact": 8.5, "status": "ACTIVE"},
    {"offer_id": "OFF004", "offer_name": "Smart Home Bundle", "category": "electronics", "discount_type": "PERCENTAGE", "discount_value": 30, "priority": 82, "inventory_count": 30, "expiration_timestamp": int(time.time()) + 259200, "min_purchase_amount": 500, "max_discount_cap": 200, "target_segments": ["premium"], "margin_impact": 18.0, "status": "ACTIVE"},
    {"offer_id": "OFF005", "offer_name": "Fitness Gear Sale", "category": "sports", "discount_type": "PERCENTAGE", "discount_value": 35, "priority": 75, "inventory_count": 120, "expiration_timestamp": int(time.time()) + 432000, "min_purchase_amount": 100, "max_discount_cap": 80, "target_segments": ["standard", "premium"], "margin_impact": 25.0, "status": "ACTIVE"},
    {"offer_id": "OFF006", "offer_name": "Book Lovers Special", "category": "books", "discount_type": "BOGO", "discount_value": 50, "priority": 60, "inventory_count": 1000, "expiration_timestamp": int(time.time()) + 604800, "min_purchase_amount": 30, "max_discount_cap": 50, "target_segments": ["standard", "new_user"], "margin_impact": 12.0, "status": "ACTIVE"},
    {"offer_id": "OFF007", "offer_name": "Beauty Box Exclusive", "category": "beauty", "discount_type": "PERCENTAGE", "discount_value": 45, "priority": 90, "inventory_count": 80, "expiration_timestamp": int(time.time()) + 7200, "min_purchase_amount": 60, "max_discount_cap": 70, "target_segments": ["premium", "standard"], "margin_impact": 28.0, "status": "ACTIVE"},
    {"offer_id": "OFF008", "offer_name": "Home Decor Clearance", "category": "home", "discount_type": "PERCENTAGE", "discount_value": 50, "priority": 65, "inventory_count": 300, "expiration_timestamp": int(time.time()) + 518400, "min_purchase_amount": 150, "max_discount_cap": 150, "target_segments": ["standard"], "margin_impact": 32.0, "status": "ACTIVE"},
    {"offer_id": "OFF009", "offer_name": "Gaming Console Deal", "category": "electronics", "discount_type": "FIXED_AMOUNT", "discount_value": 100, "priority": 92, "inventory_count": 25, "expiration_timestamp": int(time.time()) + 10800, "min_purchase_amount": 400, "max_discount_cap": 100, "target_segments": ["premium"], "margin_impact": 10.0, "status": "ACTIVE"},
    {"offer_id": "OFF010", "offer_name": "Organic Food Bundle", "category": "food", "discount_type": "PERCENTAGE", "discount_value": 20, "priority": 78, "inventory_count": 400, "expiration_timestamp": int(time.time()) + 345600, "min_purchase_amount": 100, "max_discount_cap": 40, "target_segments": ["premium", "standard"], "margin_impact": 15.0, "status": "ACTIVE"}
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

print("✓ Inserted 10 diverse offers")
