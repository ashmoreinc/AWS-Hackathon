import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
offers_table = dynamodb.Table(os.environ['OFFERS_TABLE'])

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'MODIFY':
            new_image = record['dynamodb']['NewImage']
            old_image = record['dynamodb']['OldImage']
            
            new_inventory = int(new_image.get('inventory_count', {}).get('N', 0))
            old_inventory = int(old_image.get('inventory_count', {}).get('N', 0))
            
            if new_inventory == 0 and old_inventory > 0:
                offer_id = new_image['offer_id']['S']
                category = new_image['category']['S']
                
                print(f"STOCKOUT DETECTED: {offer_id} ({category})")
                
                # Find pivot offer
                response = offers_table.scan(
                    FilterExpression='category = :cat AND inventory_count > :zero AND offer_id <> :oid',
                    ExpressionAttributeValues={
                        ':cat': category,
                        ':zero': 0,
                        ':oid': offer_id
                    }
                )
                
                candidates = response.get('Items', [])
                
                if candidates:
                    pivot_offer = max(candidates, key=lambda x: float(x.get('priority', 0)))
                    print(f"PIVOT TO: {pivot_offer['offer_id']} (Priority: {pivot_offer['priority']})")
                    
                    # Boost pivot offer priority
                    offers_table.update_item(
                        Key={'PK': f"OFFER#{pivot_offer['offer_id']}", 'SK': 'METADATA'},
                        UpdateExpression='SET priority = priority + :boost',
                        ExpressionAttributeValues={':boost': Decimal('20')}
                    )
                else:
                    print(f"NO PIVOT AVAILABLE for category {category}")
            
            elif new_inventory <= 5 and new_inventory > 0:
                offer_id = new_image['offer_id']['S']
                print(f"LOW INVENTORY ALERT: {offer_id} - {new_inventory} units remaining")
    
    return {'statusCode': 200}
