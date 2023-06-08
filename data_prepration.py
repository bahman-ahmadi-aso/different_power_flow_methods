import sys,os,time,numpy as np,pandas as pd,matplotlib.pyplot as plt


for j in range(100):
    df = pd.read_csv("data/time_series/reactive_power_scaled_oneyear15min.csv")
    # loop through the columns corresponding to the nodes
    for i in range(1, 34):
        # generate random numbers between 0.6 and 1.4 with the same length as the column
        rand_nums = np.random.uniform(low=0.6, high=1.4, size=len(df))
        # replace the values in the column with the random numbers
        df.iloc[:, i] = rand_nums

    # save the modified dataframe to a new csv file
    df.to_csv('data/time_series/reactive_power_scaled_oneyear15min_'+str(j+1)+'th_commit.csv', index=False)

a=1


