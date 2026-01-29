import { NextRequest, NextResponse } from "next/server";
import { PutCommand, GetCommand, ScanCommand, DeleteCommand } from "@aws-sdk/lib-dynamodb";
import { docClient, DYNAMODB_TABLE_NAME } from "@/lib/aws-config";

// GET - Retrieve items from DynamoDB
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get("id");

    if (id) {
      // Get specific item by ID
      const command = new GetCommand({
        TableName: DYNAMODB_TABLE_NAME,
        Key: { id },
      });
      const response = await docClient.send(command);
      
      if (!response.Item) {
        return NextResponse.json({ error: "Item not found" }, { status: 404 });
      }
      
      return NextResponse.json({ item: response.Item });
    } else {
      // Scan all items with pagination
      const command = new ScanCommand({
        TableName: DYNAMODB_TABLE_NAME,
        Limit: 100, // Limit results for performance
      });
      const response = await docClient.send(command);
      
      return NextResponse.json({ 
        items: response.Items || [],
        lastEvaluatedKey: response.LastEvaluatedKey 
      });
    }
  } catch (error) {
    console.error("DynamoDB GET Error:", error);
    return NextResponse.json(
      { error: "Failed to retrieve items from DynamoDB" },
      { status: 500 }
    );
  }
}

// POST - Create or update item in DynamoDB
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { id, ...data } = body;

    if (!id) {
      return NextResponse.json({ error: "ID is required" }, { status: 400 });
    }

    // Validate ID format
    if (typeof id !== 'string' || id.length > 255) {
      return NextResponse.json({ error: "Invalid ID format" }, { status: 400 });
    }

    const item = {
      id,
      ...data,
      createdAt: new Date().toISOString(),
    };

    const command = new PutCommand({
      TableName: DYNAMODB_TABLE_NAME,
      Item: item,
    });

    await docClient.send(command);

    return NextResponse.json({ success: true, item });
  } catch (error) {
    console.error("DynamoDB POST Error:", error);
    return NextResponse.json(
      { error: "Failed to create item in DynamoDB" },
      { status: 500 }
    );
  }
}

// DELETE - Remove item from DynamoDB
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get("id");

    if (!id) {
      return NextResponse.json({ error: "ID is required" }, { status: 400 });
    }

    const command = new DeleteCommand({
      TableName: DYNAMODB_TABLE_NAME,
      Key: { id },
    });

    await docClient.send(command);

    return NextResponse.json({ success: true, message: "Item deleted" });
  } catch (error) {
    console.error("DynamoDB DELETE Error:", error);
    return NextResponse.json(
      { error: "Failed to delete item from DynamoDB" },
      { status: 500 }
    );
  }
}
