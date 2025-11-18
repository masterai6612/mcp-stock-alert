# 💰 Dividend Stocks Feature Guide

## Overview

The Dividend Stocks feature scans **600+ US & Canadian stocks** from your comprehensive stock universe to find the best dividend-paying opportunities that also meet growth requirements.

## Quick Start

### Run Analysis

```bash
# Activate virtual environment
source venv_new/bin/activate

# Run comprehensive dividend analysis (takes 5-10 minutes)
python dividend_stock_analyzer.py
```

### View Results

1. **Streamlit Dashboard**: Navigate to "💰 Top 50 Dividends" page
2. **JSON File**: `top_50_dividend_stocks.json`

## Features

### 🔍 Comprehensive Scanning

- **533 validated stocks** from stock universe
- **US stocks**: ~280 stocks (mega caps, large caps, growth, value)
- **Canadian stocks**: ~250 stocks (TSX listings)
- **Parallel processing**: 15 workers for fast analysis
- **Analysis time**: 5-10 minutes

### 📊 Scoring System

**Dividend Score (0-100 points):**

- **50 points** - Technical analysis score (RSI, volume, price position)
- **30 points** - Dividend yield (up to 10% yield)
- **20 points** - Growth potential (1-month price change)

### 🏷️ Stock Categories

Stocks are automatically categorized based on their characteristics:

1. **Growth + High Dividend**: 10%+ growth, 4%+ yield (best of both worlds)
2. **Dividend + Growth**: 7%+ growth, 4%+ yield (balanced)
3. **Growth**: 10%+ growth (high growth focus)
4. **High Dividend**: 4%+ yield (income focus)
5. **Growth + Dividend**: 7%+ growth, 2%+ yield (moderate both)
6. **Dividend**: 2%+ yield (basic dividend)

### 🎯 Filtering Criteria

**Minimum Requirements:**
- Dividend yield ≥ 2.0%
- Active trading (3-month history)
- Valid market data

**Technical Analysis:**
- RSI (Relative Strength Index)
- Price position (52-week range)
- Volume trends
- Price momentum (1-week, 1-month)

## Streamlit Dashboard

### Navigation

1. Open Streamlit app
2. Click "💰 Top 50 Dividends" in sidebar
3. View comprehensive dividend stock analysis

### Display Modes

**📋 Compact List:**
- Quick overview of all stocks
- Symbol, category, yield, growth, score
- Easy scanning of top picks

**📊 Detailed Cards:**
- Full company information
- Dividend income projections (100/1000 shares)
- Technical indicators and performance
- Category badges and growth status

### Filters

- **Category**: Filter by stock category
- **Sector**: Filter by industry sector
- **Min Yield**: Adjust minimum dividend yield (2-10%)

### Portfolio Summary

- Average dividend yield
- Average 1-month growth
- Number of stocks meeting 7%+ growth
- Average dividend score
- Category breakdown

## Output Files

### top_50_dividend_stocks.json

```json
{
  "generated_at": "2025-11-18T10:30:00",
  "total_scanned": 533,
  "total_dividend_stocks": 120,
  "top_50_count": 50,
  "criteria": {
    "min_dividend_yield": 2.0,
    "scoring": {
      "technical": "50%",
      "dividend_yield": "30%",
      "growth": "20%"
    }
  },
  "all_dividend_stocks": [...],
  "top_50_dividend_stocks": [...]
}
```

### Stock Data Structure

```json
{
  "symbol": "JNJ",
  "company_name": "Johnson & Johnson",
  "sector": "Healthcare",
  "market_cap": 400000000000,
  "current_price": 165.50,
  "dividend_yield": 3.2,
  "change_1w": 2.5,
  "change_1m": 8.3,
  "rsi": 62.5,
  "price_position": 85.0,
  "volume_trend": 15.2,
  "technical_score": 7.5,
  "dividend_score": 72.5,
  "category": "Dividend + Growth",
  "meets_growth_requirement": true,
  "is_dividend_stock": true
}
```

## Integration with Auto-Update

The dividend analysis is integrated into the daily auto-update system:

