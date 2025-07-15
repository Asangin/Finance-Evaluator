from src.valuation.yfinance_api import ticket_info


def classify_fast_grower(growth, peg_ratio, free_cash_flow, debt_to_equity):
    # Fast Grower deeper check
    if (
            growth and growth >= 0.25 and
            peg_ratio and 0.5 <= peg_ratio <= 3 and
            free_cash_flow and free_cash_flow > 0 and
            debt_to_equity < 100  # avoid overleveraged growth
            # pe_ratio < 80
    ):
        return True
    else:
        return False

def classify_slow_grower(growth, dividend_yield, payout_ratio, market_cap, pe_ratio, five_year_dividend_growth):
    # Conservative growth (roughly matches GDP)
    slow_growth = growth is not None and 0.01 <= growth <= 0.25
    solid_dividend = dividend_yield >= 0.01 and 0 < payout_ratio <= 0.85
    large_cap = market_cap > 10e9  # Big companies
    upside_is_limited = pe_ratio and pe_ratio <= 20
    # Assume positive 5yr dividend growth if current > 5-year average
    dividend_growth_ok = dividend_yield > five_year_dividend_growth

    return slow_growth and solid_dividend and large_cap and dividend_growth_ok and upside_is_limited

def classify_stalwart(market_cap, growth, earnings_growth, pe_ratio, beta):
    # Stalwart check
    if (
            market_cap > 10e9 and
            0.06 <= growth <= 0.10 and
            earnings_growth and earnings_growth > 0 and
            pe_ratio and 12 <= pe_ratio <= 25 and
            beta <= 1.2
    ):
        return True
    else:
        return False

def classify_company(ticker_symbol):
    try:
        info = ticket_info(ticker_symbol)

        growth = info.get("revenueGrowth", 0)
        print(f"revenueGrowth={growth}")
        pe_ratio = info.get("trailingPE", None)
        print(f"trailingPE={pe_ratio}")
        dividend_yield = info.get("dividendYield", 0) or 0
        print(f"dividendYield={dividend_yield}")
        payout_ratio = info.get("payoutRatio", 0) or 0
        print(f"payoutRatio={payout_ratio}")
        market_cap = info.get("marketCap", 0)
        print(f"marketCap={market_cap}")
        five_year_dividend_growth = info.get("fiveYearAvgDividendYield", 0)  # Yahoo reports this as average yield, not exact growth
        print(f"fiveYearAvgDividendYield={five_year_dividend_growth}")
        earnings_growth = info.get("earningsGrowth", None)
        peg_ratio = pe_ratio / (earnings_growth * 100) if pe_ratio and earnings_growth else None
        print(f"trailingPE/earningsGrowth*100 = PEG: {pe_ratio}/{(earnings_growth * 100)}={peg_ratio}")
        free_cash_flow = info.get("freeCashflow", 0)
        print(f"freeCashflow={free_cash_flow}")
        debt_to_equity = info.get("debtToEquity", 0)
        print(f"debtToEquity={debt_to_equity}")
        beta = info.get("beta", 1)
        print(f"beta {beta}")

        if classify_fast_grower(growth, peg_ratio, free_cash_flow, debt_to_equity):
            return "Fast Grower"
        if classify_slow_grower(growth, dividend_yield, payout_ratio, market_cap, pe_ratio, five_year_dividend_growth):
            return "Slow Grower"
        if classify_stalwart(market_cap, growth, earnings_growth, pe_ratio, beta):
            return "Stalwart"

        sector = info.get("sector", "").lower()
        return (f"company from sector: {sector}. "
                f"Can be one of the: Cyclical, Turnaround, Asset Play. "
                f"Which is hard to define bt script.")

    except Exception as e:
        return f"Error processing {ticker_symbol}: {str(e)}"