# Quick Start - Deploy to AWS

## 🚀 One-Command Deployment

```bash
./deploy.sh
```

## 📋 Step-by-Step

### 1. Deploy Infrastructure (5 minutes)

```bash
./deploy.sh
```

When prompted, type `yes` to deploy.

### 2. Seed Data (30 seconds)

```bash
python seed_database.py
```

### 3. Get Your API Endpoint

```bash
cd terraform
terraform output api_endpoint
```

Copy the URL (e.g., `https://abc123.execute-api.us-east-1.amazonaws.com/prod`)

### 4. Test the API

```bash
python test_api.py https://YOUR_API_ENDPOINT
```

## 🎯 API Endpoints

### Get Personalized Offers

```bash
curl -X POST https://YOUR_API_ENDPOINT/offers/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_id": "USER001"}'
```

### Track User Event

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

## 🏗️ What Gets Deployed

- ✅ DynamoDB Tables (Offers, UserActivity)
- ✅ Kinesis Stream (offer-engagement-stream)
- ✅ Lambda Functions (3 functions)
- ✅ API Gateway (HTTP API)
- ✅ IAM Roles & Permissions
- ✅ DynamoDB Streams Triggers

## 💰 Cost

~$13/month for 100K requests

## 🧹 Cleanup

```bash
cd terraform
terraform destroy
```

## 📚 Full Documentation

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

## 🎬 Demo Flow

1. **Get offers** for USER001 (electronics fan)
2. **Track click** on electronics offer
3. **Simulate stockout** by setting inventory to 0
4. **Watch auto-pivot** in CloudWatch Logs
5. **Get offers** again - see boosted pivot offer

## ⚡ Key Features

- **Real-time ranking** with Multi-Armed Bandit algorithm
- **Auto-pivot** on stockout (DynamoDB Streams)
- **Event tracking** via Kinesis
- **Diversity filter** (max 2 offers per category)
- **Sub-100ms latency**

## 🔧 Requirements

- AWS CLI configured
- Terraform 1.0+
- Python 3.11+
- Boto3 (`pip install boto3`)

## 📞 Support

Check CloudWatch Logs if issues occur:
```bash
aws logs tail /aws/lambda/offer-get-offers --follow
```
