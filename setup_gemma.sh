#!/bin/bash

# Setup Gemma Model for Advanced Stock Analysis
# This script downloads and sets up Gemma 1.1 Instruct 2B model

echo "🤖 Setting up Gemma for Advanced Market Analysis"
echo "=================================================="

# Check if Kaggle credentials are set
if [ -z "$KAGGLE_USERNAME" ] || [ -z "$KAGGLE_KEY" ]; then
    echo "❌ Error: Kaggle credentials not set"
    echo ""
    echo "Please set your Kaggle credentials:"
    echo "  export KAGGLE_USERNAME=<YOUR USERNAME>"
    echo "  export KAGGLE_KEY=<YOUR KAGGLE KEY>"
    echo ""
    echo "Get your API key from: https://www.kaggle.com/settings/account"
    exit 1
fi

# Create models directory
mkdir -p models/gemma
cd models/gemma

echo "📥 Downloading Gemma 1.1 Instruct 2B model..."
echo "This may take a few minutes..."

# Download the model
curl -L -u $KAGGLE_USERNAME:$KAGGLE_KEY \
  -o gemma_model.tar.gz \
  https://www.kaggle.com/api/v1/models/keras/gemma/keras/gemma_1.1_instruct_2b_en/4/download

if [ $? -eq 0 ]; then
    echo "✅ Model downloaded successfully"
    
    echo "📦 Extracting model..."
    tar -xzf gemma_model.tar.gz
    
    if [ $? -eq 0 ]; then
        echo "✅ Model extracted successfully"
        rm gemma_model.tar.gz
        
        cd ../..
        
        echo ""
        echo "🎉 Gemma setup complete!"
        echo ""
        echo "Model location: models/gemma/"
        echo ""
        echo "Next steps:"
        echo "1. Install dependencies: pip install keras-nlp tensorflow"
        echo "2. Run: python gemma_market_analysis.py"
        echo ""
    else
        echo "❌ Error extracting model"
        exit 1
    fi
else
    echo "❌ Error downloading model"
    echo "Please check your Kaggle credentials"
    exit 1
fi
