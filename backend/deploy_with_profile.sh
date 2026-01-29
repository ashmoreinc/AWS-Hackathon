#!/bin/bash

set -e

export AWS_PROFILE=AdministratorAccess-851311377237

echo "🚀 Deploying Offer Management System"
echo "====================================="
echo ""
echo "📋 AWS Profile: $AWS_PROFILE"
echo ""

# Verify credentials
echo "🔐 Verifying AWS credentials..."
aws sts get-caller-identity || {
    echo "❌ Error: Invalid credentials"
    echo "Run first: aws sso login --profile AdministratorAccess-851311377237"
    exit 1
}

echo "✓ Valid credentials"
echo ""

# Package Lambda
echo "📦 Packaging Lambda functions..."
cd lambda
rm -f deployment.zip
zip -q deployment.zip get_offers.py track_event.py inventory_monitor.py
echo "✓ Lambda packaged ($(ls -lh deployment.zip | awk '{print $5}'))"
cd ..

# Terraform
echo ""
echo "🔧 Deploying with Terraform..."
cd terraform

terraform init

echo ""
echo "📋 Planning..."
terraform plan -out=tfplan

echo ""
read -p "Deploy to AWS? (yes/no): " confirm

if [ "$confirm" = "yes" ]; then
    echo ""
    echo "🚀 Deploying..."
    terraform apply tfplan
    
    echo ""
    echo "✅ Deployment complete!"
    echo ""
    echo "📡 API Endpoint:"
    terraform output -raw api_endpoint
    echo ""
    echo ""
    echo "📝 Next steps:"
    echo "1. Seed data: cd .. && python seed_database.py"
    echo "2. Test API: python test_api.py \$(cd terraform && terraform output -raw api_endpoint)"
    echo ""
else
    echo "❌ Deployment cancelled"
    rm -f tfplan
fi
