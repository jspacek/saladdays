import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys
sys.path.append('.')

def comparison_graph():
    """
     Compare the
    """
    print("________________________________ Load Balancing Tor ____________________________________\n")

    df1 = [pd.DataFrame()]
    results_file_1 = "analysis/lb_tor_bridges.csv"
    df1 = pd.read_csv(results_file_1)
    print(df1)
    n = df1.n.max()
    proxies_x = [i for i in range(0, n)]
    optimal_fraction = 100/n # optimal percent of clients per proxy

    fig, ax = plt.subplots()
    # plot the optimal load average line from proxies 1 to n
    optimal_fraction_y = [optimal_fraction] * n
    print(optimal_fraction_y)
    line1, = ax.plot(proxies_x, optimal_fraction_y,'grey',dashes=[3,3])

    # plot the average value of the least to highly loaded proxies, as % total
    assignment_averages = []
    # scale each proxy load as a fraction of the total assignments in that experiment
    # since a proxy load of 1 in 3000 assignments is not the same weight as in 1000 assignments
    print(df1.loc[:,'p1':'p60'].sum(axis = 1))

    for i in range (0,n):
        df1[df1.columns[i+3]] = df1[df1.columns[i+3]]/df1.num_tries * 100
        assignment_averages.append(df1[df1.columns[i+3]].mean())

    print(df1)
    print(assignment_averages)
    line2, = ax.plot(proxies_x, assignment_averages,'blue')

    plt.legend([line1,line2],["Optimal fraction of load","Average fraction of load"])

    ax.set(xlabel='Proxies (least loaded to highest loaded)', ylabel='% of total assignments',
           title='Load Balancing averages for Tor bridge assignment')

    plt.savefig("analysis/load_balance_tor.png")

if __name__ == '__main__':
    comparison_graph()
