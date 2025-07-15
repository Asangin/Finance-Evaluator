from typing import Dict, Optional
import datetime
# --------------------------- Reporting ------------------------------------------
from src.valuation.utility_helpers import fmt_money, fmt_price


def export_report(filename: str,
                  symbol: str,
                  price: Optional[float],
                  pegy: Optional[float],
                  dcf: Optional[Dict],
                  comps: Dict[str, float],
                  avg_multiples: Dict[str, float],
                  rule_of_40: dict):
    lines = []
    lines.append("Valuation Report – " + symbol.upper())
    lines.append("Date: " + datetime.date.today().isoformat())
    lines.append("".ljust(60, "-"))
    if price:
        lines.append(f"Current market price: {fmt_price(price)}")
    lines.append("")

    # PEGY
    if pegy:
        label = pegy["type"]
        lines.append(f"{label}: {pegy['value']:.2f}")
        if label == "PEG":
            lines.append("(Dividend yield not available – showing PEG instead of PEGY)")
    else:
        lines.append("PEGY/PEG: N/A (missing data)")
    lines.append("")

    # DCF
    lines.append("Discounted Cash‑Flow (DCF)")
    if dcf:
        lines.append(f"PV of forecast FCFs: {fmt_money(dcf['pv_fcfs'])}")
        lines.append(f"PV of terminal value: {fmt_money(dcf['pv_terminal'])}")
        lines.append(f"Total equity value: {fmt_money(dcf['total_equity'])}")
        lines.append(f"Intrinsic value per share: {fmt_price(dcf['intrinsic_per_share'])}")
    else:
        lines.append("DCF: N/A (missing data)")
    lines.append("")

    # Comps
    lines.append("Comparable Company Analysis (Comps)")
    if comps:
        for m, pv in comps.items():
            lines.append(f"Implied price by {m}: {fmt_price(pv)} (avg multiple {avg_multiples[m]:.2f})")
    else:
        lines.append("Comps: N/A (missing or insufficient data)")
    lines.append("")

    # Rule of 40
    lines.append("Rule of 40 (Revenue Growth Rate (%) + Profitability Margin (%) should be ≥ 40%)")
    if rule_of_40:
        lines.append(rule_of_40["message"])
    else:
        lines.append("Rule of 40: N/A (missing or insufficient data)")

    # write file
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))