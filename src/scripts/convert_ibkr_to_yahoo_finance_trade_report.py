import csv
from datetime import datetime

# Input and output file paths
input_file = 'Yahoo_finance_export 2.csv'
output_file = 'converted_trades.csv'

# Mapping to output format
output_headers = [
    "Symbol", "Current Price", "Date", "Time", "Change",
    "Open", "High", "Low", "Volume", "Trade Date",
    "Purchase Price", "Quantity", "Commission",
    "High Limit", "Low Limit", "Comment", "Transaction Type"
]


def parse_datetime(datetime_str):
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d,%H%M %Z")
        return dt.strftime("%Y/%m/%d"), dt.strftime("%H:%M %Z")
    except Exception as e:
        return "", ""


def convert_row(row):
    date_str, time_str = parse_datetime(row["Date/Time"])
    return {
        "Symbol": row["Symbol"],
        "Current Price": "",
        "Date": date_str,
        "Time": time_str,
        "Change": "",  # No data in original
        "Open": "",  # No data in original
        "High": "",  # No data in original
        "Low": "",  # No data in original
        "Volume": "",  # No data in original
        "Trade Date": row["TradeDate"].replace("-", ""),
        "Purchase Price": row["Price"],
        "Quantity": row["Quantity"],
        "Commission": row["Commission"],
        "High Limit": "",
        "Low Limit": "",
        "Comment": "",
        "Transaction Type": row["Buy/Sell"]
    }


def convert_ibkr_to_yahoo_finance():
    # Read, convert, and write
    with open(input_file, newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=output_headers)
        writer.writeheader()

        for row in reader:
            converted = convert_row(row)
            writer.writerow(converted)

    print(f"Conversion completed. Output written to {output_file}")
