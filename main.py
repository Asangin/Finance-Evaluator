# main.py
from src.scripts.company_analysis import analyze_company
from src.scripts.convert_ibkr_to_yahoo_finance_trade_report import convert_ibkr_to_yahoo_finance
from src.scripts.lynch_company_category import classify_company
from src.scripts.valuation_tool_main import run_valuation
from src.valuation.yfinance_api import dcf_intrinsic_value


def run_ui_tests():
    print("Running UI tests... (placeholder)")
    # Add actual UI test logic here

def run_api_tests():
    print("Running API tests... (placeholder)")
    # Add actual API test logic here

def explore_product_feature():
    print("Exploring product feature... (placeholder)")
    # Add product exploration logic here

def show_menu():
    print("\n=== Automation Task Menu ===")
    print("1. Valuation tool")
    print("2. Simple company analysis")
    print("3. Peter Lynch company category")
    print("4. Convert IBKR csv report into Yahoo finance csv report")
    print("5. Intrinsic Value per Share")
    print("0. Exit")

def main():
    while True:
        show_menu()
        choice = input("Choose an option (0-5): ").strip()

        if choice == "1":
            run_valuation()
        elif choice == "2":
            symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
            analyze_company(symbol)
        elif choice == "3":
            symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
            classification = classify_company(symbol)
            print(f"\n Company classified as {classification}")
        elif choice == "4":
            convert_ibkr_to_yahoo_finance()
        elif choice == "5":
            symbol = input("Enter stock symbol (e.g., AAPL): ").upper()
            intrinsic_value, equity_value, enterprise_value = dcf_intrinsic_value(symbol)
            print(f"Intrinsic Value per Share for {symbol}: ${intrinsic_value:.2f}")
            print(f"Equity Value: ${equity_value / 1e9:.2f} B")
            print(f"Enterprise Value: ${enterprise_value / 1e9:.2f} B")
        elif choice == "0":
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
