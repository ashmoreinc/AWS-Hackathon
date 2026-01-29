# Business Rules - Offer Management System

## Hackathon Challenge

Create a dynamic system that optimises which discounts to display to each user in real-time based on their profile, redemption history, current inventory, merchant priorities, and engagement patterns. The solution should intelligently balance showing high-value offers that drive conversions with maintaining a diverse mix of deals, while adapting to real-time factors like trending categories, expiring promotions and other environmental factors.

---

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

The rank should be calculated for each offer based on the following scoring system:

### Pre-filtering Rules

- **Inventory Check**: Offers must have inventory available
  - Only include offers where inventory_count > 0 (if inventory field exists)
  - Offers with no inventory field are always included

- **Expiry Check**: Offers must not be expired
  - Only include offers where expiry date is in the future
  - Expired offers are excluded from results

### Base Contextual Scoring (0-4 points)

- **Connection Match**: +1 point
  - If user.connection_type == 'wifi' and offer.offerType == 'online' = +1 point
  - If user.connection_type == 'mobile' and offer.offerType != 'online' = +1 point

- **Merchant Priority (Boost)**: +1 point
  - If offer.boost == true = +1 point

- **Urgency (Expiry)**: 0-1 point (tiered)
  - If offer.expiry < 7 days = +1 point (critical urgency)
  - If offer.expiry 7-14 days = +0.5 point (urgent)
  - If offer.expiry > 14 days = 0 points

- **Commission Value**: 0-1 point (tiered)
  - offer.commission 0-1 = 0 points (low value)
  - offer.commission 2-3 = +0.5 points (medium value)
  - offer.commission 4-5 = +1 point (high value)

### Advanced Scoring

- **Inventory Scarcity**: 0-0.3 points
  - Boost offers with low inventory to drive urgency
  - High inventory (>100) = 0 points
  - Low inventory (1-10) = +0.3 points
  - Linear interpolation between

- **Personalization Boost**: 0-1 point
  - Add AWS Personalize score if available for the user
  - Personalize scores (0-1) are added directly to final score
  - Only applies to offers in user's personalized recommendations
  - Loaded from `./data/personalize_recommendations.json`

- **Lunch Time Boost**: +3 points
  - If current time is between 12:00 PM and 2:00 PM
  - AND offer.lunch == true
  - Add +3 points to boost lunch offers without dominating other factors

- **Gift Card Penalty**: -0.5 points
  - If offer.offerType == "gift-card" = -0.5 points (lower purchase intent)

- **Coffee Time Penalty**: 0 to -1 points (linear)
  - Deprioritize coffee offers after 2:00 PM
  - Detection: Check if offer name contains "coffee", "café", "cafe", "espresso", "cappuccino", "latte" (case-insensitive)
  - If current time >= 14:00 (2:00 PM):
    - Penalty = -((current_hour - 14) / 10)
    - At 2:00 PM = 0 penalty
    - At 6:00 PM = -0.4 penalty
    - At 10:00 PM = -0.8 penalty
    - At midnight (24:00) = -1.0 penalty
  - Maintains personalization while reducing coffee relevance in evening

- **Coffee Morning Boost**: +2 points
  - Boost coffee offers between 7:00 AM and 9:00 AM
  - Detection: Same keywords as coffee penalty
  - Encourages morning coffee purchases

- **Diversity Constraint**: Applied during selection
  - Maximum 60% (12 out of 20) of any single offerType
  - Enforced while selecting top 20 offers
  - Ensures balanced mix: online, in-store, gift-card

**Maximum Possible Score**: ~8.3 points (with all factors)

### Scoring Flow

1. **Pre-filter**: Remove offers with zero inventory and expired offers
2. **Calculate base score**: Connection + Boost + Expiry + Commission (0-4 points)
3. **Add inventory scarcity**: Low stock bonus (0-0.3 points)
4. **Add personalization boost**: AWS Personalize score if available (0-1 point)
5. **Add lunch time boost**: +3 points if lunch time and offer.lunch == true
6. **Apply gift card penalty**: -0.5 if offerType == "gift-card"
7. **Apply coffee time adjustment**: +2 if 7-9AM, 0 to -1 if after 2PM (linear)
8. **Sort by final score**: Descending order
9. **Apply diversity constraint**: Select top 20 with max 12 per offerType

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
API allows connection_type and time override in request:
  POST /offers/recommend
  {
    "user_id": "USER001",
    "connection_type": "mobile",  // Override stored value
    "current_time": "13:30"        // Override current time (HH:MM format, 24h)
  }

This allows testing different scenarios
```

### Rule 11: Response Format

```
API returns:
  - Top 20 offers (sorted by final_score)
  - User's connection_type
  - offer object with:
    - base_score: Score from business rules (0-4.3)
    - personalize_score: AWS Personalize score if available (0-1)
    - final_score: base_score + personalize_score
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
