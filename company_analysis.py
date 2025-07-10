import yfinance as yf

from valuation.valuation import ticket_info


def pe_score(pe_ratio):
    if pe_ratio is None:
        return None, "Not available"
    elif pe_ratio >= 64.00:
        return 1, "Very high (Overvalued)"
    elif pe_ratio >= 53.00:
        return 2, "Very high"
    elif pe_ratio >= 43.00:
        return 3, "High"
    elif pe_ratio >= 33.00:
        return 4, "Moderately high"
    elif pe_ratio > 23.00:
        return 5, "Fair"
    elif pe_ratio == 23.00:
        return 6, "Average"
    elif pe_ratio > 22.98:
        return 7, "Slightly undervalued"
    elif pe_ratio >= 17.99:
        return 8, "Undervalued"
    elif pe_ratio >= 12.99:
        return 9, "Very undervalued"
    else:
        return 10, "Extremely undervalued"


def ev_to_ebitda_score(ev_ebitda):
    if ev_ebitda is None:
        return None, "Not available"

    if ev_ebitda <= 6.00:
        return 10, "Very low — undervalued (or risk of weak outlook)"
    elif ev_ebitda <= 8.00:
        return 9, "Low — potentially undervalued"
    elif ev_ebitda <= 10.00:
        return 8, "Reasonable — average"
    elif ev_ebitda <= 12.00:
        return 7, "Slightly high"
    elif ev_ebitda <= 15.00:
        return 5, "High — potentially overvalued"
    elif ev_ebitda <= 18.00:
        return 3, "Very high"
    else:
        return 1, "Extremely high — rich valuation"


def pb_score(pb_ratio):
    """
    Interpretation
    P/B ≈ 1–2: Fairly valued or undervalued depending on industry. Considered good.
    P/B > 3–4: Can be reasonable for high-growth/tech companies.
    P/B > 10: Often considered expensive, possibly overvalued.
    """
    if pb_ratio is None:
        return None, "Not available"

    if pb_ratio <= 1.00:
        return 10, "Deep value"
    elif pb_ratio < 2.00:
        return 9, "Undervalued"
    elif pb_ratio < 3.00:
        return 8, "Fair valuation (ideal)"
    elif pb_ratio < 4.00:
        return 7, "Slightly overvalued"
    elif pb_ratio < 6.00:
        return 6, "Mildly expensive"
    elif pb_ratio < 8.00:
        return 5, "Expensive"
    elif pb_ratio < 10.00:
        return 3, "Very expensive"
    else:
        return 1, "Extremely overvalued"

def ps_score(ps_ratio):
    """
    How to Interpret P/S:
    The lower, the better (generally).
    A low P/S can suggest the company is undervalued relative to its revenue.
    However, industry context matters (tech firms tend to have higher P/S).
    """
    if ps_ratio is None:
        return None, "Not available"

    if ps_ratio <= 0.5:
        return 10, "Extremely undervalued"
    elif ps_ratio <= 1.0:
        return 9, "Undervalued"
    elif ps_ratio <= 1.5:
        return 8, "Fairly valued"
    elif ps_ratio <= 2.0:
        return 7, "Slightly high"
    elif ps_ratio <= 3.0:
        return 6, "Expensive"
    elif ps_ratio <= 5.0:
        return 4, "Overvalued"
    elif ps_ratio <= 8.0:
        return 2, "Very overvalued"
    else:
        return 1, "Extremely overvalued / hype"

def earnings_growth_score(growth):
    if growth is None:
        return None, "Not available"

    growth_percent = growth * 100

    if growth_percent <= -10.01:
        return 1, "Strongly negative"
    elif growth_percent <= -5.00:
        return 2, "Very weak"
    elif growth_percent < 0.00:
        return 3, "Weak"
    elif growth_percent < 5.00:
        return 4, "Low growth"
    elif growth_percent < 10.00:
        return 5, "Modest growth"
    elif growth_percent == 10.00:
        return 6, "Good baseline"
    elif growth_percent < 20.00:
        return 7, "Strong growth"
    elif growth_percent < 30.00:
        return 8, "Very strong growth"
    elif growth_percent < 40.00:
        return 9, "Excellent"
    else:
        return 10, "Hyper growth"


def profit_margin_score(margin):
    if margin is None:
        return None, "Not available"

    margin_percent = margin * 100

    if margin_percent <= -10.01:
        return 1, "Severe loss"
    elif margin_percent <= -5.00:
        return 2, "Very poor"
    elif margin_percent < 0.00:
        return 3, "Negative margin"
    elif margin_percent < 5.00:
        return 4, "Very low margin"
    elif margin_percent < 10.00:
        return 5, "Low margin"
    elif margin_percent == 10.00:
        return 6, "Average"
    elif margin_percent < 20.00:
        return 7, "Moderate"
    elif margin_percent < 30.00:
        return 8, "Good"
    elif margin_percent < 40.00:
        return 9, "Excellent"
    else:
        return 10, "Outstanding"


