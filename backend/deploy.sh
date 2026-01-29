#!/bin/bash

set -e

echo "🚀 Deploying Offer Management System to AWS"
echo "============================================"

# Package Lambda functions with data files
echo "📦 Packaging Lambda functions..."
cd lambda

# Copy data files to lambda directory
cp ../../data/offers.json .
cp ../../data/users.json .

# Create deployment package
zip -q deployment.zip get_offers.py track_event.py offers.json users.json

# Clean up copied files
rm offers.json users.json

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
