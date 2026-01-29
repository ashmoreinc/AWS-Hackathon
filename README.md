# AWS Hackathon - Next.js with AWS Integration

A modern Next.js application with TypeScript, Tailwind CSS, and AWS integration (DynamoDB and S3), including complete Terraform infrastructure configuration for AWS deployment.

## 🚀 Features

- **Next.js 16** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **AWS SDK v3** integration
- **DynamoDB** for NoSQL database operations
- **S3** for object storage
- **Terraform** infrastructure as code
- **CloudFront** CDN distribution
- Interactive UI for testing AWS operations

## 📁 Project Structure

```
.
├── nextjs-app/              # Next.js application
│   ├── src/
│   │   ├── app/            # App router pages and API routes
│   │   │   ├── api/        # API endpoints
│   │   │   │   ├── dynamodb/  # DynamoDB operations
│   │   │   │   └── s3/        # S3 operations
│   │   │   ├── page.tsx    # Main page with UI
│   │   │   └── layout.tsx  # Root layout
│   │   └── lib/            # Utility libraries
│   │       └── aws-config.ts  # AWS SDK configuration
│   ├── package.json
│   └── .env.local.example  # Environment variables template
│
└── terraform/              # Infrastructure as Code
    ├── main.tf            # Provider configuration
    ├── variables.tf       # Input variables
    ├── outputs.tf         # Output values
    ├── s3.tf             # S3 bucket resources
    ├── dynamodb.tf       # DynamoDB table
    ├── iam.tf            # IAM users and policies
    ├── cloudfront.tf     # CloudFront distribution
    └── secrets.tf        # Sensitive outputs
```

## 🛠️ Setup

### Prerequisites

- Node.js 18+ and npm
- AWS Account
- AWS CLI configured
- Terraform 1.0+

### 1. Install Dependencies

```bash
cd nextjs-app
npm install
```

### 2. Configure Environment Variables

Create a `.env.local` file in the `nextjs-app` directory:

```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your AWS credentials:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
DYNAMODB_TABLE_NAME=hackathon-dev-items
S3_BUCKET_NAME=hackathon-dev-app-bucket
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to see the application.

## ☁️ AWS Infrastructure Deployment

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Review and Customize Variables

Edit `terraform.tfvars` or use command-line variables:

```bash
terraform plan -var="project_name=hackathon" -var="environment=dev" -var="aws_region=us-east-1"
```

### 3. Deploy Infrastructure

```bash
terraform apply
```

Review the plan and type `yes` to confirm.

### 4. Get AWS Credentials

After deployment, retrieve the IAM credentials:

```bash
terraform output iam_access_key_id
terraform output iam_secret_access_key
```

Update your `.env.local` file with these credentials.

### 5. Get Resource Names

```bash
terraform output dynamodb_table_name
terraform output s3_bucket_name
```

Update your `.env.local` file with the resource names.

## 📡 API Routes

### DynamoDB API (`/api/dynamodb`)

#### GET - Retrieve Items
- **Get all items**: `GET /api/dynamodb`
- **Get specific item**: `GET /api/dynamodb?id={item_id}`

#### POST - Create/Update Item
```bash
POST /api/dynamodb
Content-Type: application/json

{
  "id": "item1",
  "data": "your data here"
}
```

#### DELETE - Remove Item
```bash
DELETE /api/dynamodb?id={item_id}
```

### S3 API (`/api/s3`)

#### GET - List Objects or Get Presigned URL
- **List all objects**: `GET /api/s3`
- **Get presigned URL**: `GET /api/s3?key={object_key}`

#### POST - Upload Object
```bash
POST /api/s3
Content-Type: application/json

{
  "key": "folder/file.txt",
  "content": "base64_encoded_content",
  "contentType": "text/plain"
}
```

#### DELETE - Remove Object
```bash
DELETE /api/s3?key={object_key}
```

## 🎨 Frontend Features

The main page provides an interactive UI with:

- **Tab Navigation**: Switch between DynamoDB and S3 operations
- **DynamoDB Tab**: Create, read, and delete items
- **S3 Tab**: Upload, list, and delete objects
- **Real-time Response Display**: View API responses in JSON format
- **Modern UI**: Responsive design with Tailwind CSS

## 🏗️ Infrastructure Components

### AWS Resources Created by Terraform:

1. **S3 Buckets**:
   - Application data bucket (private)
   - Static website hosting bucket (public)
   - Versioning enabled

2. **DynamoDB Table**:
   - Pay-per-request billing
   - Point-in-time recovery enabled
   - Primary key: `id` (String)

3. **IAM**:
   - Application user with programmatic access
   - Policy for S3 and DynamoDB operations
   - Access keys for authentication

4. **CloudFront**:
   - CDN distribution for static website
   - HTTPS redirect enabled
   - Custom error pages for SPA routing

## 🔒 Security Considerations

- Never commit `.env.local` or AWS credentials to version control
- Use IAM roles instead of access keys in production
- Enable MFA for AWS accounts
- Regularly rotate access keys
- Use least privilege principle for IAM policies
- Consider using AWS Secrets Manager for sensitive data

## 🚀 Deployment Options

### Option 1: Vercel (Recommended for Next.js)

1. Push your code to GitHub
2. Import project in Vercel
3. Add environment variables in Vercel dashboard
4. Deploy automatically

### Option 2: AWS Amplify

1. Build the Next.js app: `npm run build`
2. Deploy to Amplify Console
3. Configure environment variables

### Option 3: Static Export to S3

1. Export Next.js as static site (if no dynamic features needed)
2. Upload to S3 static website bucket
3. Access via CloudFront URL

## 📊 Monitoring and Logging

- CloudWatch Logs for Lambda functions
- S3 access logs
- DynamoDB metrics in CloudWatch
- CloudFront access logs

## 🧹 Cleanup

To destroy all AWS resources:

```bash
cd terraform
terraform destroy
```

## 📝 Development

### Build for Production

```bash
cd nextjs-app
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Issue: AWS Credentials Not Working
- Verify credentials in `.env.local`
- Check IAM user has correct policies attached
- Ensure AWS region is correct

### Issue: DynamoDB/S3 Operations Fail
- Verify resource names match between Terraform outputs and `.env.local`
- Check AWS resource exists in correct region
- Verify IAM permissions

### Issue: Build Errors
- Clear Next.js cache: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check Node.js version (18+ required)

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [AWS SDK for JavaScript v3](https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)