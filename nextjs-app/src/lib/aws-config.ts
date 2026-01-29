import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";
import { S3Client } from "@aws-sdk/client-s3";

// Validate required environment variables
const requiredEnvVars = ['AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'];
const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  throw new Error(
    `Missing required environment variables: ${missingVars.join(', ')}. ` +
    'Please configure your .env.local file with AWS credentials.'
  );
}

// AWS Configuration
const awsConfig = {
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
};

// DynamoDB Client
const dynamoDBClient = new DynamoDBClient(awsConfig);
export const docClient = DynamoDBDocumentClient.from(dynamoDBClient);

// S3 Client
export const s3Client = new S3Client(awsConfig);

// Table and bucket names
export const DYNAMODB_TABLE_NAME = process.env.DYNAMODB_TABLE_NAME || "hackathon-items";
export const S3_BUCKET_NAME = process.env.S3_BUCKET_NAME || "hackathon-bucket";
