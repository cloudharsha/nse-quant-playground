"""
Quick test script to verify NSE data availability and timeframes
"""
import yfinance as yf
from datetime import datetime, timedelta

def test_ticker(ticker_symbol):
    """Test a single ticker for data availability"""
    print(f"\n{'='*60}")
    print(f"Testing: {ticker_symbol}")
    print('='*60)

    ticker = yf.Ticker(ticker_symbol)

    # Test different timeframes
    timeframes = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d']

    print("\nChecking timeframes:")
    available_timeframes = []

    for tf in timeframes:
        try:
            # Try to fetch recent data
            test_data = ticker.history(period='5d', interval=tf)
            if not test_data.empty:
                print(f"  ✓ {tf:5s} - Available ({len(test_data)} candles)")
                available_timeframes.append(tf)
            else:
                print(f"  ✗ {tf:5s} - No data")
        except Exception as e:
            print(f"  ✗ {tf:5s} - Error: {str(e)[:50]}")

    # Get company info
    try:
        info = ticker.info
        print(f"\nCompany Info:")
        print(f"  Name: {info.get('longName', 'N/A')}")
        print(f"  Sector: {info.get('sector', 'N/A')}")
        print(f"  Market Cap: {info.get('marketCap', 'N/A')}")
    except:
        print("\nCould not fetch company info")

    return available_timeframes

def main():
    """Main test function"""
    print("="*60)
    print("NSE Data Availability Test")
    print("="*60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test a few major stocks
    test_stocks = [
        'RELIANCE.NS',
        'TCS.NS',
        'INFY.NS'
    ]

    all_timeframes = set()

    for stock in test_stocks:
        available = test_ticker(stock)
        all_timeframes.update(available)

    print(f"\n{'='*60}")
    print("Summary")
    print('='*60)
    print(f"Timeframes available across all tested stocks:")
    for tf in sorted(all_timeframes):
        print(f"  - {tf}")

    print(f"\nRecommendation:")
    if '1m' in all_timeframes:
        print("  ✓ Use 1-minute timeframe for highest granularity")
    elif '2m' in all_timeframes:
        print("  ✓ Use 2-minute timeframe (1m not available)")
    elif '5m' in all_timeframes:
        print("  ✓ Use 5-minute timeframe (1m, 2m not available)")
    else:
        print(f"  ✓ Use {min(all_timeframes)} timeframe (lowest available)")

if __name__ == "__main__":
    main()