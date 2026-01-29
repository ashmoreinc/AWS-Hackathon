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

## API Behavior

### Rule 10: Connection Type Override
```
API allows connection_type override in request:
  POST /offers/recommend
  {
    "user_id": "USER001",
    "connection_type": "mobile"  // Override stored value
  }

This allows testing different scenarios
```

### Rule 11: Response Format
```
API returns:
  - Top 3 offers (sorted by final_score)
  - User's connection_type
  - Preferred offer_type
  - Total available offers count
```
---

## Data Retention

### Rule 13: Activity History
```
User activity stored indefinitely
Can be used for future analytics
No automatic deletion
```
---

## Constraints

### Rule 14: Offer Limits
```
Maximum 3 offers returned per request
Ensures fast response time
Prevents decision paralysis
```

## System Limits

- **API Rate Limit**: None (API Gateway default)
- **DynamoDB**: Pay-per-request (auto-scales)
- **Lambda Timeout**: 30 seconds
- **Kinesis Retention**: 24 hours
- **Max Offer Priority**: 100
- **Min Offer Priority**: 1