```bash
# Manual update
python update_streamlit_data.py
```

**Update sequence:**
1. Gemma AI analysis (10 min)
2. **Dividend analysis (15 min)** ← NEW
3. Recommendations update
4. Summary creation

**GitHub Actions:**
- Runs daily at scheduled time
- Includes dividend analysis
- Updates Streamlit Cloud automatically

## Example Dividend Stocks

### High-Quality Dividend Aristocrats
- **JNJ** - Johnson & Johnson (Healthcare)
- **PG** - Procter & Gamble (Consumer Staples)
- **KO** - Coca-Cola (Beverages)
- **PEP** - PepsiCo (Food & Beverage)
- **WMT** - Walmart (Retail)

### High-Yield Stocks
- **MO** - Altria (Tobacco) - 8%+ yield
- **ABBV** - AbbVie (Pharma) - 4%+ yield
- **T** - AT&T (Telecom) - 6%+ yield
- **VZ** - Verizon (Telecom) - 6%+ yield

### Canadian Dividend Leaders
- **ENB.TO** - Enbridge (Energy Pipeline) - 7%+ yield
- **BCE.TO** - BCE Inc (Telecom) - 6%+ yield
- **TD.TO** - TD Bank (Banking) - 5%+ yield
- **RY.TO** - Royal Bank (Banking) - 4%+ yield

### REITs (Real Estate)
- **O** - Realty Income (Monthly dividend)
- **SPG** - Simon Property Group
- **PSA** - Public Storage

## Performance Metrics

### Analysis Speed
- **Stocks scanned**: 533
- **Time**: 5-10 minutes
- **Rate**: ~1-2 stocks/second
- **Workers**: 15 parallel threads

### Expected Results
- **Dividend stocks found**: 80-150 stocks
- **Top 50**: Best dividend opportunities
- **Categories**: 6 different types
- **Sectors**: 10+ different sectors

## Tips for Using Dividend Stocks

### Income Investors
1. Filter by "High Dividend" or "Dividend" category
2. Set minimum yield to 4%+
3. Focus on stable sectors (Utilities, Consumer Staples)
4. Check dividend history and payout ratio

### Growth + Income Investors
1. Filter by "Growth + Dividend" categories
2. Look for 7%+ growth with 3%+ yield
3. Balance between growth and income
4. Consider reinvesting dividends

### Risk Management
1. Diversify across sectors
2. Check technical scores (prefer 7+/10)
3. Monitor RSI (avoid overbought >70)
4. Review price position (prefer 30-70%)

## Troubleshooting

### Analysis Takes Too Long
- Normal: 5-10 minutes for 600+ stocks
- Timeout: 15 minutes maximum
- Check internet connection
- Verify yfinance is working

### No Dividend Stocks Found
- Check if stock universe is loaded
- Verify yfinance API is accessible
- Review minimum yield criteria (2%)
- Check log output for errors

### Missing Data
- Some stocks may not have dividend data
- Canadian stocks use .TO suffix
- Market data may be delayed
- Verify stock symbols are valid

## Command Reference

```bash
# Run dividend analysis
python dividend_stock_analyzer.py

# Run with virtual environment
source venv_new/bin/activate
python dividend_stock_analyzer.py

# Update all Streamlit data (includes dividends)
python update_streamlit_data.py

# View results
cat top_50_dividend_stocks.json | jq '.top_50_dividend_stocks[0:5]'
```

## Next Steps

1. **Run Analysis**: Generate your first dividend stock report
2. **Review Results**: Check Streamlit dashboard
3. **Set Filters**: Customize based on your investment goals
4. **Monitor**: Run daily or weekly for updates
5. **Compare**: Cross-reference with Gemma AI picks

## Disclaimer

⚠️ **Important**: This analysis is for informational purposes only. Not financial advice. Dividend payments are not guaranteed and can be reduced or eliminated. Past performance does not guarantee future results. Always do your own research and consult with a financial advisor before investing.

---

**Last Updated**: November 18, 2025
**Version**: 1.0
**Feature**: Comprehensive Dividend Stock Scanner
