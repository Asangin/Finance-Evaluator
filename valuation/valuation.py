from typing import List, Dict, Optional

from pytickersymbols import PyTickerSymbols
import yfinance as yf

from valuation.utility_helpers import safe_get


# ------------------------------- PEGY -------------------------------------------

def calculate_pegy(info: Dict) -> Optional[Dict[str, float]]:
    pe = safe_get(info, "trailingPE")
    growth = safe_get(info, "earningsQuarterlyGrowth")
    dividend_yield = safe_get(info, "dividendYield")

    if pe is None or growth is None:
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


# ------------------------------- DCF --------------------------------------------

def calculate_dcf(info: Dict,
                  years: int = 5,
                  growth_rate: float = 0.08,
                  discount_rate: float = 0.10,
                  terminal_growth: float = 0.03) -> Optional[Dict]:
    """Return a dict with intrinsic value components or None if data missing."""
    fcf = safe_get(info, "freeCashflow")  # trailing twelve months
    shares_out = safe_get(info, "sharesOutstanding")
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

def suggest_peers(target_industry: str, exclude: str, index: str = 'S&P 500', max_peers: int = 10) -> List[str]:
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
    meets = score >= 40 # TODO for tech only, need to understand this value for other companies
    message = (
        f"✅ Meets Rule of 40 (Score = {score:.2f}%)"
        if meets else
        f"❌ Does NOT meet Rule of 40 (Score = {score:.2f}%)"
    )
    return {
        "score": score,
        "meets_rule": meets,
        "message": message
    }
