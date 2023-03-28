import math

def american_option_price(S, X, T, r, sigma, n, option_type):
    """
    Calculates the price of an American option using the Cox-Ross-Rubinstein model.
    
    Arguments:
    S -- Current price of the underlying asset
    X -- Strike price of the option
    T -- Time to expiration (in years)
    r -- Risk-free interest rate
    sigma -- Volatility of the underlying asset
    n -- Number of time steps
    option_type -- 'call' or 'put'
    
    Returns:
    The price of the American option.
    """
    
    # Calculate parameters
    delta_t = T / n
    u = math.exp(sigma * math.sqrt(delta_t))
    d = 1 / u
    p = (math.exp(r * delta_t) - d) / (u - d)
    
    # Initialize the option values at expiration
    option_values = [0] * (n + 1)
    for i in range(n + 1):
        if option_type == 'call':
            option_values[i] = max(S * (u ** (n - i)) * (d ** i) - X, 0)
        elif option_type == 'put':
            option_values[i] = max(X - S * (u ** (n - i)) * (d ** i), 0)
    
    # Perform backward induction
    for j in range(n - 1, -1, -1):
        for i in range(j + 1):
            if option_type == 'call':
                early_exercise = max(S * (u ** (j - i)) * (d ** i) - X, 0)
            elif option_type == 'put':
                early_exercise = max(X - S * (u ** (j - i)) * (d ** i), 0)
            
            discounted_option_value = math.exp(-r * delta_t) * (p * option_values[i] + (1 - p) * option_values[i + 1])
            option_values[i] = max(early_exercise, discounted_option_value)
    
    return option_values[0]


S = 100  # Current price of the underlying asset
X = 105  # Strike price of the option
T = 1  # Time to expiration in years
r = 0.05  # Risk-free interest rate
sigma = 0.3  # Volatility of the underlying asset
n = 100  # Number of time steps
option_type = 'call'  # 'call' or 'put'

option_price = american_option_price(S, X, T, r, sigma, n, option_type)
print("Option price:", option_price)