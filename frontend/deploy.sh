#!/bin/bash

echo "🚀 Deploying ASDP Frontend..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Make sure you're in the frontend directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Build the application
echo "🔨 Building application..."
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Build completed"
else
    echo "❌ Build failed"
    exit 1
fi

# Check if build output exists
if [ ! -d "dist" ]; then
    echo "❌ Build output directory 'dist' not found"
    exit 1
fi

echo "✅ Frontend deployment preparation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Commit and push your changes to GitHub"
echo "2. Vercel will automatically redeploy"
echo "3. Check the deployment at: https://asdp-frontend.vercel.app/"
echo ""
echo "🔧 Manual deployment commands:"
echo "   git add ."
echo "   git commit -m 'Fix frontend deployment issues'"
echo "   git push origin main"
echo ""
echo "🌐 Vercel deployment will be automatic if connected to GitHub"
