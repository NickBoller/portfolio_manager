import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries
from scipy import stats

api_key = 'URRP3SWEDY8WA3M4'

ts = TimeSeries(key=api_key, output_format='pandas')

print("Enter a ticker symbol: ")
stock = input()

print("Pick a Time frame in months (recommended = 60)")
time_frame = int(input())

gspc_data, gspc_meta_data = ts.get_monthly_adjusted(symbol='^GSPC')
data, meta_data = ts.get_monthly_adjusted(symbol=stock)

stock_df = pd.DataFrame(data['5. adjusted close'][:time_frame])
gspc_df = pd.DataFrame(gspc_data['5. adjusted close'][:time_frame])

# Calculates beta using the slope of a simple linear regression
def calc_beta(dependent_var, independent_var):
	monthly_prices = pd.concat([dependent_var, independent_var], axis=1)
	monthly_prices.columns = ['stock', '^GSPC']
	monthly_returns = monthly_prices.pct_change(1)
	clean_monthly_returns = monthly_returns.dropna(axis=0)

	gspc = clean_monthly_returns['^GSPC']
	stock = clean_monthly_returns['stock']

	slope, intercept, r_value, p_value, std_err = stats.linregress(gspc, stock)
	return slope

beta = calc_beta(stock_df, gspc_df)

# Use the 10 year U.S. treasury bond as the risk free rate
risk_free_rate_data, risk_free_rate_meta_data = ts.get_monthly_adjusted(symbol='^TNX')
ten_year_treasury_bond = risk_free_rate_data['5. adjusted close'][0]

# Take the average return of the S&P500 
# timeline: how many months back to calculate the % change
def calc_expected_market_return(timeline):
	# Gets the data from present as far back as timeline then reverses the array
	gspc_monthly = pd.DataFrame(gspc_data['5. adjusted close'][timeline-1::-1])
	monthly_change = gspc_monthly.pct_change()
	clean_monthly_change = monthly_change.dropna()

	avg_change = 0
	for x in clean_monthly_change['5. adjusted close']:
		avg_change += x

	years = timeline / 12.0
	return avg_change / years * 100

# Gets average return of past 10 years
expected_market_return = calc_expected_market_return(int(len(gspc_data['5. adjusted close'])/2))

def capm(rf, b, rm):
	return rf + (b*(rm-rf))
print("=======================================================")
print("beta is: ", beta)
print("risk free rate is: ", ten_year_treasury_bond)
print("expected market return is: ", expected_market_return)
print("capm is: ", capm(ten_year_treasury_bond, beta, expected_market_return))
print("=======================================================")

