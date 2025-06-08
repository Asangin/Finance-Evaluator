import yfinance as yf

def calculate_pegy(ticker_symbol, info):
    pe_ratio = info.get("trailingPE")
    earnings_growth = info.get("earningsQuarterlyGrowth")
    dividend_yield = info.get("dividendYield")

    print(f"\n🔍 PEGY Data:")
    print(f"  P/E Ratio: {pe_ratio}")
    print(f"  Earnings Growth: {earnings_growth}")
    print(f"  Dividend Yield: {dividend_yield}")

    if pe_ratio is None or earnings_growth is None or dividend_yield is None:
        print("❌ Missing one or more required data points. Cannot calculate PEGY.")
        return

    dividend_yield_percent = dividend_yield * 100
    earnings_growth_percent = earnings_growth * 100

    if (earnings_growth_percent + dividend_yield_percent) == 0:
        print("❌ Invalid denominator (growth + dividend is zero).")
        return

    pegy = pe_ratio / (earnings_growth_percent + dividend_yield_percent)
    print(f"📊 PEGY Ratio: {pegy:.2f}")


def calculate_dcf(ticker_symbol, info):
    fcf = info.get("freeCashflow")
    shares_outstanding = info.get("sharesOutstanding")

    if fcf is None or shares_outstanding is None:
        print("❌ DCF Calculation requires free cash flow and share count.")
        return

    try:
        fcf = float(fcf)
        shares_outstanding = float(shares_outstanding)
    except:
        print("❌ Invalid numerical data.")
        return

    # User-defined assumptions
    growth_rate = 0.08
    discount_rate = 0.10
    terminal_growth = 0.03
    years = 5

    print(f"\n📉 DCF Inputs:")
    print(f"  Free Cash Flow: ${fcf:,.0f}")
    print(f"  Growth Rate: {growth_rate * 100:.1f}%")
    print(f"  Discount Rate: {discount_rate * 100:.1f}%")
    print(f"  Terminal Growth: {terminal_growth * 100:.1f}%")
    print(f"  Projection Period: {years} years")

    # Project FCFs and calculate present value
    projected_fcfs = []
    for i in range(1, years + 1):
        fcf *= (1 + growth_rate)
        discounted_fcf = fcf / ((1 + discount_rate) ** i)
        projected_fcfs.append(discounted_fcf)

    total_pv_fcfs = sum(projected_fcfs)
    terminal_value = fcf * (1 + terminal_growth) / (discount_rate - terminal_growth)
    discounted_terminal = terminal_value / ((1 + discount_rate) ** years)

    intrinsic_value = total_pv_fcfs + discounted_terminal
    intrinsic_value_per_share = intrinsic_value / shares_outstanding

    print(f"\n💰 DCF Valuation:")
    print(f"  Present Value of FCFs: ${total_pv_fcfs:,.0f}")
    print(f"  Present Value of Terminal Value: ${discounted_terminal:,.0f}")
    print(f"  Total Intrinsic Value: ${intrinsic_value:,.0f}")
    print(f"  📌 Intrinsic Value per Share: ${intrinsic_value_per_share:.2f}")


def calculate_comparables(target_symbol, target_info):
    peers_input = input("Enter comma-separated comparable company tickers (e.g., MSFT,GOOGL,NVDA): ")
    peer_tickers = [p.strip().upper() for p in peers_input.split(",") if p.strip()]

    if not peer_tickers:
        print("⚠️ No peers entered. Skipping comparables.")
        return

    peer_pe_ratios = []
    peer_ps_ratios = []

    print(f"\n🔍 Fetching data for peers: {', '.join(peer_tickers)}")

    for peer in peer_tickers:
        try:
            peer_info = yf.Ticker(peer).info
            peer_pe = peer_info.get("trailingPE")
            peer_ps = peer_info.get("priceToSalesTrailing12Months")
            if peer_pe: peer_pe_ratios.append(peer_pe)
            if peer_ps: peer_ps_ratios.append(peer_ps)
        except Exception as e:
            print(f"❌ Could not fetch data for {peer}: {e}")

    if not peer_pe_ratios and not peer_ps_ratios:
        print("❌ Not enough peer data for comparison.")
        return

    avg_pe = sum(peer_pe_ratios) / len(peer_pe_ratios) if peer_pe_ratios else None
    avg_ps = sum(peer_ps_ratios) / len(peer_ps_ratios) if peer_ps_ratios else None

    print("\n📊 Peer Multiples:")
    if avg_pe:
        print(f"  Average P/E Ratio: {avg_pe:.2f}")
    if avg_ps:
        print(f"  Average P/S Ratio: {avg_ps:.2f}")

    target_eps = target_info.get("trailingEps")
    target_revenue = target_info.get("totalRevenue")
    shares_outstanding = target_info.get("sharesOutstanding")

    print("\n📈 Comparable Valuation for", target_symbol.upper())

    if avg_pe and target_eps:
        implied_price_pe = avg_pe * target_eps
        print(f"  💰 Implied Price by P/E: ${implied_price_pe:.2f}")

    if avg_ps and target_revenue and shares_outstanding:
        implied_market_cap = avg_ps * target_revenue
        implied_price_ps = implied_market_cap / shares_outstanding
        print(f"  💰 Implied Price by P/S: ${implied_price_ps:.2f}")


def print_ticker_current_value(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    price = info.get("currentPrice")
    print(
        f"\n💵 Current Market Price for {symbol.upper()}: ${price:.2f}" if price else "⚠️ Current price not available.")
    return info
