from src.valuation.yfinance_api import check_dividends_and_ddm, dcf_valuation, ticket_info


def test_fcf():
    result = check_dividends_and_ddm("NVO")
    print(result)

def test_dcf_model():
    """
    Discounted Cash Flow (DCF) Method
    Most popular and widely used.
    This method is good for stable companies with predictable cash flows.
    """
    stock = "GOOG"
    info = ticket_info(stock)
    freeCashflow = info.get("freeCashflow", None)
    sharesOutstanding = info.get("sharesOutstanding", None)
    totalCash = info.get("totalCash", None)
    totalDebt = info.get("totalDebt", None)
    print(f"freeCashflow: {freeCashflow}")
    print(f"sharesOutstanding: {sharesOutstanding}")
    print(f"totalCash: {totalCash}")
    print(f"totalCash: {totalDebt}")
    fair_value = dcf_valuation(
        fcf=freeCashflow,  # $10B FCF
        growth_rate=0.08,  # 8% growth
        discount_rate=0.10,  # 10% discount rate
        terminal_growth=0.03,  # 3% terminal growth
        years=5,  # 5-year forecast
        debt=totalDebt,  # $20B debt
        cash=totalCash,  # $10B cash
        shares_outstanding=sharesOutstanding  # 1B shares
    )

    print(f"Stock: {stock}")
    print(f"Curent Price: ${info.get('currentPrice')}")
    print(f"Fair Value per Share: ${fair_value:.2f}")

