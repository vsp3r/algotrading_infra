def calculate_profit(initial_investment, apy_percentage):
    # Constants
    DAYS_IN_WEEK = 7
    DAYS_IN_MONTH = 30
    COMPOUNDING_FREQUENCY = 365  # Assuming compounding is done daily

    # Calculate daily interest rate
    daily_interest_rate = (1 + apy_percentage / 100) ** (1 / COMPOUNDING_FREQUENCY) - 1

    # Calculate profit for the first week
    weekly_profit = initial_investment
    for _ in range(DAYS_IN_WEEK):
        daily_profit = weekly_profit * daily_interest_rate
        weekly_profit += daily_profit

    # Calculate profit for the first month
    monthly_profit = initial_investment
    for _ in range(DAYS_IN_MONTH):
        daily_profit = monthly_profit * daily_interest_rate
        monthly_profit += daily_profit

    return weekly_profit - initial_investment, monthly_profit - initial_investment


initial_investment = 10000  # Example initial investment amount
apy_percentage = 800  # Example APY percentage

weekly_profit, monthly_profit = calculate_profit(initial_investment, apy_percentage)
print("Profit for the first week:", weekly_profit)
print("Profit for the first month:", monthly_profit)
