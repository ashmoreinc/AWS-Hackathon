# Real-Time Trending Categories with Kinesis + Lambda + Redis

## Architecture Flow

```
User Clicks Offer
       ↓
API Gateway → Lambda (Event Producer)
       ↓
Kinesis Data Stream
       ↓
Lambda (kinesis_redis_processor.py) ← Batch processing (100 records/batch)
       ↓
ElastiCache Redis
   ├── trending:categories:1h (Sorted Set)
   ├── trending:categories:24h (Sorted Set)
   ├── trending:velocity:{category}:{minute} (Counter)
   ├── offer:engagement:{offer_id} (Hash)
   └── user:affinity:{user_id} (Sorted Set)
       ↓
Decision Engine Lambda (decision_engine_redis.py)
       ↓
Ranked Offers Response
```

## Component Details

### 1. Event Producer (API Gateway → Lambda)

When a user interacts with an offer, send event to Kinesis:

```python
import boto3
import json

kinesis = boto3.client('kinesis')

def publish_offer_event(user_id, offer_id, category, event_type):
    kinesis.put_record(
        StreamName='offer-engagement-stream',
        Data=json.dumps({
            'user_id': user_id,
            'offer_id': offer_id,
            'category': category,
            'event_type': event_type,  # CLICK, VIEW, REDEMPTION, ADD_TO_CART
            'timestamp': int(time.time())
        }),
        PartitionKey=user_id
    )
```

### 2. Kinesis Stream Configuration

- **Shard count**: Start with 2 shards (2 MB/s write, 4 MB/s read)
- **Retention**: 24 hours
- **Lambda trigger**: Batch size 100, batch window 5 seconds
- **Error handling**: DLQ for failed records

### 3. Redis Data Structures

#### Trending Categories (Sorted Sets)
```
ZREVRANGE trending:categories:1h 0 4 WITHSCORES
→ ["electronics", 245.0, "fashion", 189.0, "food", 156.0]
```

#### Category Velocity (Counters)
```
GET trending:velocity:electronics:28934567
→ "42"  (42 clicks in this minute)
```

#### Offer Engagement (Hashes)
```
HGETALL offer:engagement:OFF001
→ {"CLICK": "127", "REDEMPTION": "23", "ADD_TO_CART": "45"}
```

#### User Affinity (Sorted Sets)
```
ZREVRANGE user:affinity:USER123 0 -1 WITHSCORES
→ ["electronics", 85.0, "fashion", 62.0, "sports", 41.0]
```

### 4. Decision Engine Query Pattern

The Decision Engine Lambda queries Redis in parallel:

```python
# Parallel Redis queries using pipeline
pipe = redis_client.pipeline()
pipe.zrevrange('trending:categories:1h', 0, 9, withscores=True)
pipe.zrevrange(f'user:affinity:{user_id}', 0, 9, withscores=True)
for offer in candidate_offers:
    pipe.hgetall(f"offer:engagement:{offer['offer_id']}")
results = pipe.execute()
```

**Query latency**: ~5-10ms for all Redis operations

### 5. Real-Time Ranking Adjustment

**Scenario**: Electronics category suddenly trending due to flash sale

1. **T=0**: User clicks electronics offer → Kinesis event
2. **T+2s**: Lambda processes batch → Redis ZINCRBY
3. **T+3s**: Next user requests offers → Decision Engine queries Redis
4. **Result**: Electronics offers boosted by +30 trending points

**Before trending boost**:
```
Offer A (Fashion, Priority 90) → Score: 90
Offer B (Electronics, Priority 85) → Score: 85
```

**After trending boost**:
```
Offer A (Fashion, Priority 90) → Score: 90
Offer B (Electronics, Priority 85 + 30 trending) → Score: 115 ✓ Wins
```

### 6. Performance Optimizations

**Lambda Configuration**:
- Memory: 512 MB (sufficient for Redis client)
- Timeout: 30 seconds
- Reserved concurrency: 10 (prevent Redis connection exhaustion)
- VPC: Same VPC as ElastiCache for low latency

**Redis Configuration**:
- Instance: cache.r6g.large (13.07 GB memory)
- Cluster mode: Disabled (simpler for sorted sets)
- Connection pooling: Reuse Redis client across Lambda invocations

**Cost Estimate** (1M events/day):
- Kinesis: $0.015/shard-hour × 2 × 24 = $0.72/day
- Lambda: 1M invocations × 100ms × $0.0000166667 = $1.67/day
- ElastiCache: cache.r6g.large = $3.50/day
- **Total**: ~$6/day or $180/month

### 7. Monitoring & Alerts

**CloudWatch Metrics**:
- Kinesis: IncomingRecords, WriteProvisionedThroughputExceeded
- Lambda: Duration, Errors, IteratorAge
- Redis: CPUUtilization, NetworkBytesIn/Out, CurrConnections

**Alarms**:
- Lambda error rate > 1%
- Kinesis iterator age > 60 seconds (processing lag)
- Redis CPU > 75%

### 8. Testing the System

```bash
# 1. Publish test events to Kinesis
python test_kinesis_producer.py

# 2. Query Redis directly
redis-cli -h your-redis-endpoint.cache.amazonaws.com
> ZREVRANGE trending:categories:1h 0 -1 WITHSCORES

# 3. Invoke Decision Engine
aws lambda invoke \
  --function-name decision-engine-redis \
  --payload '{"user_id":"USER123","offers":[...]}' \
  response.json
```

## Key Benefits

1. **Sub-10ms latency**: Redis queries are extremely fast
2. **Real-time adaptation**: Trending categories update within 2-5 seconds
3. **Personalization**: User affinity tracked per individual
4. **Scalability**: Kinesis auto-scales, Lambda concurrent execution
5. **Cost-effective**: Pay only for actual usage

## Integration with Offer Ranker

Combine both Lambda functions for complete solution:

```
User Request → API Gateway
       ↓
Orchestrator Lambda
       ↓
   ┌───┴───┐
   ↓       ↓
DynamoDB  Redis (Trending)
   ↓       ↓
   └───┬───┘
       ↓
Multi-Armed Bandit Ranker (offer_ranker_lambda.py)
       ↓
Decision Engine (decision_engine_redis.py)
       ↓
Top 3 Optimized Offers
```

This architecture ensures offers are ranked using both historical patterns (DynamoDB) and real-time signals (Redis), maximizing conversion while maintaining diversity.
