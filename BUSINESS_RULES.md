# Business Rules - Offer Management System

## Core Model

### Offer Types
- **high_street**: Physical store offers (Starbucks, Tesco, Costa)
- **online**: Digital/delivery offers (Amazon, ASOS, Deliveroo)

### User Connection Types
- **wifi**: User at home
- **mobile**: User on the go

---

## Ranking Rules

### Rule 1: Connection-Based Targeting
```
IF user.connection_type == "wifi" THEN
    Prioritize offers WHERE offer_type == "online"
    Apply +50 priority boost to online offers
ELSE IF user.connection_type == "mobile" THEN
    Prioritize offers WHERE offer_type == "high_street"
    Apply +50 priority boost to high_street offers
```

### Rule 2: Base Priority
```
All offers have base priority (1-100)
Higher priority = more important to merchant
```

### Rule 3: Final Score Calculation
```
final_score = base_priority + connection_type_boost

WHERE:
  connection_type_boost = 50 if offer matches user location context
  connection_type_boost = 0 otherwise
```

### Rule 4: Offer Filtering
```
Only show offers WHERE:
  - status == "ACTIVE"
  - inventory_count > 0
  - expiration_timestamp > current_time
```

---

## Examples

### Example 1: WiFi User
```
User: USER001 (connection_type: wifi)

Available Offers:
  - Amazon Prime (online, priority: 95) → Score: 145 ✓
  - ASOS Sale (online, priority: 88) → Score: 138 ✓
  - Starbucks (high_street, priority: 90) → Score: 90
  - Tesco (high_street, priority: 85) → Score: 85

Result: Show Amazon Prime and ASOS first
```

### Example 2: Mobile User
```
User: USER002 (connection_type: mobile)

Available Offers:
  - Amazon Prime (online, priority: 95) → Score: 95
  - Starbucks (high_street, priority: 90) → Score: 140 ✓
  - Tesco (high_street, priority: 85) → Score: 135 ✓
  - Costa (high_street, priority: 80) → Score: 130 ✓

Result: Show Starbucks, Tesco, and Costa first
```

---

## Inventory Management

### Rule 5: Stockout Detection
```
WHEN offer.inventory_count reaches 0:
  1. DynamoDB Streams triggers inventory_monitor Lambda
  2. Find next best offer in same category
  3. Apply +20 priority boost to pivot offer
  4. Redirect future traffic automatically
```

### Rule 6: Low Stock Alert
```
WHEN offer.inventory_count <= 5:
  - Log warning
  - Continue showing offer
  - Monitor for potential stockout
```

---

## Event Tracking

### Rule 7: Event Types
```
Supported events:
  - CLICK: User clicked on offer
  - VIEW: User viewed offer details
  - REDEMPTION: User redeemed offer (decrements inventory)
  - ADD_TO_CART: User added to cart
  - DISMISS: User dismissed offer
```

### Rule 8: Event Processing
```
All events:
  1. Stored in DynamoDB (UserActivity table)
  2. Published to Kinesis stream
  3. Available for analytics
```

---

## API Behavior

### Rule 9: Connection Type Override
```
API allows connection_type override in request:
  POST /offers/recommend
  {
    "user_id": "USER001",
    "connection_type": "mobile"  // Override stored value
  }

This allows testing different scenarios
```

### Rule 10: Response Format
```
API returns:
  - Top 3 offers (sorted by final_score)
  - User's connection_type
  - Preferred offer_type
  - Total available offers count
```

---

## Data Retention

### Rule 11: Offer Expiration
```
DynamoDB TTL enabled on expiration_timestamp
Expired offers automatically deleted
No manual cleanup required
```

### Rule 12: Activity History
```
User activity stored indefinitely
Can be used for future analytics
No automatic deletion
```

---

## Constraints

### Rule 13: Offer Limits
```
Maximum 3 offers returned per request
Ensures fast response time
Prevents decision paralysis
```

### Rule 14: Inventory Constraints
```
Inventory cannot go negative
Redemption fails if inventory = 0
Concurrent redemptions handled by DynamoDB
```

---

## Future Enhancements (Not Implemented)

### Potential Rule 15: Time-Based Targeting
```
Morning (6am-12pm): Prioritize coffee/breakfast offers
Lunch (12pm-2pm): Prioritize food delivery
Evening (6pm-10pm): Prioritize dinner/entertainment
```

### Potential Rule 16: Location-Based Radius
```
For high_street offers:
  - Use GPS to find nearby stores
  - Only show offers within 5km radius
  - Sort by distance
```

### Potential Rule 17: Personalization
```
Track user preferences over time
Learn which offer types user prefers
Adjust scoring based on history
```

---

## System Limits

- **API Rate Limit**: None (API Gateway default)
- **DynamoDB**: Pay-per-request (auto-scales)
- **Lambda Timeout**: 30 seconds
- **Kinesis Retention**: 24 hours
- **Max Offer Priority**: 100
- **Min Offer Priority**: 1