def roe_score(roe):
    if roe is None:
        return None, "Not available"

    roe_percent = roe * 100

    if roe_percent <= -5.01:
        return 1, "Extremely bad"
    elif roe_percent < 0.00:
        return 2, "Very poor"
    elif roe_percent < 5.00:
        return 3, "Weak return"
    elif roe_percent < 10.00:
        return 4, "Below average"
    elif roe_percent < 15.00:
        return 5, "Average"
    elif roe_percent == 15.00:
        return 6, "Good baseline"
    elif roe_percent < 25.00:
        return 7, "Solid performance"
    elif roe_percent < 35.00:
        return 8, "Strong"
    elif roe_percent < 45.00:
        return 9, "Excellent"
    else:
        return 10, "Exceptional"


def dividend_yield_score(yield_percent):
    if yield_percent is None:
        return None, "Not available"

    if yield_percent == 0.00:
        return 1, "No dividend"
    elif yield_percent <= 0.24:
        return 2, "Very low"
    elif yield_percent <= 0.49:
        return 3, "Low"
    elif yield_percent <= 0.99:
        return 4, "Mild"
    elif yield_percent <= 1.24:
        return 5, "Okay"
    elif yield_percent == 1.25:
        return 6, "Baseline"
    elif yield_percent <= 1.50:
        return 7, "Decent"
    elif yield_percent <= 2.00:
        return 8, "Good"
    elif yield_percent <= 2.50:
        return 9, "Very good"
    else:
        return 10, "High yield"


def analyze_company(ticker_symbol):
    # Fetch data
    info = ticket_info(symbol)

    try:
        print(f"\n--- Analysis for {info.get('shortName', ticker_symbol)} ({ticker_symbol}) ---")

        # P/E Analysis with score
        pe_ratio = info.get("trailingPE")
        print(f"PE Ratio: {pe_ratio}")
        score, description = pe_score(pe_ratio)
        if score is not None:
            print(f"   - Score: {score}/10 ({description})")
        else:
            print(f"   - {description}")

        # EV/EBITDA
        ev_ebitda = info.get("enterpriseToEbitda")
        print(f"EV/EBITDA: {ev_ebitda}")
        score, description = ev_to_ebitda_score(ev_ebitda)
        if score is not None:
            print(f"   - Score: {score}/10 ({description})")
        else:
            print(f"   - {description}")

        # P/S Ratio
        ps_ratio = info.get("priceToSalesTrailing12Months")
        print(f"P/S Ratio: {ps_ratio}")
        score, description = ps_score(ps_ratio)
        if score is not None:
            print(f"   - Score: {score}/10 ({description})")
        else:
            print(f"   - {description}")

        # P/B Ratio
        pb_ratio = info.get("priceToBook")
        print(f"P/B Ratio: {pb_ratio}")
        score, description = pb_score(pb_ratio)
        if score is not None:
            print(f"   - Score: {score}/10 ({description})")
        else:
            print(f"   - {description}")

        # Earnings Growth Analysis
        growth_5y = info.get(
            "earningsQuarterlyGrowth")  # Yahoo doesn't always have 5y forward, using quarterly as proxy
        print(f"Earnings Growth (YoY as proxy): {growth_5y * 100:.2f}%")
        score, description = earnings_growth_score(growth_5y)
        if score is not None:
            print(f"   - Score: {score}/10 ({description})")
        else:
            print(f"   - {description}")

        # Profit Margin
        profit_margin = info.get("profitMargins")
        if profit_margin is not None:
            margin_percent = profit_margin * 100
            print(f"Profit Margin: {margin_percent:.2f}%")
        else:
            print("Profit Margin: Not available")

        score, description = profit_margin_score(profit_margin)
        print(f"   - Score: {score}/10 ({description})" if score else f"   - {description}")

        # ROE
        roe = info.get("returnOnEquity")
        if roe is not None:
            roe_percent = roe * 100
            print(f"Return on Equity (ROE): {roe_percent:.2f}%")
        else:
            print("ROE: Not available")

        score, description = roe_score(roe)
        print(f"   - Score: {score}/10 ({description})" if score else f"   - {description}")

        # Dividend Yield
        dividend_yield = info.get("dividendYield")
        if dividend_yield is not None:
            yield_percent = dividend_yield
            print(f"Dividend Yield: {yield_percent:.2f}%")
        else:
            print("Dividend Yield: Not available")

        score, description = dividend_yield_score(dividend_yield)
        print(f"   - Score: {score}/10 ({description})" if score else f"   - {description}")

        # Total Score
        metrics = [
            pe_score(pe_ratio)[0],
            ev_to_ebitda_score(ev_ebitda)[0],
            earnings_growth_score(growth_5y)[0],
            profit_margin_score(profit_margin)[0],
            roe_score(roe)[0],
            dividend_yield_score(dividend_yield)[0]
        ]

        total_score = sum(score for score in metrics if score is not None)
        count = sum(1 for score in metrics if score is not None)

        if count:
            print(f"\n📊 Final Score: {total_score}/{count * 10} ({(total_score / (count * 10)) * 100:.1f}%)")
        else:
            print("\n📊 Final Score: Not enough data")

    except Exception as e:
        print(f"Error fetching or analyzing data for {ticker_symbol}: {e}")


if __name__ == "__main__":
    # Example: Apple
    symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
    analyze_company(symbol)
