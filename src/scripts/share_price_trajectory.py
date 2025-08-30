import pandas as pd

from src.valuation.yfinance_api import ticket_info


def project_company_price(
    current_share_price: float,
    current_shares_outstanding: int,
    base_market_cap_for_upside: float,
    initial_projected_revenue_year1: float,
    projection_years: int,
    scenarios: dict
) -> pd.DataFrame:
    """
    Projects company price based on revenue growth, profit margin, and P/E multiple scenarios.

    Args:
        current_share_price (float): The current trading price per share.
        current_shares_outstanding (int): The current number of shares outstanding.
        base_market_cap_for_upside (float): The baseline market capitalization used for
                                            calculating the '5 Year Upside' (e.g., £2,400m from your image).
        initial_projected_revenue_year1 (float): The revenue for the first projected year (e.g., 2025 revenue).
        projection_years (int): The number of years to project revenue (e.g., 5 for 2025-2029).
        scenarios (dict): A dictionary where keys are scenario names (e.g., 'Low', 'Medium', 'High')
                          and values are dictionaries containing 'revenue_growth_rate' (float)
                          and 'profit_margin' (float).

    Returns:
        pd.DataFrame: A DataFrame containing the projected results for each scenario.
    """

    # Calculate current market capitalization based on provided current price and shares
    current_market_cap_calculated = current_share_price * current_shares_outstanding

    print(f"--- Company Information ---")
    print(f"Current Share Price: £{current_share_price:,.2f}")
    print(f"Current Shares Outstanding: {current_shares_outstanding:,}")
    print(f"Current Market Cap: £{current_market_cap_calculated:,.0f}")
    print(f"Base Market Cap for Upside Calculation: £{base_market_cap_for_upside:,.0f}\n")

    results = {}

    for scenario_name, params in scenarios.items():
        revenue_growth_rate = params['revenue_growth_rate']
        profit_margin = params['profit_margin']
        future_pe_multiple = params['future_pe_multiple'] # Assuming P/E is part of scenario now

        print(f"--- Scenario: {scenario_name} ---")
        print(f"  Revenue Growth Rate: {revenue_growth_rate:.1%}")
        print(f"  Profit Margin: {profit_margin:.1%}")
        print(f"  Future P/E Multiple: {future_pe_multiple}x\n")

        # 1. Project Revenue
        projected_revenues = {}
        current_revenue = initial_projected_revenue_year1
        for i in range(projection_years):
            year = 2025 + i # Starting from 2025 as per your image
            projected_revenues[year] = current_revenue
            current_revenue *= (1 + revenue_growth_rate)

        # The last projected revenue is for the final year (e.g., 2029)
        final_projected_revenue = projected_revenues[2025 + projection_years - 1]
        print(f"  Projected Revenues (Millions £):")
        for year, rev in projected_revenues.items():
            print(f"    {year}: £{rev / 1_000_000:,.0f}m") # Display in millions

        # 2. Calculate Total Earnings for the final year
        final_total_earnings = final_projected_revenue * profit_margin
        print(f"\n  Total Earnings ({2025 + projection_years - 1}): £{final_total_earnings:,.0f}")

        # 3. Calculate Projected Market Cap
        projected_market_cap = final_total_earnings * future_pe_multiple
        print(f"  Projected Market Cap ({2025 + projection_years - 1}): £{projected_market_cap:,.0f}")

        # 4. Calculate Projected Price Per Share
        projected_price_per_share = projected_market_cap / current_shares_outstanding
        print(f"  Projected Price Per Share ({2025 + projection_years - 1}): £{projected_price_per_share:,.2f}")

        # 5. Calculate 5 Year Upside
        # This uses the 'base_market_cap_for_upside' from the model's screenshot
        five_year_upside = (projected_market_cap / base_market_cap_for_upside) - 1
        print(f"  5 Year Upside: {five_year_upside:.2%}\n")

        results[scenario_name] = {
            'Revenue Growth Rate': f"{revenue_growth_rate:.1%}",
            'Profit Margin': f"{profit_margin:.1%}",
            'Future P/E Multiple': f"{future_pe_multiple}x",
            f'Total Earnings ({2025 + projection_years - 1})': f"£{final_total_earnings:,.0f}",
            f'Projected Market Cap ({2025 + projection_years - 1})': f"£{projected_market_cap:,.0f}",
            f'Projected Price/Share ({2025 + projection_years - 1})': f"£{projected_price_per_share:,.2f}",
            '5 Year Upside': f"{five_year_upside:.2%}"
        }

    # Convert results to a pandas DataFrame for better presentation
    results_df = pd.DataFrame.from_dict(results, orient='index')
    return results_df

# --- Model Inputs (Adjust these values) ---
CURRENT_SHARE_PRICE = 2.40 # £2.40 as per the image
CURRENT_SHARES_OUTSTANDING = 145_000_000 # 145m shares
# This is the crucial '£2,400m' from the "Pre Buy Back" row in your image,
# which the model uses as the baseline for upside calculation.
BASE_MARKET_CAP_FOR_UPSIDE = 2_400_000_000

# Initial projected revenue for the first year (2025 in your image)
INITIAL_PROJECTED_REVENUE_2025 = 5_800_000_000 # £5,800m

PROJECTION_YEARS = 5 # Projecting from 2025 to 2029 (5 years)

# Define scenarios with their respective growth rates, profit margins, and P/E multiples
# The P/E multiple (15x) is consistent across all scenarios in your example.
SCENARIOS = {
    'Low': {
        'revenue_growth_rate': 0.03,  # 3%
        'profit_margin': 0.04,        # 4%
        'future_pe_multiple': 15
    },
    'Medium': {
        'revenue_growth_rate': 0.05,  # 5%
        'profit_margin': 0.06,        # 6%
        'future_pe_multiple': 15
    },
    'High': {
        'revenue_growth_rate': 0.07,  # 7%
        'profit_margin': 0.07,        # 7%
        'future_pe_multiple': 15
    }
}

# Run the projection
info = ticket_info("BME.L")
print(info)


final_results_df = project_company_price(
    current_share_price=CURRENT_SHARE_PRICE,
    current_shares_outstanding=CURRENT_SHARES_OUTSTANDING,
    base_market_cap_for_upside=BASE_MARKET_CAP_FOR_UPSIDE,
    initial_projected_revenue_year1=INITIAL_PROJECTED_REVENUE_2025,
    projection_years=PROJECTION_YEARS,
    scenarios=SCENARIOS
)

print("\n--- Summary of Results ---")
print(final_results_df.to_markdown(numalign="left", stralign="left"))
