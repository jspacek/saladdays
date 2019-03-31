import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.append('.')
from core import util

def needle_expected_value():
    """
     Compare the sample mean against upper and lower bounds in a 5 giant step
    """
    print("________________________________ Needle Algorithm E[X] ____________________________________\n")

    df = [pd.DataFrame()]
    results_file = "analysis/needle_bounds_gs_5.csv"
    df = pd.read_csv(results_file)
    #print(df)
    n = df.n
    sample_mean = df.sample_mean
    upper_bound = df.upper_bound
    lower_bound = df.lower_bound

    fig, ax = plt.subplots()
    line1, = ax.plot(n, upper_bound,'blue',dashes=[2, 2])
    line2, = ax.plot(n, lower_bound,'purple',dashes=[4,4])

    plt.fill_between(n, upper_bound, lower_bound, color='orchid', alpha='0.5')
    mean, = ax.plot(n, sample_mean,'black')

    plt.legend([line1,mean,line2],["Upper Bound", "Experiment E[X]","Lower Bound"])

    ax.set(xlabel='n', ylabel='E[X] proxy assignments',
           title='Bounds on the average number of proxy assignments to find all proxies in giant step = 5')
    ax.grid()
    #plt.show()
    plt.savefig("analysis/needle_expected_value_giant_step.png")

if __name__ == '__main__':
    needle_expected_value()
