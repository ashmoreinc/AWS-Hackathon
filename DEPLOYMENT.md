# Deployment Guide

This guide walks you through deploying the AWS Hackathon project to AWS.

## Prerequisites

1. **AWS Account**: Create an account at [aws.amazon.com](https://aws.amazon.com)
2. **AWS CLI**: Install and configure
   ```bash
   aws configure
   ```
3. **Terraform**: Install from [terraform.io](https://terraform.io)
4. **Node.js**: Version 18 or higher

## Step-by-Step Deployment

### 1. Clone and Setup

```bash
git clone <repository-url>
cd AWS-Hackathon
```

### 2. Deploy AWS Infrastructure

```bash
cd terraform

# Initialize Terraform
terraform init

# Review the infrastructure plan
terraform plan

# Deploy (this will create AWS resources)
terraform apply
# Type 'yes' when prompted
```

**What gets created:**
- S3 buckets for app data and static website hosting
- DynamoDB table for data storage
- IAM user with appropriate permissions
- CloudFront distribution for CDN
- All necessary policies and configurations

### 3. Retrieve AWS Credentials

After Terraform completes, get your credentials:

```bash
# Get the access key ID
terraform output iam_access_key_id

# Get the secret access key (sensitive)
terraform output -raw iam_secret_access_key

# Get resource names
terraform output dynamodb_table_name
terraform output s3_bucket_name
```

**Important**: Save these values securely!

### 4. Configure Next.js Application

```bash
cd ../nextjs-app

# Copy the environment template
cp .env.local.example .env.local

# Edit .env.local with your values from Terraform output
nano .env.local
```

Your `.env.local` should look like:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
DYNAMODB_TABLE_NAME=hackathon-dev-items
S3_BUCKET_NAME=hackathon-dev-app-bucket
```

### 5. Install Dependencies and Test Locally

```bash
npm install

# Run development server
npm run dev
```

Visit http://localhost:3000 to test the application.

### 6. Deploy to Vercel (Recommended)

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Setup complete"
   git push
   ```

2. Visit [vercel.com](https://vercel.com) and import your repository

3. Add environment variables in Vercel dashboard:
   - `AWS_REGION`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `DYNAMODB_TABLE_NAME`
   - `S3_BUCKET_NAME`

4. Deploy!

### Alternative: Deploy Static Site to S3

If you prefer to host on AWS:

```bash
# Build the Next.js app
npm run build

# Export static files (if using static export)
npm run export  # Add this script to package.json if needed

# Upload to S3
aws s3 sync out/ s3://your-static-bucket-name/

# Get CloudFront URL
cd ../terraform
terraform output cloudfront_domain_name
```

## Testing the Deployment

### Test DynamoDB API

```bash
# Create an item
curl -X POST https://your-app-url/api/dynamodb \
  -H "Content-Type: application/json" \
  -d '{"id": "test1", "data": "Hello AWS!"}'

# Get all items
curl https://your-app-url/api/dynamodb

# Get specific item
curl https://your-app-url/api/dynamodb?id=test1

# Delete item
curl -X DELETE https://your-app-url/api/dynamodb?id=test1
```

### Test S3 API

```bash
# Upload a file
curl -X POST https://your-app-url/api/s3 \
  -H "Content-Type: application/json" \
  -d '{"key": "test.txt", "content": "SGVsbG8gUzMh", "contentType": "text/plain"}'

# List objects
curl https://your-app-url/api/s3

# Get presigned URL
curl https://your-app-url/api/s3?key=test.txt

# Delete object
curl -X DELETE https://your-app-url/api/s3?key=test.txt
```

## Monitoring

### Check CloudWatch Logs

```bash
# View recent logs
aws logs tail /aws/lambda/your-function-name --follow
```

### Check DynamoDB Metrics

```bash
# Get table description
aws dynamodb describe-table --table-name hackathon-dev-items
```

### Check S3 Bucket

```bash
# List objects
aws s3 ls s3://hackathon-dev-app-bucket/
```

## Updating Infrastructure

To update your infrastructure:

```bash
cd terraform

# Review changes
terraform plan

# Apply changes
terraform apply
```

## Cost Estimation

Approximate monthly costs (varies by usage):
- **S3**: $0.023 per GB + requests
- **DynamoDB**: Pay per request (~$1.25 per million writes)
- **CloudFront**: $0.085 per GB + requests
- **IAM**: Free

**Estimated total for low traffic**: $5-20/month

## Cleanup

To remove all AWS resources:

```bash
cd terraform
terraform destroy
# Type 'yes' when prompted
```

**Warning**: This will delete all data!

## Troubleshooting

### Issue: Terraform Apply Fails

**Solution**: Check AWS credentials and permissions
```bash
aws sts get-caller-identity
```

### Issue: Bucket Name Already Exists

**Solution**: Bucket names must be globally unique. Edit `terraform/variables.tf` and change `project_name`.

### Issue: API Returns 500 Error

**Solution**: Check CloudWatch logs and verify:
- AWS credentials in environment variables
- Resource names match Terraform outputs
- IAM permissions are correct

### Issue: CORS Errors

**Solution**: Add CORS configuration to S3 bucket or API Gateway if needed.

## Security Best Practices

1. **Never commit credentials**: Use `.env.local` (already in `.gitignore`)
2. **Rotate keys regularly**: Create new IAM access keys periodically
3. **Use IAM roles in production**: Better than access keys
4. **Enable MFA**: On your AWS account
5. **Monitor usage**: Set up CloudWatch alarms
6. **Use Secrets Manager**: For production credentials

## Next Steps

- [ ] Set up custom domain with Route 53
- [ ] Add SSL certificate with ACM
- [ ] Configure CI/CD pipeline
- [ ] Set up monitoring and alerts
- [ ] Implement authentication (Cognito)
- [ ] Add backup strategy
- [ ] Set up staging environment

## Support

For issues or questions:
1. Check the main README.md
2. Review AWS documentation
3. Check CloudWatch logs
4. Open an issue on GitHub
