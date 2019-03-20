import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.append('.')

def comparison_graph():
    """
     Compare the results for trials on needle and Tor Bridge algorithms
     TODO: uniform random, maybe POD
    """
    print("________________________________ Needle and Tor Bridge Comparison ____________________________________\n")

    df1 = [pd.DataFrame()]
    df2 = [pd.DataFrame()]
    df3 = [pd.DataFrame()]

    results_file_1 = "analysis/comparison_needle.csv"
    results_file_2 = "analysis/comparison_tor.csv"
    results_file_3 = "analysis/comparison_CCP.csv"
    results_file_4 = "analysis/comparison_half_window_no_repeat.csv"
    results_file_5 = "analysis/comparison_half_window_repeat_4_times.csv"
    results_file_6 = "analysis/comparison_quarter_window_no_repeat.csv"

    df1 = pd.read_csv(results_file_1)
    df2 = pd.read_csv(results_file_2)
    df3 = pd.read_csv(results_file_3)
    df4 = pd.read_csv(results_file_4)
    df5 = pd.read_csv(results_file_5)
    df6 = pd.read_csv(results_file_6)

    fig, ax = plt.subplots()
    line1, = ax.plot(df1.n, df1.sample_mean,'purple',dashes=[3,3])
    line4, = ax.plot(df4.n, df4.sample_mean,'magenta')
    line5, = ax.plot(df5.n, df5.sample_mean,'violet')
    line6, = ax.plot(df6.n, df6.sample_mean,'pink')
    line3, = ax.plot(df3.n, df3.sample_mean,'grey')
    line2, = ax.plot(df2.n, df2.sample_mean,'green',dashes=[2,2])

    plt.legend([line1,line4,line5,line6,line2,line3],["Needle Algorithm: no windows", "Needle Algorithm: half window, no repeat", "Needle Algorithm: half window, repeat 4 times", "Needle Algorithm: quarter window, no repeat","Tor Bridges: 10 Bridge Rings", "Coupon Collector nH_n"])

    ax.set(xlabel='Number of Proxies', ylabel='Average number of Assignments before Enumeration',
           title='Average number of proxy assignments to find all proxies')
    ax.grid()
    #plt.show()
    #graphnamepng = "analysis/archive/proxy_exposure_by_client_assignment%d_trials_%d_proxies_%d_victim_list.png" % (util.NUM_TRIALS, util.NUM_PROXIES, util.VICTIM_LIST)
    plt.savefig("analysis/comparison_graph.png")

if __name__ == '__main__':
    comparison_graph()
