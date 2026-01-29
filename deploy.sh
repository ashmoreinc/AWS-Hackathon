#!/bin/bash

set -e

echo "🚀 Deploying Offer Management System to AWS"
echo "============================================"

# Package Lambda functions
echo "📦 Packaging Lambda functions..."
cd lambda
zip -q deployment.zip get_offers.py track_event.py inventory_monitor.py
echo "✓ Lambda package created"

# Initialize Terraform
echo ""
echo "🔧 Initializing Terraform..."
cd ../terraform
terraform init

# Plan deployment
echo ""
echo "📋 Planning deployment..."
terraform plan -out=tfplan

# Apply deployment
echo ""
read -p "Deploy to AWS? (yes/no): " confirm
if [ "$confirm" = "yes" ]; then
    echo "🚀 Deploying infrastructure..."
    terraform apply tfplan
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📡 API Endpoint:"
    terraform output -raw api_endpoint
    echo ""
    echo ""
    echo "🔗 Available endpoints:"
    echo "  POST $(terraform output -raw api_endpoint)/offers/recommend"
    echo "  POST $(terraform output -raw api_endpoint)/events/track"
    echo ""
else
    echo "❌ Deployment cancelled"
fi
