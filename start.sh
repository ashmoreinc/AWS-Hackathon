#!/bin/bash

# Quick Start Script for AWS Hackathon Project

echo "🚀 AWS Hackathon Project - Quick Start"
echo "======================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    exit 1
fi

echo "✅ npm version: $(npm --version)"
echo ""

# Navigate to nextjs-app directory
cd nextjs-app || exit 1

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  .env.local file not found!"
    echo "📝 Creating .env.local from example..."
    cp .env.local.example .env.local
    echo ""
    echo "⚠️  IMPORTANT: Edit nextjs-app/.env.local with your AWS credentials before running the app!"
    echo ""
    read -p "Press Enter to continue after editing .env.local, or Ctrl+C to exit..."
fi

echo "🎯 Starting development server..."
echo ""
echo "Access the application at: http://localhost:3000"
echo ""
npm run dev
