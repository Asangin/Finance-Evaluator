import yfinance as yf
from src.valuation.yfinance_api import ticket_info

def test_yahoo():
    info = ticket_info("META")
    print(info)
    print("sharesOutstanding" + str(info.get("sharesOutstanding", 0)))
    print("previousClose" + str(info.get("previousClose", 0)))

def test_cashflow_info():
    ticker = yf.Ticker("META")
    print(ticker.cashflow)

def test_dividends_info():
    ticker = yf.Ticker("VZ")
    print(ticker.dividends)