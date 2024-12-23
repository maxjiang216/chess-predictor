import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def compute_portfolio_returns(portfolios, portfolio_names=None, start_date=None):
    """
    Computes and graphs the historical return of multiple portfolios from each date to the most recent date.

    Parameters:
        portfolios (list): A list of dictionaries where each represents a portfolio. Keys are stock names and values are their portfolio weights (0 to 1).
                           The sum of weights should be <= 1. The remaining weight is held in cash.
        portfolio_names (list, optional): A list of names for the portfolios to display in the legend.
        start_date (str, optional): The start date for the analysis in "YYYY-MM-DD" format. Defaults to the earliest date in the data.

    Returns:
        None
    """
    if portfolio_names is None:
        portfolio_names = [f"Portfolio {i + 1}" for i in range(len(portfolios))]

    results = {}

    for portfolio_index, portfolio in enumerate(portfolios):
        # Read data and preprocess
        stock_data = {}
        for stock, weight in portfolio.items():
            if stock.lower() == "btc":
                # Read and preprocess btc.csv
                btc_df1 = pd.read_csv("btc.csv")
                btc_df1['Date'] = pd.to_datetime(btc_df1['Date'])
                btc_df1 = btc_df1.sort_values(by='Date')

                # Remove commas and convert to float
                btc_df1['Price'] = btc_df1['Price'].str.replace(',', '').astype(float)
                btc_df1['Open'] = btc_df1['Open'].str.replace(',', '').astype(float)
                btc_df1['Average Price'] = (btc_df1['Price'] + btc_df1['Open']) / 2

                # Read and preprocess btc2.csv
                btc_df2 = pd.read_csv("btc2.csv")
                btc_df2['Date'] = pd.to_datetime(btc_df2['Date'])
                btc_df2 = btc_df2.sort_values(by='Date')

                # Remove commas and convert to float for 'Open' and 'Close/Last'
                btc_df2['Open'] = btc_df2['Open'].astype(str).str.replace(',', '').astype(float)
                btc_df2['Close/Last'] = btc_df2['Close/Last'].astype(str).str.replace(',', '').astype(float)
                btc_df2['Average Price'] = (btc_df2['Open'] + btc_df2['Close/Last']) / 2

                # Concatenate and remove overlapping dates
                btc_combined = pd.concat([btc_df1, btc_df2])
                btc_combined = btc_combined.drop_duplicates(subset='Date', keep='last')

                stock_data[stock] = btc_combined.set_index('Date')[['Average Price']].rename(columns={'Average Price': stock})
            else:
                filename = f"{stock}.csv"
                if not os.path.exists(filename):
                    raise FileNotFoundError(f"Stock file '{filename}' does not exist.")

                df = pd.read_csv(filename)
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values(by='Date')  # Ensure dates are in ascending order

                # Remove commas and convert to float for relevant columns
                if 'Close/Last' in df.columns and 'Open' in df.columns:
                    df['Open'] = df['Open'].astype(str).str.replace(',', '').str.replace('$', '').astype(float)
                    df['Close/Last'] = df['Close/Last'].astype(str).str.replace(',', '').str.replace('$', '').astype(float)
                    df['Average Price'] = (df['Open'] + df['Close/Last']) / 2
                else:
                    raise ValueError(f"Unrecognized format for file {stock}")

                stock_data[stock] = df.set_index('Date')[['Average Price']].rename(columns={'Average Price': stock})

        # Combine data into a single DataFrame using outer join to include all dates
        combined_data = pd.concat(stock_data.values(), axis=1, join='outer').sort_index()

        # Forward fill missing prices to handle non-trading days
        combined_data = combined_data.ffill()

        # Drop any remaining NaN values
        combined_data = combined_data.dropna()

        # Filter by start_date
        if start_date:
            start_date = pd.to_datetime(start_date)
            combined_data = combined_data[combined_data.index >= start_date]

        # Initialize DataFrames to track holdings and portfolio value
        holdings = pd.DataFrame(0.0, index=combined_data.index, columns=combined_data.columns.tolist() + ['Cash'])
        portfolio_value = pd.Series(0.0, index=combined_data.index)
        cumulative_invested = pd.Series(0.0, index=combined_data.index)

        # Initialize cumulative investment
        total_invested = 0.0

        # Iterate over each day to simulate daily investments
        for i, date in enumerate(combined_data.index):
            daily_investment = 1.0  # $1 invested each day
            total_invested += daily_investment
            cumulative_invested.at[date] = total_invested

            for stock, weight in portfolio.items():
                investment_amount = daily_investment * weight
                price = combined_data.at[date, stock]
                shares_bought = investment_amount / price
                if i == 0:
                    holdings.at[date, stock] = shares_bought
                else:
                    holdings.at[date, stock] = holdings.iloc[i - 1][stock] + shares_bought

            # For cash holdings (if any)
            cash_weight = 1.0 - sum(portfolio.values())
            if cash_weight > 0:
                cash_investment = daily_investment * cash_weight
                if i == 0:
                    holdings.at[date, 'Cash'] = cash_investment
                else:
                    holdings.at[date, 'Cash'] = holdings.iloc[i - 1]['Cash'] + cash_investment

        # Calculate portfolio value each day
        for date in combined_data.index:
            current_holdings = holdings.loc[date]
            current_prices = combined_data.loc[date]
            # Calculate value from stocks
            value = 0.0
            for stock in portfolio.keys():
                value += current_holdings[stock] * current_prices[stock]
            # Add cash
            if 'Cash' in current_holdings:
                value += current_holdings['Cash']
            portfolio_value.at[date] = value

        # Calculate normalized return: portfolio value divided by cumulative invested up to that day
        normalized_return = portfolio_value / cumulative_invested

        # Store results for plotting
        results[portfolio_names[portfolio_index]] = normalized_return

    # Plot results
    plt.figure(figsize=(12, 8))
    for label, values in results.items():
        plt.plot(values.index, values, label=label)

    # plt.yscale("log")
    plt.title("Cumulative Return of Portfolios Over Time")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return (Current Value / Total Invested Up to Date)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":
    # Example portfolios
    portfolios = [
        # {
        #     "btc": 1,
        # },
        # {
        #     "btc": 0.5,
        #     "qqq": 0.3,
        #     "spdr": 0.1,
        #     "tsla": 0.02,
        #     "nvda": 0.02,
        #     "goog": 0.02,
        #     "msft": 0.01,
        #     "amzn": 0.01,
        #     "aapl": 0.01,
        #     "meta": 0.01,
        # },
        {
            "qqq": 0.5,
            "btc": 0.2,
            "spdr": 0.2,
            "tsla": 0.02,
            "nvda": 0.02,
            "goog": 0.02,
            "msft": 0.01,
            "amzn": 0.01,
            "aapl": 0.01,
            "meta": 0.01,
        },
        {
            "spdr": 0.5,
            "qqq": 0.3,
            "btc": 0.1,
            "tsla": 0.02,
            "nvda": 0.02,
            "goog": 0.02,
            "msft": 0.01,
            "amzn": 0.01,
            "aapl": 0.01,
            "meta": 0.01,
        },
        {
            "spdr": 0.7,
            "qqq": 0.2,
            "btc": 0.1,
        },
        {
            "spdr": 0.9,
            "btc": 0.1,
        },
        {
            "qqq": 0.9,
            "btc": 0.1,
        },
    ]
    portfolio_names = ["QQQ Aggressive", "SPDR Aggressive", "SPDR Balanced", "SPDR Only", "QQQ Only"]

    compute_portfolio_returns(portfolios, portfolio_names=portfolio_names, start_date="2020-01-01")
