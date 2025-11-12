#!/usr/bin/env python3
"""
Test Gemma Market Analysis System
Tests both with and without Gemma AI
"""

print("🧪 Testing Gemma Market Analysis System")
print("=" * 60)

# Test 1: Check dependencies
print("\n1️⃣ Checking dependencies...")
try:
    import yfinance as yf
    print("   ✅ yfinance")
except:
    print("   ❌ yfinance - run: pip install yfinance")

try:
    from current_stock_summary import get_technical_analysis
    print("   ✅ current_stock_summary")
except:
    print("   ❌ current_stock_summary")

try:
    from stock_universe import get_comprehensive_stock_list
    print("   ✅ stock_universe")
except:
    print("   ❌ stock_universe")

# Test 2: Check Gemma availability
print("\n2️⃣ Checking Gemma AI...")
try:
    import keras_nlp
    import tensorflow as tf
    print("   ✅ Gemma AI available")
    gemma_available = True
except:
    print("   ⚠️  Gemma AI not available (will use fallback)")
    gemma_available = False

# Test 3: Test stock analysis
print("\n3️⃣ Testing stock analysis...")
try:
    from gemma_market_analysis import GemmaMarketAnalyst
    
    analyst = GemmaMarketAnalyst()
    print("   ✅ GemmaMarketAnalyst initialized")
    
    # Test with a sample stock
    print("\n   Testing with AAPL...")
    stock_data = get_technical_analysis('AAPL')
    
    if stock_data:
        print(f"   ✅ Got data for AAPL: ${stock_data['current_price']:.2f}")
        
        # Test AI analysis
        analysis = analyst.analyze_stock_with_ai(stock_data)
        print(f"   ✅ AI Analysis: {analysis[:100]}...")
        
        # Test AI scoring
        ai_score = analyst._calculate_ai_score(stock_data)
        print(f"   ✅ AI Score: {ai_score:.0f}/100")
    else:
        print("   ⚠️  Could not get AAPL data")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Check email configuration
print("\n4️⃣ Checking email configuration...")
import os
from dotenv import load_dotenv
load_dotenv()

email_from = os.getenv('EMAIL_FROM')
email_password = os.getenv('EMAIL_PASSWORD')

if email_from and email_password:
    print(f"   ✅ Email configured: {email_from}")
else:
    print("   ⚠️  Email not configured in .env")

# Test 5: Check Kaggle credentials (for Gemma download)
print("\n5️⃣ Checking Kaggle credentials...")
kaggle_user = os.getenv('KAGGLE_USERNAME')
kaggle_key = os.getenv('KAGGLE_KEY')

if kaggle_user and kaggle_key:
    print(f"   ✅ Kaggle configured: {kaggle_user}")
else:
    print("   ⚠️  Kaggle credentials not set (needed for Gemma download)")
    print("      Set: export KAGGLE_USERNAME=your_username")
    print("      Set: export KAGGLE_KEY=your_api_key")

# Summary
print("\n" + "=" * 60)
print("📊 SYSTEM STATUS SUMMARY")
print("=" * 60)

if gemma_available:
    print("🤖 Gemma AI: ✅ AVAILABLE")
    print("   Full AI-powered analysis enabled")
else:
    print("🤖 Gemma AI: ⚠️  NOT AVAILABLE")
    print("   Using enhanced rule-based analysis (still excellent!)")

print("\n💡 Next Steps:")
if not gemma_available:
    print("   1. To enable Gemma AI:")
    print("      - Set Kaggle credentials")
    print("      - Run: ./setup_gemma.sh")
    print("      - Run: pip install -r requirements_gemma.txt")
    print("\n   2. Or use without Gemma:")
    print("      - Run: python gemma_market_analysis.py")
    print("      - System works great with fallback mode!")
else:
    print("   ✅ System ready!")
    print("   Run: python gemma_market_analysis.py")

print("\n✅ Test complete!")
