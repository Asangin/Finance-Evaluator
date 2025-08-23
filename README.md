# Comapanies analyses tool

> This repository was created only for educational purposes. Use it at your own risk.

## API

> [finviz api](https://stock-analysis-engine.readthedocs.io/en/latest/finviz_api.html)
> [Download market data from Yahoo! Finance's API](https://pypi.org/project/yfinance/)

Most of the script was built on top of the Yahoo API.

## Main script

> [valuation_tool](src/scripts/valuation_tool_main.py)

## Quick company analysis script

> [company_analysis](src/scripts/company_analysis.py)

## Trade Reports converter

> [converter from ibkr to yahoo finance](src/scripts/convert_ibkr_to_yahoo_finance_trade_report.py)

There is also open AI model available to recreate scrip in any language by uploading [spec](open_ai_spec) and send a
promt: `Please regenerate the Python script based on this spec.` to AI chat.

## Run test

```bash
pytest test/test_yahoo.py::test_yahoo
pytest test/test_yahoo.py::test_fcf_info
```
