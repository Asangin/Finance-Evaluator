import yfinance as yf

from typing import List, Dict, Optional
from pytickersymbols import PyTickerSymbols
from src.valuation.utility_helpers import safe_get


# ------------------------------- PEGY -------------------------------------------

def calculate_pegy(info: Dict) -> Optional[Dict[str, float]]:
    pe = safe_get(info, "trailingPE")
    growth = safe_get(info, "earningsQuarterlyGrowth")
    dividend_yield = safe_get(info, "dividendYield")

    if pe is None or growth is None:
        print("⚠️ trailingPE is missing")
        return None

    growth_pct = growth * 100
    if dividend_yield:
        dividend_pct = dividend_yield * 100
        denominator = growth_pct + dividend_pct
        if denominator == 0:
            return None
        return {"type": "PEGY", "value": pe / denominator}
    else:
        if growth_pct == 0:
            return None
        return {"type": "PEG", "value": pe / growth_pct}


def interpret_pegy_ratio(pegy: float) -> str:
    if pegy < 1:
        return f"✅ PEGY/PEG Ratio {pegy:.2f} suggests the stock may be undervalued."
    elif pegy < 2:
        return f"⚖️ PEGY/PEG Ratio {pegy:.2f} suggests fair valuation."
    else:
        return f"⚠️ PEGY/PEG Ratio {pegy:.2f} suggests the stock may be overvalued."


# ------------------------------- DCF --------------------------------------------

def calculate_dcf_v2(info: Dict,
                  growth_rate: float,
                  years: int = 5,
                  discount_rate: float = 0.10,
                  terminal_growth: float = 0.03) -> Optional[Dict]:
    """Return a dict with intrinsic value components or None if data missing."""
    fcf = safe_get(info, "freeCashflow")  # trailing twelve months
    shares_out = safe_get(info, "sharesOutstanding")
    if growth_rate == 0.0:
        growth_rate = info.get("earningsGrowth", 0.05)
    if None in (fcf, shares_out):
        return None

    # Project FCFs and discount
    projected_pvs = []
    next_fcf = fcf
    for year in range(1, years + 1):
        next_fcf *= (1 + growth_rate)
        discounted = next_fcf / ((1 + discount_rate) ** year)
        projected_pvs.append(discounted)

    pv_fcfs = sum(projected_pvs)

    # Terminal value (Gordon growth model)
    terminal_value = next_fcf * (1 + terminal_growth) / (discount_rate - terminal_growth)
    pv_terminal = terminal_value / ((1 + discount_rate) ** years)

    total_equity_value = pv_fcfs + pv_terminal
    intrinsic_per_share = total_equity_value / shares_out

    return {
        "pv_fcfs": pv_fcfs,
        "pv_terminal": pv_terminal,
        "total_equity": total_equity_value,
        "intrinsic_per_share": intrinsic_per_share,
    }


# --------------------------- Peer suggestion ------------------------------------

def suggest_peers(
        target_industry: str,
        exclude: str = '',
        index: str = 'S&P 500',  # 'S&P 500', 'DAX', 'FTSE 100'
        max_peers: int = 10) -> List[str]:
    """Return up to `max_peers` peer tickers in the same industry."""
    stock_data = PyTickerSymbols()
    stocks = stock_data.get_stocks_by_index(index)
    peers = []
    for stock in stocks:
        symbol = stock.get("symbol")
        industries = stock.get("industries")
        # print(f"symbol: ${symbol}, industries: ${industries}")
        for item in industries:
            if (target_industry.lower() == str(item).lower()):
                peers.append(symbol)
        if len(peers) >= max_peers:
            break
    return peers


