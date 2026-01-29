/**
 * Lambda API Handler
 * Handles API Gateway requests and routes them appropriately
 */

import { APIGatewayProxyEventV2, APIGatewayProxyResultV2 } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import {
  DynamoDBDocumentClient,
  GetCommand,
  PutCommand,
  DeleteCommand,
  ScanCommand,
} from '@aws-sdk/lib-dynamodb';
import { S3Client } from '@aws-sdk/client-s3';

// Initialize AWS clients
const dynamoClient = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(dynamoClient);
const s3Client = new S3Client({});

const TABLE_NAME = process.env.DYNAMODB_TABLE!;
const BUCKET_NAME = process.env.S3_BUCKET!;

// Types
interface Item {
  id: string;
  [key: string]: unknown;
  createdAt?: string;
  updatedAt?: string;
}

interface ItemsResponse {
  items: Item[];
  count: number;
}

interface MessageResponse {
  message: string;
}

interface ErrorResponse {
  error: string;
  message?: string;
}

interface WelcomeResponse {
  message: string;
  environment: string | undefined;
  availableEndpoints: string[];
}

interface HealthResponse {
  status: string;
  timestamp: string;
}

type ResponseBody = Item | ItemsResponse | MessageResponse | ErrorResponse | WelcomeResponse | HealthResponse;

/**
 * Main Lambda handler
 */
export const handler = async (event: APIGatewayProxyEventV2): Promise<APIGatewayProxyResultV2> => {
  console.log('Received event:', JSON.stringify(event, null, 2));

  const method = event.requestContext?.http?.method;
  const path = event.rawPath || event.requestContext?.http?.path;
  const pathParameters = event.pathParameters;
  const queryStringParameters = event.queryStringParameters;
  const body = event.body;

  try {
    // Health check endpoint
    if (path === '/health' || path === '/api/health') {
      return response(200, { status: 'healthy', timestamp: new Date().toISOString() });
    }

    // Route handling
    if (path.startsWith('/api/items') || path.startsWith('/items')) {
      return await handleItems(method, pathParameters, queryStringParameters, body);
    }

    // Default response
    return response(200, {
      message: 'Welcome to the API',
      environment: process.env.ENVIRONMENT,
      availableEndpoints: [
        'GET /health - Health check',
        'GET /api/items - List all items',
        'GET /api/items/{id} - Get item by ID',
        'POST /api/items - Create new item',
        'PUT /api/items/{id} - Update item',
        'DELETE /api/items/{id} - Delete item',
      ],
    });
  } catch (error) {
    console.error('Error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return response(500, { error: 'Internal server error', message: errorMessage });
  }
};

/**
 * Handle /items endpoints
 */
async function handleItems(
  method: string | undefined,
  pathParameters: Record<string, string | undefined> | undefined,
  queryParams: Record<string, string | undefined> | undefined,
  body: string | undefined
): Promise<APIGatewayProxyResultV2> {
  const id = pathParameters?.id || pathParameters?.proxy?.split('/')[1];

  switch (method) {
    case 'GET':
      if (id) {
        return await getItem(id);
      }
      return await listItems(queryParams);

    case 'POST':
      return await createItem(JSON.parse(body || '{}'));

    case 'PUT':
      if (!id) return response(400, { error: 'Item ID is required' });
      return await updateItem(id, JSON.parse(body || '{}'));

    case 'DELETE':
      if (!id) return response(400, { error: 'Item ID is required' });
      return await deleteItem(id);

    default:
      return response(405, { error: 'Method not allowed' });
  }
}

/**
 * Get a single item by ID
 */
async function getItem(id: string): Promise<APIGatewayProxyResultV2> {
  const command = new GetCommand({
    TableName: TABLE_NAME,
    Key: { id },
  });

  const result = await docClient.send(command);

  if (!result.Item) {
    return response(404, { error: 'Item not found' });
  }

  return response(200, result.Item as Item);
}

/**
 * List all items
 */
async function listItems(
  queryParams: Record<string, string | undefined> | undefined
): Promise<APIGatewayProxyResultV2> {
  const command = new ScanCommand({
    TableName: TABLE_NAME,
    Limit: parseInt(queryParams?.limit || '50'),
  });

  const result = await docClient.send(command);
  return response(200, { items: (result.Items || []) as Item[], count: result.Count || 0 });
}

/**
 * Create a new item
 */
async function createItem(data: Partial<Item>): Promise<APIGatewayProxyResultV2> {
  const item: Item = {
    id: data.id || generateId(),
    ...data,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  const command = new PutCommand({
    TableName: TABLE_NAME,
    Item: item,
  });

  await docClient.send(command);
  return response(201, item);
}

/**
 * Update an existing item
 */
async function updateItem(id: string, data: Partial<Item>): Promise<APIGatewayProxyResultV2> {
  const item: Item = {
    ...data,
    id,
    updatedAt: new Date().toISOString(),
  };

  const command = new PutCommand({
    TableName: TABLE_NAME,
    Item: item,
  });

  await docClient.send(command);
  return response(200, item);
}

/**
 * Delete an item
 */
async function deleteItem(id: string): Promise<APIGatewayProxyResultV2> {
  const command = new DeleteCommand({
    TableName: TABLE_NAME,
    Key: { id },
  });

  await docClient.send(command);
  return response(200, { message: 'Item deleted successfully' });
}

/**
 * Generate a simple unique ID
 */
function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
}

/**
 * Create a standardized API response
 */
function response(statusCode: number, body: ResponseBody): APIGatewayProxyResultV2 {
  return {
    statusCode,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key',
      'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    },
    body: JSON.stringify(body),
  };
}
