import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MaxNLocator

import sys
sys.path.append('.')

def comparison_graph():
    """
     Compare the
    """
    print("________________________________ Load Balancing Needle ____________________________________\n")

    df1 = [pd.DataFrame()]
    results_file_1 = "analysis/results_100_1_steps_no_repeat_10_n_past_enum_lb.csv"
    df1 = pd.read_csv(results_file_1)
    #print(df1)
    n = df1.n.max()
    proxies_x = [i+1 for i in range(0, n)]
    print(proxies_x)

    optimal_fraction = 100/n # optimal percent of clients per proxy
    print("We want to have an optimal proportion of clients per %d proxies, that is %f percent." % (n,optimal_fraction))
    fig, ax = plt.subplots()
    # plot the optimal load average line from proxies 1 to n
    optimal_fraction_y = [optimal_fraction] * n
    #print("give x values for the optimal fraction to draw a straight line")
    #print(optimal_fraction_y)
    line1, = ax.plot(proxies_x, optimal_fraction_y,'pink')

    # plot the average value of the least to highly loaded proxies, as % total
    assignment_averages = []
    # scale each proxy load as a fraction of the total assignments in that experiment
    # since a proxy load of 1 in 3000 assignments is not the same weight as a proxy load of 1 in 1000 assignments
    for i in range (0,n):
        df1[df1.columns[i+3]] = df1[df1.columns[i+3]]/df1.num_tries * 100
        assignment_averages.append(df1[df1.columns[i+3]].mean())
    #assert(df1.loc[:,'p1':'p60'].sum(axis = 1),100)
    print(df1)
    print(assignment_averages)
    line2, = ax.plot(proxies_x, assignment_averages,'--bo')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_xlim([1,n])
    #ax.set_ylim([1,(2*optimal_fraction)])
    y_title = 'Optimal proportion of load = 100 / %d percent' % n
    plt.legend([line1,line2],[y_title,"Average fraction of load"])
    plt.grid(True)
    ax.set(xlabel='%d proxies (sorted by least loaded to highest loaded)'%n, ylabel='Percentage of total assignments')

    plt.savefig("analysis/load_balance_needle_results_100_1_steps_no_repeat_10_n_past_enum.png")

if __name__ == '__main__':
    comparison_graph()
