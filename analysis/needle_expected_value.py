import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.append('.')
from core import util

def needle_expected_value():
    """
     Compare the sample mean against n^2
    """
    print("________________________________ Needle Algorithm E[X] ____________________________________\n")

    df = [pd.DataFrame()]
    results_file = "analysis/compiled_results.csv"
    df = pd.read_csv(results_file)
    #print(df)
    n = df.n
    sample_mean = df.sample_mean
    n_squared = df.n_squared
    one_half_n_squared = df.one_half_n_squared
    two_n_squared = df.two_n_squared
    two_half_n_squared = df.two_half_n_squared
    three_n_squared = df.three_n_squared

    fig, ax = plt.subplots()
    line1, = ax.plot(n, n_squared,'pink',dashes=[5,5])
    line2, = ax.plot(n, one_half_n_squared,'plum',dashes=[4,4])
    line3, = ax.plot(n, two_n_squared,'orchid',dashes=[3, 3])
    line4, = ax.plot(n, two_half_n_squared,'purple',dashes=[2, 2])
    line5, = ax.plot(n, three_n_squared,'indigo',dashes=[1, 1])
    plt.fill_between(n, n_squared, one_half_n_squared, color='lavender', alpha='0.5', label="blah")
    plt.fill_between(n, one_half_n_squared, two_n_squared, color='plum', alpha='0.5')
    plt.fill_between(n, two_n_squared, two_half_n_squared, color='orchid', alpha='0.5')
    plt.fill_between(n, two_half_n_squared, three_n_squared, color='purple', alpha='0.5')
    plt.fill_between(n, three_n_squared, 0, color='ivory', alpha='0.5')
    mean, = ax.plot(n, sample_mean,'black')

    plt.legend([mean,line1,line2,line3,line4,line5],["Experiment E[X]","n^2", "1.5n^2", "2n^2", "2.5n^2", "3n^2"])

    #plt.legend(handles=[fill1], labels=["n 2"])

    ax.set(xlabel='n', ylabel='E[X] proxy assignments',
           title='Average number of proxy assignments to find all proxies')
    ax.grid()
    #plt.show()
    #graphnamepng = "analysis/archive/proxy_exposure_by_client_assignment%d_trials_%d_proxies_%d_victim_list.png" % (util.NUM_TRIALS, util.NUM_PROXIES, util.VICTIM_LIST)
    plt.savefig("analysis/needle_expected_value.png")
    #plt.savefig(graphnamesvg, format='svg', dpi=1200)

if __name__ == '__main__':
    needle_expected_value()
