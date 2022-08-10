#!/usr/bin/env python
# coding: utf-8

# ### For Beta calucualtion initialization with pandas, numpy and scipy
import json
import pandas as pd
from scipy.stats import mstats
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--excel-file', required=True,
                    dest='excel_file', help='Absolute path for input Excel file')
parser.add_argument('--as-of-date', required=True,
                    dest='as_of_date', help='ISO date eg. 2021-10-31')
parser.add_argument('--window', dest='window', default='1y',
                    help='Window eg. 1y (default: %(default)s)')
parser.add_argument('--frequency', required=True, dest='frequency', default='daily',
                    help='Period Frequency eg. daily, weekly, monthly, quarterly, bi-weekly (default: %(default)s)', choices=("daily", "weekly", "monthly", "quarterly", "bi-weekly"))
args = parser.parse_args()
if not vars(args):
    parser.print_help()
    parser.exit(0)


winsorize_limits = [0.05, 0.05]
excel_file_path = args.excel_file
as_of_date = args.as_of_date
window = args.window
frequency = args.frequency
if not os.path.isfile(excel_file_path):
    raise FileNotFoundError(excel_file_path)


# ### pandas read Excel file: `task2_stock_data.xlsx`
print('Reading Excel file from location[`%s`]...' % excel_file_path)
df = pd.read_excel(excel_file_path)


def using_mstats_df(df):
    return df.apply(using_mstats, axis=0)


def using_mstats(s):
    return mstats.winsorize(s, limits=winsorize_limits)


df.set_index('date', inplace=True)
grouped = df.groupby(level='date')

# ### applying winsorize
print('Applying winsorize Left tails [%s%%] and Right tails [%s%%]...' % (
    winsorize_limits[0]*100, winsorize_limits[1]*100), sep=' ')
df = grouped.apply(using_mstats_df)
df.reset_index(inplace=True)
print('DONE')


AS_OF_DATE = pd.to_datetime(as_of_date)
WINDOW = window
FREQUENCY = frequency
year_ago = (AS_OF_DATE - pd.DateOffset(years=int(WINDOW[0]))).to_pydatetime()

frequency_dict = {"daily": "D", "weekly": "W", "yearly": "Y",
                  "monthly": "M", 'bi-weekly': 'SM', 'quarterly': 'Q'}
print('\nUser Inputs:')
print("\tDate range From: %s, To: %s" %
      (year_ago.strftime('%m/%d/%Y'), AS_OF_DATE.strftime('%m/%d/%Y')))
print("\tFrequency: %s" % FREQUENCY)
print("\tWindow: %s" % WINDOW)
input_df = df[(df['date'] >= year_ago) & (df['date'] < AS_OF_DATE)]

print('\nResampling to `%s` frequency values...' % FREQUENCY)
input_df = input_df.resample(frequency_dict[FREQUENCY], on='date').mean()
log_returns = np.log(input_df/input_df.shift())
covariance = log_returns.cov()
variance = log_returns["SPY US Equity"].var()
beta_df = covariance.loc["SPY US Equity"]/variance
beta_df_dict = beta_df.round(4).fillna("N/A").to_dict()
# beta_df_dict.pop('SPY US Equity')
output_file_name = 'beta_calc_%s-%s-as_of-%s.json' % (
    window, frequency, as_of_date)
print('Writing `%s` json file...' % output_file_name)
with open(output_file_name, 'w') as f:
    f.write(json.dumps(beta_df_dict, indent=4))
