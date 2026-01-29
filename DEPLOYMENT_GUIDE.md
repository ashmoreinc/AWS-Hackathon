# AWS Deployment Guide - Offer Management System

## Prerequisites

- AWS CLI configured with credentials
- Terraform installed (v1.0+)
- Python 3.11+
- Boto3 installed (`pip install boto3`)

## Deployment Steps

### 1. Deploy Infrastructure

```bash
chmod +x deploy.sh
./deploy.sh
```

This will:
- Package Lambda functions
- Initialize Terraform
- Create DynamoDB tables (Offers, UserActivity)
- Create Kinesis stream
- Deploy Lambda functions
- Configure API Gateway
- Set up DynamoDB Streams triggers

### 2. Seed Initial Data

```bash
python seed_database.py
```

This creates:
- 5 sample offers across different categories
- 3 test users with category preferences

### 3. Get API Endpoint

```bash
cd terraform
terraform output api_endpoint
```

Example output: `https://abc123.execute-api.us-east-1.amazonaws.com/prod`

## API Usage

### Endpoint 1: Get Personalized Offers

**Request:**
```bash
curl -X POST https://YOUR_API_ENDPOINT/offers/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER001"
  }'
```

**Response:**
```json
{
  "user_id": "USER001",
  "recommended_offers": [
    {
      "offer_id": "OFF001",
      "offer_name": "Premium Laptop Deal",
      "category": "electronics",
      "discount_type": "PERCENTAGE",
      "discount_value": 25,
      "priority": 95,
      "inventory_count": 50,
      "score": 87.5
    },
    {
      "offer_id": "OFF002",
      "offer_name": "Fashion Flash Sale",
      "category": "fashion",
      "discount_type": "PERCENTAGE",
      "discount_value": 40,
      "priority": 88,
      "inventory_count": 200,
      "score": 72.3
    },
    {
      "offer_id": "OFF004",
      "offer_name": "Smart Home Bundle",
      "category": "electronics",
      "discount_type": "PERCENTAGE",
      "discount_value": 30,
      "priority": 82,
      "inventory_count": 30,
      "score": 68.9
    }
  ],
  "total_available": 5
}
```

### Endpoint 2: Track User Events

**Request:**
```bash
curl -X POST https://YOUR_API_ENDPOINT/events/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER001",
    "offer_id": "OFF001",
    "category": "electronics",
    "event_type": "CLICK"
  }'
```

**Response:**
```json
{
  "message": "Event tracked successfully",
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Event Types:**
- `CLICK` - User clicked on offer
- `VIEW` - User viewed offer details
- `REDEMPTION` - User redeemed offer
- `ADD_TO_CART` - User added offer to cart
- `DISMISS` - User dismissed offer

## Testing the System

### Test 1: Get Offers for Different Users

```bash
# Premium user (prefers electronics)
curl -X POST https://YOUR_API_ENDPOINT/offers/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER001"}'

# Standard user (prefers fashion)
curl -X POST https://YOUR_API_ENDPOINT/offers/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER002"}'
```

### Test 2: Track Multiple Events

```bash
# User clicks offer
curl -X POST https://YOUR_API_ENDPOINT/events/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER001",
    "offer_id": "OFF001",
    "category": "electronics",
    "event_type": "CLICK"
  }'

# User redeems offer
curl -X POST https://YOUR_API_ENDPOINT/events/track \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "USER001",
    "offer_id": "OFF001",
    "category": "electronics",
    "event_type": "REDEMPTION"
  }'
```

### Test 3: Simulate Inventory Stockout

```python
import boto3
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Offers')

# Reduce inventory to trigger stockout
table.update_item(
    Key={'PK': 'OFFER#OFF001', 'SK': 'METADATA'},
    UpdateExpression='SET inventory_count = :zero',
    ExpressionAttributeValues={':zero': Decimal('0')}
)

# Check CloudWatch Logs for inventory_monitor Lambda
# Should see: "STOCKOUT DETECTED: OFF001 (electronics)"
# Should see: "PIVOT TO: OFF004 (Priority: 82)"
```

## Architecture Components

### DynamoDB Tables

1. **Offers Table**
   - Stores offer catalog
   - Streams enabled for inventory monitoring
   - TTL enabled for automatic expiration

2. **UserActivity Table**
   - Stores user profiles and event history
   - Tracks category affinity
   - Records engagement scores

### Lambda Functions

1. **offer-get-offers**
   - Triggered by: API Gateway POST /offers/recommend
   - Returns: Top 3 personalized offers
   - Scoring: Priority + Relevance + Urgency + Inventory

2. **offer-track-event**
   - Triggered by: API Gateway POST /events/track
   - Stores event in DynamoDB
   - Publishes to Kinesis stream

3. **offer-inventory-monitor**
   - Triggered by: DynamoDB Streams (Offers table)
   - Detects stockouts (inventory = 0)
   - Auto-pivots to next best offer (+20 priority boost)

### Kinesis Stream

- **Name**: offer-engagement-stream
- **Shards**: 2
- **Retention**: 24 hours
- **Purpose**: Real-time event processing for trending analysis

## Monitoring

### CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/offer-get-offers --follow
aws logs tail /aws/lambda/offer-track-event --follow
aws logs tail /aws/lambda/offer-inventory-monitor --follow
```

### Key Metrics to Monitor

- API Gateway: Request count, latency, 4xx/5xx errors
- Lambda: Invocations, duration, errors
- DynamoDB: Read/write capacity, throttles
- Kinesis: IncomingRecords, GetRecords latency

## Cost Estimate

**Monthly costs (assuming 100K requests/month):**

- API Gateway: $0.35 (100K requests)
- Lambda: $0.20 (100K invocations × 512MB × 200ms avg)
- DynamoDB: $1.25 (on-demand pricing)
- Kinesis: $10.80 (2 shards × $0.015/hour × 720 hours)
- **Total**: ~$13/month

## Cleanup

To destroy all resources:

```bash
cd terraform
terraform destroy
```

## Troubleshooting

**Issue**: API returns 500 error
**Solution**: Check Lambda logs for detailed error messages

**Issue**: No offers returned
**Solution**: Verify offers are seeded with `inventory_count > 0` and `status = ACTIVE`

**Issue**: Inventory monitor not triggering
**Solution**: Ensure DynamoDB Streams are enabled on Offers table

**Issue**: Events not tracked
**Solution**: Verify Kinesis stream exists and Lambda has permissions

## Next Steps

1. Add ElastiCache Redis for trending categories (see `kinesis_redis_processor.py`)
2. Implement A/B testing framework
3. Add CloudWatch dashboards
4. Set up SNS alerts for stockouts
5. Deploy to multiple regions for global availability

## Support

For issues or questions, check:
- CloudWatch Logs for error details
- DynamoDB console for data verification
- API Gateway console for endpoint testing
