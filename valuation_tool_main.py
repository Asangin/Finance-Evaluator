# valuation_tool_main.py
"""
A console application that provides three valuation methods for a given stock ticker:

1. PEGY Ratio
2. Discounted Cash‑Flow (DCF) intrinsic value per share
3. Comparable Company Analysis (Comps) with user‑selected multiples (P/E, P/S, EV/EBITDA)

Features
--------
* Auto‑suggests peer companies from the same industry (S&P 500 universe) using yfinance.
* Lets the user decide which valuation multiples to apply.
* Creates a plain‑text report file summarising all results.

Requirements
------------
$ pip install yfinance pandas numpy

Run
---
$ python valuation_tool_main.py

The script will interactively ask for:
* Target ticker symbol (e.g. AAPL)
* Whether to use auto‑suggested peers
* Manual peer tickers (comma‑separated) to add / override
* Multiples to include (P/E, P/S, EV/EBITDA)
* Optional DCF parameters (defaults can be accepted by pressing ↵)
"""

import numpy as np

from valuation.reporting import export_report
from valuation.utility_helpers import safe_get, fmt_price
from valuation.valuation import ticket_info, calculate_pegy, calculate_dcf, suggest_peers, collect_peer_multiples, \
    apply_comps, rule_of_40, suggest_multiple_peers, interpret_pegy_ratio


# --------------------------- Main interactive flow ------------------------------

def prompt_float(prompt: str, default: float) -> float:
    raw = input(f"{prompt} [{default}]: ").strip()
    try:
        return float(raw) if raw else default
    except ValueError:
        print("Invalid number – using default.")
        return default


def main():
    print("\n📈 Comprehensive Valuation Tool (PEGY • DCF • Comps)\n")

    while True:
        symbol = input("Enter target stock ticker (or 'exit'): ").strip()
        if symbol.lower() == "exit":
            break
        if not symbol:
            continue

        info = ticket_info(symbol)

        price = safe_get(info, "currentPrice")
        if price:
            print(f"\n💵Current market price for {symbol.upper()}: {fmt_price(price)}")
        else:
            print("\n⚠️ Current price unavailable.")

        # ---------------- PEGY ----------------
        pegy_val = calculate_pegy(info)
        if pegy_val:
            print(f"📊 {pegy_val['type']} ratio: {pegy_val['value']:.2f}")
            if pegy_val['type'] == "PEG":
                print("(Dividend yield not available – showing PEG instead of PEGY)")
        else:
            print("PEGY/PEG ratio not available (missing data).")

        ratio_msg = interpret_pegy_ratio(pegy_val['value'])
        print(ratio_msg)

        # ---------------- DCF -----------------
        print("\nEnter DCF assumptions (press ↵ to accept default):")
        g_rate = prompt_float("FCF growth rate (will be fetch from company info, if not specified)", 0.0)
        d_rate = prompt_float("Discount rate (as decimal)", 0.10)
        t_growth = prompt_float("Terminal growth rate (as decimal)", 0.03)
        years = int(prompt_float("Projection years", 5))

        dcf_res = calculate_dcf(info, g_rate, years, d_rate, t_growth)
        if dcf_res:
            print("Result: ")
            print(f"💰 Discounted Cash Flow (5y): {fmt_price(dcf_res['pv_fcfs'])}")
            print(f"💰 Terminal value (Gordon growth model): {fmt_price(dcf_res['pv_terminal'])}")
            print(f"💰 Total equity: {fmt_price(dcf_res['total_equity'])}")
            print(f"📌 Intrinsic value per share (DCF): {fmt_price(dcf_res['intrinsic_per_share'])}")
        else:
            print("⚠️ DCF valuation unavailable (missing data).")

        # -------------- Peer suggestion ---------------
        industry = safe_get(info, "industry")
        print(f"\nIndustry: {industry if industry else 'N/A'}")
        suggested = []
        if industry:
            suggested = suggest_multiple_peers(industry)
            if suggested:
                print(f"\n🤝 Suggested peers in same industry ({industry}): {', '.join(suggested)}")
        manual_peers = input("Enter additional/comma‑separated peer tickers (or press ↵ to use suggested only): ")
        extra = [p.strip().upper() for p in manual_peers.split(',') if p.strip()]
        peer_list = list({*suggested, *extra})  # unique set
        if not peer_list:
            print("⚠️ No peers specified – skipping Comparable valuation.")
            comps_prices = {}
            avg_mults = {}
        else:
            # -------------- Multiples selection --------------
            print("\nAvailable multiples: P/E, P/S, EV/EBITDA")
            multiples_raw = input("Choose multiples (comma‑separated): ").upper().split(',')
            chosen_multiples = [m.strip() for m in multiples_raw if m.strip() in [
                "P/E", "P/S", "EV/EBITDA"]]
            if not chosen_multiples:
                print("No valid multiples chosen – skipping Comparable valuation.")
                comps_prices = {}
                avg_mults = {}
            else:
                print("Fetching peer multiples … this may take a moment.")
                peer_mult_lists = collect_peer_multiples(peer_list, chosen_multiples)
                avg_mults = {m: np.mean(vals) for m, vals in peer_mult_lists.items() if vals}
                if not avg_mults:
                    print("Insufficient peer data – skipping Comparable valuation.")
                    comps_prices = {}
                else:
                    comps_prices = apply_comps(info, avg_mults)
                    if comps_prices:
                        print("\nComparable valuation (implied prices):")
                        for m, p in comps_prices.items():
                            print(f"{m}: {fmt_price(p)} (avg multiple {avg_mults[m]:.2f})")
                    else:
                        print("Comparable valuation could not be calculated (missing target data).")

        # -------------- Rule of 40 ---------------

        revenue_growth = info.get("revenueGrowth", 0) * 100
        profitability = info.get("operatingMargins", 0) * 100
        rule40 = rule_of_40(revenue_growth, profitability)
        print("📐 Rule of 40:", rule40["message"])

        # -------------- Export report ---------------
        report_name = f"{symbol.upper()}_valuation_report.txt"
        export_report(report_name, symbol, price, pegy_val, dcf_res, comps_prices, avg_mults, rule40)
        print(f"\n📄 Report saved to {report_name}\n")


if __name__ == "__main__":
    main()
