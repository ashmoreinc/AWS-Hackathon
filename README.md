# Real-Time Offer Management System

Simple location-based offer targeting system using AWS serverless architecture.

## Model

**Offers**: `high_street` or `online`  
**Users**: `wifi` (at home) or `mobile` (on the go)

**Logic**:
- WiFi connection → Show **online** offers first (+50 priority boost)
- Mobile connection → Show **high street** offers first (+50 priority boost)

## Architecture

- **DynamoDB**: Stores offers and user profiles
- **Kinesis**: Tracks user events (clicks, redemptions)
- **Lambda**: 3 functions (get offers, track events, inventory monitor)
- **API Gateway**: HTTP API endpoints

## Quick Start

### 1. Deploy

```bash
./deploy_with_profile.sh
```

### 2. Seed Data

```bash
export AWS_PROFILE=AdministratorAccess-851311377237
python3 seed_database.py
```

### 3. Test

```bash
# WiFi user (sees online offers first)
curl -X POST https://YOUR_API/offers/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER001"}'

# Mobile user (sees high street offers first)
curl -X POST https://YOUR_API/offers/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER002"}'
```

## API Endpoints

**POST /offers/recommend**
```json
{
  "user_id": "USER001",
  "connection_type": "wifi"  // optional override
}
```

**POST /events/track**
```json
{
  "user_id": "USER001",
  "offer_id": "OFF002",
  "offer_type": "online",
  "event_type": "CLICK"
}
```

## Sample Offers

**Online** (WiFi priority):
- Amazon Prime Deal (30% off)
- ASOS Online Sale (40% off)
- Deliveroo Discount (£5 off)

**High Street** (Mobile priority):
- Starbucks Coffee (20% off)
- Tesco In-Store (£10 off)
- Costa Coffee (15% off)

## Postman Collection

Import `Offer_Management_Simple.postman_collection.json` for ready-to-use API tests.

## Cost

~$10/month for 100K requests

## Cleanup

```bash
cd terraform
terraform destroy
```
