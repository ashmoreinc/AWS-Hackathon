# Business Rules - Offer Management System

## Core Model

### Offer Data

- The lambda should contain the JSON file defined in `./data/offers.json`

### User Data

- The lambda should contain the JSON file defined in `./data/users.json`

### Offer Types

- These are stored in the offer data at `.offerType`. They include, `online`, `in-store`, `local`

### User Connection Types

- **wifi**: User at home
- **mobile**: User on the go

---

## Ranking Rules

The rank should be calculate for each offer based on the following list of rules

- If user.connection_type == 'wifi' and offer.offer_type == 'online' = +1 point
- If user.connection_type == 'mobile' and offer.offer_type != 'online' = +1 point
- If offer.boost = +1 point
- If offer.expiry < 2 weeks, apply an interleaved 0-1 score based on how long is left until the end
- apply 1 point for an offer.commission value of 5, and 0 points for offer.commission value of 0 - interleave other values

---

## Examples

### Example 1: WiFi User

```
User: USER001 (connection_type: wifi)

Available Offers:
  - Amazon Prime (online, boost: true, commission: 5) → Score: +1 (wifi+online) +1 (boost) +1 (commission) = 3 ✓
  - ASOS Sale (online, boost: false, commission: 3) → Score: +1 (wifi+online) +0.6 (commission) = 1.6 ✓
  - Starbucks (in-store, boost: false, commission: 2) → Score: +0.4 (commission) = 0.4
  - Tesco (in-store, boost: false, commission: 0) → Score: 0

Result: Show Amazon Prime and ASOS first
```

### Example 2: Mobile User

```
User: USER002 (connection_type: mobile)

Available Offers:
  - Amazon Prime (online, boost: false, commission: 5) → Score: +1 (commission) = 1
  - Starbucks (in-store, boost: true, commission: 4) → Score: +1 (mobile+in-store) +1 (boost) +0.8 (commission) = 2.8 ✓
  - Tesco (local, boost: false, commission: 3) → Score: +1 (mobile+local) +0.6 (commission) = 1.6 ✓
  - Costa (in-store, boost: false, commission: 2) → Score: +1 (mobile+in-store) +0.4 (commission) = 1.4 ✓

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
  - Top 20 offers (sorted by final_score)
  - User's connection_type
  - offer object
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
Maximum 20 offers returned per request
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