def suggest_multiple_peers(
        target_industry: str,
        exclude: str = '',
        indexes: list[str] = ('S&P 500', 'DAX', 'FTSE 100'),
        max_peers: int = 10) -> List[str]:
    """Return up to `max_peers` peer tickers in the same industry."""
    stock_data = PyTickerSymbols()
    stocks = []
    for index in indexes:
        index_stock = stock_data.get_stocks_by_index(index)
        for s in index_stock:
            stocks.append(s)

    peers = []
    for stock in stocks:
        symbol = stock.get("symbol")
        industries = stock.get("industries")
        # print(f"symbol: ${symbol}, industries: ${industries}")
        for item in industries:
            if (is_partial_match(target_industry, item)):
                peers.append(symbol)
        if len(peers) >= max_peers:
            break
    return peers


def is_partial_match(source: str, target: str) -> bool:
    source_words = set(source.lower().split())
    target_words = set(target.lower().split())
    return target_words.issubset(source_words)


# --------------------------- Comparable valuation -------------------------------

def collect_peer_multiples(tickers: List[str], multiples: List[str]) -> Dict[str, List[float]]:
    """Fetch selected multiples for peer tickers and return dict of lists."""
    data: Dict[str, List[float]] = {m: [] for m in multiples}
    for peer in tickers:
        try:
            info = yf.Ticker(peer).info
        except Exception:
            continue
        if "P/E" in multiples:
            val = safe_get(info, "trailingPE")
            if val:
                data["P/E"].append(val)
        if "P/S" in multiples:
            val = safe_get(info, "priceToSalesTrailing12Months")
            if val:
                data["P/S"].append(val)
        if "EV/EBITDA" in multiples:
            val = safe_get(info, "enterpriseToEbitda")
            if val:
                data["EV/EBITDA"].append(val)
    return data


def apply_comps(target_info: Dict, avg_multiples: Dict[str, float]) -> Dict[str, float]:
    """Return implied price per share for each multiple (where possible)."""
    implied_prices: Dict[str, float] = {}
    shares_out = safe_get(target_info, "sharesOutstanding")
    if not shares_out:
        return implied_prices

    if "P/E" in avg_multiples:
        eps = safe_get(target_info, "trailingEps")
        if eps:
            implied_prices["P/E"] = avg_multiples["P/E"] * eps

    if "P/S" in avg_multiples:
        revenue = safe_get(target_info, "totalRevenue")
        if revenue:
            market_cap = avg_multiples["P/S"] * revenue
            implied_prices["P/S"] = market_cap / shares_out

    if "EV/EBITDA" in avg_multiples:
        ebitda = safe_get(target_info, "ebitda")
        total_debt = safe_get(target_info, "totalDebt") or 0
        cash = safe_get(target_info, "cash") or 0
        if ebitda and (total_debt is not None) and (cash is not None):
            implied_ev = avg_multiples["EV/EBITDA"] * ebitda
            implied_market_cap = implied_ev - total_debt + cash
            implied_prices["EV/EBITDA"] = implied_market_cap / shares_out

    return implied_prices


def ticket_info(symbol):
    ticker = yf.Ticker(symbol)
    return ticker.info


def rule_of_40(revenue_growth_rate: float, profitability_margin: float) -> dict:
    """
    Revenue Growth Rate (%) + Profitability Margin (%) should be ≥ 40%
    (Profitability is usually measured using EBITDA margin, operating margin, or free cash flow margin.)
    """
    score = revenue_growth_rate + profitability_margin
    meets = score >= 40  # TODO for tech only, need to understand this value for other companies
    message = (
        f"✅ Meets Rule of 40 (Score = {score:.2f}%)"
        if meets else
        f"❌ Does NOT meet Rule of 40 (Score = {score:.2f}%)"
    )
    explanation = (
        "The Rule of 40 is a benchmark used to evaluate growth companies, especially in tech. "
        "It adds Revenue Growth Rate (%) and Profitability Margin (%). If the sum is ≥ 40%, "
        "the company is considered to have a healthy balance between growth and profitability."
    )
    return {
        "score": score,
        "meets_rule": meets,
        "message": message,
        "explanation": explanation
    }


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
