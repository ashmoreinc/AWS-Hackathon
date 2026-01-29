# Offer Management System - Simulation Suite

## Overview

This simulation suite demonstrates a real-time offer management system that automatically handles inventory stockouts and pivots to the next best offer based on merchant priorities.

## Files

1. **`offer_simulation.py`** - Basic simulation with 100 users and stockout event
2. **`advanced_simulation.py`** - Advanced simulation with DynamoDB Streams integration and auto-pivot logic
3. **`offer_ranker_lambda.py`** - Multi-Armed Bandit offer ranking Lambda
4. **`kinesis_redis_processor.py`** - Kinesis event processor for Redis trending updates
5. **`decision_engine_redis.py`** - Decision engine with Redis trending integration

## Running the Simulations

### Basic Simulation

```bash
python offer_simulation.py
```

**What it demonstrates:**
- 100 users interacting with 5 offers across 200 iterations
- Automatic stockout trigger at iteration 100 for most popular offer
- Traffic redistribution to next best offer based on priority
- Trending score decay over time

**Expected Output:**
```
PRE-STOCKOUT (Iterations 0-100):
   OFF001 (electronics, Priority 95): 45 interactions
   OFF002 (fashion, Priority 88): 28 interactions
   ...

🚨 STOCKOUT EVENT: OFF001 (electronics) - Inventory set to 0

POST-STOCKOUT (Iterations 101-200):
   OFF004 (electronics, Priority 82): 38 interactions  ← PIVOT WINNER
   OFF002 (fashion, Priority 88): 30 interactions
   OFF001 (electronics, Priority 95): 0 interactions [⚠️ OUT OF STOCK]
```

### Advanced Simulation

```bash
python advanced_simulation.py
```

**What it demonstrates:**
- Inventory monitoring via simulated DynamoDB Streams
- Automatic pivot rule generation when stockout detected
- Priority boost (+20 points) for pivot target offer
- Real-time trending score updates
- User affinity tracking
- Low inventory alerts (≤5 units)

**Expected Output:**
```
⚠️  Iteration 142: OFF001 inventory low: 5 units
⚠️  Iteration 148: OFF001 inventory low: 2 units

🔄 AUTO-PIVOT TRIGGERED:
   From: OFF001 (electronics)
   To: OFF004 (electronics, Priority 82)
   Reason: same_category
   Action: Boosting OFF004 priority by +20

PIVOT EFFECTIVENESS:
   OFF001 → OFF004
   Traffic captured: 67 interactions post-pivot
   Pivot efficiency: 89.3% of original traffic
```

## System Architecture

### Automatic Pivot Logic

```
User Redemption → DynamoDB Update
       ↓
DynamoDB Streams Event
       ↓
Lambda: Inventory Monitor
       ↓
   [Inventory ≤ 0?]
       ↓ YES
Generate Pivot Rule:
  1. Find same category offers with inventory > 0
  2. Select highest priority
  3. Apply +20 priority boost
  4. Update Decision Engine
       ↓
Next User Request → Decision Engine
       ↓
Ranked Offers (pivot target boosted)
       ↓
User receives next best offer automatically
```

### Scoring Formula (Advanced Simulation)

```python
Total Score = Base Priority 
            + User Affinity Boost (35 points)
            + Trending Boost (dynamic)
            + Pivot Boost (20 points if pivot target)
            + Inventory Urgency (10 points if < 20 units)
```

## Key Metrics

### Pre-Stockout Phase
- Most popular offer receives 40-50% of traffic
- Traffic distribution follows user affinity patterns
- Inventory depletes based on redemption rate (~25%)

### Post-Stockout Phase
- Stockout offer receives 0% traffic (filtered out)
- Pivot target captures 80-90% of original traffic
- Same-category offers preferred (user affinity maintained)
- Fallback to highest priority if no same-category available

## Integration with AWS Services

### DynamoDB Streams Configuration

```python
# Enable streams on Offers table
StreamSpecification={
    'StreamEnabled': True,
    'StreamViewType': 'NEW_AND_OLD_IMAGES'
}

# Lambda trigger configuration
EventSourceMapping={
    'EventSourceArn': 'arn:aws:dynamodb:region:account:table/Offers/stream',
    'FunctionName': 'inventory-monitor-lambda',
    'StartingPosition': 'LATEST',
    'BatchSize': 10,
    'MaximumBatchingWindowInSeconds': 1
}
```

### Inventory Monitor Lambda (Pseudo-code)

```python
def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'MODIFY':
            new_image = record['dynamodb']['NewImage']
            old_image = record['dynamodb']['OldImage']
            
            new_inventory = int(new_image['inventory_count']['N'])
            old_inventory = int(old_image['inventory_count']['N'])
            
            if new_inventory == 0 and old_inventory > 0:
                # Stockout detected
                offer_id = new_image['offer_id']['S']
                trigger_pivot(offer_id)
```

## Performance Characteristics

### Latency
- **Stockout detection**: 100-500ms (DynamoDB Streams latency)
- **Pivot rule generation**: 50-100ms (Lambda execution)
- **Next user request**: Immediate (pivot rule already applied)

### Throughput
- **Concurrent users**: 1000+ (Lambda auto-scaling)
- **Redemptions/second**: 100+ (DynamoDB write capacity)
- **Pivot activation**: <1 second from stockout to traffic redirect

### Cost (1M interactions/day)
- DynamoDB: $0.25/million writes = $0.25/day
- DynamoDB Streams: $0.02/100K reads = $0.20/day
- Lambda (inventory monitor): $0.20/million invocations = $0.20/day
- **Total**: ~$0.65/day or $20/month

## Testing Scenarios

### Scenario 1: Single Offer Stockout
```bash
python offer_simulation.py
```
Expected: Traffic redirects to same-category, next-highest-priority offer

### Scenario 2: Category-Wide Stockout
Modify `advanced_simulation.py`:
```python
# Set all electronics offers to low inventory
for offer in offers:
    if offer['category'] == 'electronics':
        offer['inventory'] = 10
```
Expected: Traffic redirects to highest-priority offer in any category

### Scenario 3: Flash Sale Surge
Modify redemption probability:
```python
action = 'REDEMPTION' if random.random() < 0.6 else 'CLICK'  # 60% redemption
```
Expected: Multiple stockouts, cascading pivots

## Monitoring & Alerts

### CloudWatch Metrics to Track
- `OfferStockouts` (count)
- `PivotActivations` (count)
- `PivotEfficiency` (percentage of traffic captured)
- `InventoryDepletionRate` (units/hour)

### Recommended Alarms
- Stockout rate > 5 per hour
- Pivot efficiency < 70%
- Inventory depletion rate > 100 units/hour

## Next Steps

1. **Deploy to AWS**: Use provided Lambda functions with actual DynamoDB and Kinesis
2. **Add ML Model**: Replace static scoring with SageMaker inference
3. **A/B Testing**: Compare pivot strategies (same-category vs highest-priority)
4. **Real-time Dashboard**: Visualize offer performance and pivot events

## Troubleshooting

**Issue**: Pivot not capturing enough traffic
**Solution**: Increase pivot boost from +20 to +30 points

**Issue**: Too many stockouts
**Solution**: Implement inventory reservation system (hold inventory for 5 minutes on offer view)

**Issue**: Users seeing same offers repeatedly
**Solution**: Increase diversity penalty in ranking algorithm

---

**Author**: Senior Data Architect  
**Version**: 1.0  
**Last Updated**: 2024
