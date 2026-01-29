#!/bin/bash

# Deploy Next.js static site to CloudFront/S3
# This script builds the Next.js app and deploys it to AWS

set -e

echo "🚀 Deploying Next.js App to CloudFront"
echo "======================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    echo "   Visit: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI found${NC}"

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured or invalid.${NC}"
    echo "   Run 'aws configure' to set up your credentials."
    exit 1
fi

echo -e "${GREEN}✅ AWS credentials valid${NC}"
echo ""

# Get Terraform outputs
echo "📦 Getting deployment configuration from Terraform..."
cd "$(dirname "$0")/terraform"

S3_BUCKET=$(terraform output -raw static_website_bucket_name 2>/dev/null)
CLOUDFRONT_ID=$(terraform output -raw cloudfront_distribution_id 2>/dev/null)
CLOUDFRONT_DOMAIN=$(terraform output -raw cloudfront_domain_name 2>/dev/null)

if [ -z "$S3_BUCKET" ] || [ -z "$CLOUDFRONT_ID" ]; then
    echo -e "${RED}❌ Could not get Terraform outputs. Make sure you've run 'terraform apply' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ S3 Bucket: ${S3_BUCKET}${NC}"
echo -e "${GREEN}✅ CloudFront Distribution: ${CLOUDFRONT_ID}${NC}"
echo ""

# Build Next.js app
echo "🔨 Building Next.js application..."
cd "../nextjs-app"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build the static export
npm run build

if [ ! -d "out" ]; then
    echo -e "${RED}❌ Build failed - 'out' directory not found.${NC}"
    echo "   Make sure next.config.ts has 'output: \"export\"' configured."
    exit 1
fi

echo -e "${GREEN}✅ Build complete${NC}"
echo ""

# Sync to S3
echo "📤 Uploading to S3..."
aws s3 sync out/ "s3://${S3_BUCKET}/" \
    --delete \
    --cache-control "public, max-age=31536000, immutable" \
    --exclude "*.html" \
    --exclude "*.json"

# Upload HTML and JSON files with shorter cache
aws s3 sync out/ "s3://${S3_BUCKET}/" \
    --delete \
    --cache-control "public, max-age=0, must-revalidate" \
    --include "*.html" \
    --include "*.json" \
    --content-type "text/html" \
    --exclude "*" \
    --include "*.html"

aws s3 sync out/ "s3://${S3_BUCKET}/" \
    --cache-control "public, max-age=0, must-revalidate" \
    --include "*.json" \
    --exclude "*" \
    --include "*.json"

echo -e "${GREEN}✅ Upload complete${NC}"
echo ""

# Invalidate CloudFront cache
echo "🔄 Invalidating CloudFront cache..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id "$CLOUDFRONT_ID" \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

echo -e "${GREEN}✅ Cache invalidation started: ${INVALIDATION_ID}${NC}"
echo ""

# Done
echo "======================================="
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo "Your site is available at:"
echo -e "${YELLOW}   https://${CLOUDFRONT_DOMAIN}${NC}"
echo ""
echo "Note: It may take a few minutes for CloudFront to propagate the changes globally."
