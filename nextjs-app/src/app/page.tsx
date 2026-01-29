"use client";

import { useState } from "react";

interface ApiResponse {
  [key: string]: unknown;
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<"dynamodb" | "s3">("dynamodb");
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // DynamoDB state
  const [itemId, setItemId] = useState("");
  const [itemData, setItemData] = useState("");

  // S3 state
  const [s3Key, setS3Key] = useState("");
  const [s3Content, setS3Content] = useState("");

  const handleDynamoDBGet = async () => {
    setLoading(true);
    try {
      const url = itemId ? `/api/dynamodb?id=${itemId}` : "/api/dynamodb";
      const res = await fetch(url);
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({ error: String(error) });
    }
    setLoading(false);
  };

  const handleDynamoDBPost = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/dynamodb", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: itemId, data: itemData }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({ error: String(error) });
    }
    setLoading(false);
  };

  const handleDynamoDBDelete = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/dynamodb?id=${itemId}`, {
        method: "DELETE",
      });
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({ error: String(error) });
    }
    setLoading(false);
  };

  const handleS3Get = async () => {
    setLoading(true);
    try {
      const url = s3Key ? `/api/s3?key=${s3Key}` : "/api/s3";
      const res = await fetch(url);
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({ error: String(error) });
    }
    setLoading(false);
  };

  const handleS3Post = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/s3", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          key: s3Key, 
          content: btoa(s3Content),
          contentType: "text/plain"
        }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({ error: String(error) });
    }
    setLoading(false);
  };

  const handleS3Delete = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/s3?key=${s3Key}`, {
        method: "DELETE",
      });
      const data = await res.json();
      setResponse(data);
    } catch (error) {
      setResponse({ error: String(error) });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 py-8 px-4">
      <main className="max-w-6xl mx-auto">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 mb-8">
          <h1 className="text-4xl font-bold text-gray-800 dark:text-white mb-2">
            AWS Hackathon Project
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Next.js application with AWS DynamoDB and S3 integration
          </p>

          {/* Tab Navigation */}
          <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab("dynamodb")}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === "dynamodb"
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              }`}
            >
              DynamoDB
            </button>
            <button
              onClick={() => setActiveTab("s3")}
              className={`px-6 py-3 font-medium transition-colors ${
                activeTab === "s3"
                  ? "text-blue-600 border-b-2 border-blue-600"
                  : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
              }`}
            >
              S3
            </button>
          </div>

          {/* DynamoDB Tab */}
          {activeTab === "dynamodb" && (
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">
                DynamoDB Operations
              </h2>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Item ID
                </label>
                <input
                  type="text"
                  value={itemId}
                  onChange={(e) => setItemId(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Enter item ID"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Item Data (for POST)
                </label>
                <textarea
                  value={itemData}
                  onChange={(e) => setItemData(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Enter any data"
                  rows={3}
                />
              </div>
              <div className="flex gap-4 flex-wrap">
                <button
                  onClick={handleDynamoDBGet}
                  disabled={loading}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
                >
                  GET Items
                </button>
                <button
                  onClick={handleDynamoDBPost}
                  disabled={loading || !itemId}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors font-medium"
                >
                  POST Item
                </button>
                <button
                  onClick={handleDynamoDBDelete}
                  disabled={loading || !itemId}
                  className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 transition-colors font-medium"
                >
                  DELETE Item
                </button>
              </div>
            </div>
          )}

          {/* S3 Tab */}
          {activeTab === "s3" && (
            <div className="space-y-4">
              <h2 className="text-2xl font-semibold text-gray-800 dark:text-white mb-4">
                S3 Operations
              </h2>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Object Key
                </label>
                <input
                  type="text"
                  value={s3Key}
                  onChange={(e) => setS3Key(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="e.g., folder/file.txt"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Content (for POST)
                </label>
                <textarea
                  value={s3Content}
                  onChange={(e) => setS3Content(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  placeholder="Enter text content"
                  rows={3}
                />
              </div>
              <div className="flex gap-4 flex-wrap">
                <button
                  onClick={handleS3Get}
                  disabled={loading}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium"
                >
                  GET Objects
                </button>
                <button
                  onClick={handleS3Post}
                  disabled={loading || !s3Key || !s3Content}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors font-medium"
                >
                  POST Object
                </button>
                <button
                  onClick={handleS3Delete}
                  disabled={loading || !s3Key}
                  className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 transition-colors font-medium"
                >
                  DELETE Object
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Response Display */}
        {response && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">
              Response
            </h3>
            <pre className="bg-gray-100 dark:bg-gray-900 p-4 rounded-lg overflow-x-auto text-sm">
              {JSON.stringify(response, null, 2)}
            </pre>
          </div>
        )}
      </main>
    </div>
  );
}
