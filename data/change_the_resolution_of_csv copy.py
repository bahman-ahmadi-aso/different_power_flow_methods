import sys,os,time,numpy as np,pandas as pd,matplotlib.pyplot as plt

DU='oneyear' # 'oneyear' or 'oneday'
active_power_time_series = pd.read_csv("data/time_series/active_power_scaled_"+DU+".csv",index_col=0,parse_dates=True)
reactive_power_time_series = pd.read_csv("data/time_series/reactive_power_scaled_"+DU+".csv",index_col=0,parse_dates=True)

name="windturbine_"   #"active_power_scaled_"   #"reactive_power_scaled_"
# Load your data into a DataFrame, assuming the datetime column is named 'datetime' and the data column is named 'data'
df = pd.read_csv("data/time_series/"+name+DU+".csv", parse_dates=['date_time'], index_col=['date_time'])

# Resample the data to 15-minute frequency and interpolate missing values
df_15min = df.resample('15T').mean().interpolate(method='time')

# Save the resampled data to a new CSV file
df_15min.to_csv("data/time_series/"+name+DU+"15min.csv")




a=1

