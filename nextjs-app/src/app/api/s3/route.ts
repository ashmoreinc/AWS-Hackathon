import { NextRequest, NextResponse } from "next/server";
import { PutObjectCommand, GetObjectCommand, ListObjectsV2Command, DeleteObjectCommand } from "@aws-sdk/client-s3";
import { s3Client, S3_BUCKET_NAME } from "@/lib/aws-config";
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";

// Maximum file size: 5MB
const MAX_FILE_SIZE = 5 * 1024 * 1024;

// Validate S3 key format
function isValidS3Key(key: string): boolean {
  // Key should not contain path traversal patterns
  if (key.includes('..') || key.startsWith('/')) {
    return false;
  }
  // Key should only contain alphanumeric, hyphen, underscore, forward slash, and dot
  const validKeyPattern = /^[a-zA-Z0-9\-_/.]+$/;
  return validKeyPattern.test(key) && key.length <= 1024;
}

// GET - List objects or get presigned URL for an object
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const key = searchParams.get("key");

    if (key) {
      // Validate key
      if (!isValidS3Key(key)) {
        return NextResponse.json({ error: "Invalid object key" }, { status: 400 });
      }

      // Get presigned URL for specific object
      const command = new GetObjectCommand({
        Bucket: S3_BUCKET_NAME,
        Key: key,
      });
      
      const url = await getSignedUrl(s3Client, command, { expiresIn: 3600 });
      
      return NextResponse.json({ url });
    } else {
      // List all objects in bucket with pagination
      const command = new ListObjectsV2Command({
        Bucket: S3_BUCKET_NAME,
        MaxKeys: 100, // Limit results for performance
      });
      
      const response = await s3Client.send(command);
      
      return NextResponse.json({ 
        objects: response.Contents?.map(obj => ({
          key: obj.Key,
          size: obj.Size,
          lastModified: obj.LastModified,
        })) || [],
        isTruncated: response.IsTruncated || false,
        nextContinuationToken: response.NextContinuationToken
      });
    }
  } catch (error) {
    console.error("S3 GET Error:", error);
    return NextResponse.json(
      { error: "Failed to retrieve S3 objects" },
      { status: 500 }
    );
  }
}

// POST - Upload object to S3 (base64 encoded)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { key, content, contentType } = body;

    if (!key || !content) {
      return NextResponse.json(
        { error: "Key and content are required" },
        { status: 400 }
      );
    }

    // Validate key format
    if (!isValidS3Key(key)) {
      return NextResponse.json({ error: "Invalid object key format" }, { status: 400 });
    }

    // Decode base64 content and check size
    let buffer: Buffer;
    try {
      buffer = Buffer.from(content, 'base64');
    } catch {
      return NextResponse.json({ error: "Invalid base64 content" }, { status: 400 });
    }

    // Check file size
    if (buffer.length > MAX_FILE_SIZE) {
      return NextResponse.json(
        { error: `File size exceeds maximum of ${MAX_FILE_SIZE / 1024 / 1024}MB` },
        { status: 413 }
      );
    }

    const command = new PutObjectCommand({
      Bucket: S3_BUCKET_NAME,
      Key: key,
      Body: buffer,
      ContentType: contentType || "application/octet-stream",
    });

    await s3Client.send(command);

    return NextResponse.json({ 
      success: true, 
      message: "File uploaded successfully",
      key 
    });
  } catch (error) {
    console.error("S3 POST Error:", error);
    return NextResponse.json(
      { error: "Failed to upload to S3" },
      { status: 500 }
    );
  }
}

// DELETE - Remove object from S3
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const key = searchParams.get("key");

    if (!key) {
      return NextResponse.json({ error: "Key is required" }, { status: 400 });
    }

    // Validate key format
    if (!isValidS3Key(key)) {
      return NextResponse.json({ error: "Invalid object key" }, { status: 400 });
    }

    const command = new DeleteObjectCommand({
      Bucket: S3_BUCKET_NAME,
      Key: key,
    });

    await s3Client.send(command);

    return NextResponse.json({ 
      success: true, 
      message: "File deleted successfully" 
    });
  } catch (error) {
    console.error("S3 DELETE Error:", error);
    return NextResponse.json(
      { error: "Failed to delete from S3" },
      { status: 500 }
    );
  }
}
