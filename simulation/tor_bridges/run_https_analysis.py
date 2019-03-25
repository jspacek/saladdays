# -*- coding: utf-8 ; test-case-name: bridgedb.test.test_Main -*-
#
#
# This file is modified from BridgeDB, a Tor bridge distribution system, for
# The Unbalancing Act simulation, the original authors are:
#
# :authors: please see the AUTHORS file for attributions
# :copyright: (c) 2013-2017, Isis Lovecruft
#             (c) 2013-2017, Matthew Finkel
#             (c) 2007-2017, Nick Mathewson
#             (c) 2007-2017, The Tor Project, Inc.
# :license: see LICENSE for licensing information

"""This module sets up BridgeDB and starts the servers running."""

import crypto
import util
import collections
import math
import pandas as pd
from bridges import Bridge
from httpsdistributor import HTTPSDistributor
from testutil import generateFakeBridges
from testutil import randomValidIPv4String
import capitalbridges
from bridgerequest import BridgeRequestBase
from httpsrequest import HTTPSBridgeRequest

key = b'aQpeOFIj8q20s98awfoiq23rpOIjFaqpEWFoij1X'
domainmap = {
    'example.com':      'example.com',
    'dkim.example.com': 'dkim.example.com',
}
domainrules = {
    'example.com':      ['ignore_dots'],
    'dkim.example.com': ['dkim', 'ignore_dots']
}

"""
This simulation duplicates the description from httpsDistributor prepopulateRings

        As an example, if BridgeDB was configured with ``N_IP_CLUSTERS=4`` and
        ``PROXY_LIST_FILES=["open-socks-proxies.txt"]``, then the total number
        of subhashrings is five — four for the "clusters", and one for the
        :data:`proxies`. Thus, the resulting hashring-subhashring structure
        would look like:

        +------------------+---------------------------------------------------+-------------+
        |                  |               Directly connecting users           | Tor / known |
        |                  |                                                   | proxy users |
        +------------------+------------+------------+------------+------------+-------------+
        | Clusters         | Cluster-1  | Cluster-2  | Cluster-3  | Cluster-4  | Cluster-5   |
        +==================+============+============+============+============+=============+
        | Subhashrings     |            |            |            |            |             |
        | (total, assigned)| (5,1)      | (5,2)      | (5,3)      | (5,4)      | (5,5)       |
        +------------------+------------+------------+------------+------------+-------------+
        | Filtered         | (5,1)-IPv4 | (5,2)-IPv4 | (5,3)-IPv4 | (5,4)-IPv4 | (5,5)-IPv4  |
        | Subhashrings     |            |            |            |            |             |
        | bBy requested    +------------+------------+------------+------------+-------------+
        | bridge type)     | (5,1)-IPv6 | (5,2)-IPv6 | (5,3)-IPv6 | (5,4)-IPv6 | (5,5)-IPv6  |
        |                  |            |            |            |            |             |
        +------------------+------------+------------+------------+------------+-------------+

        The "filtered subhashrings" are essentially filtered copies of their
        respective subhashring, such that they only contain bridges which
        support IPv4 or IPv6, respectively.  Additionally, the contents of
        ``(5,1)-IPv4`` and ``(5,1)-IPv6`` sets are *not* disjoint.

        Thus, in this example, we end up with **10 total subhashrings**.
"""
def createBridgeRings():
    """
    Create the https bridge distributor
    """
    # Create a BridgeSplitter to assign the bridges to the different distributors.
    bridgesplitter_hashring = capitalbridges.BridgeSplitter(key)
    #<class 'capitalbridges.BridgeSplitter'>
    print("Created bridgesplitter_hashring: %r" % bridgesplitter_hashring)

    # Create ring parameters.
    ringParams = capitalbridges.BridgeRingParameters(needPorts=[(443, 1)],
                                              needFlags=[("Stable", 1)])

    # TODO Do we need a proxy list here?
    proxyList = []
    httpsDistributor = HTTPSDistributor(
        4, # like the eample in httpsdistributor
        crypto.getHMAC(key, b"HTTPS-IP-Dist-Key"),
        proxyList,
        answerParameters=ringParams)
    HTTPS_SHARE = 10
    bridgesplitter_hashring.addRing(httpsDistributor.hashring, "https", HTTPS_SHARE)

    return bridgesplitter_hashring, httpsDistributor

def run(n):
    """
    This is BridgeDB's main entry point and main runtime loop.
    """
    filename = "analysis/results_tor_bridges_%d_n.csv" % n
    flb_name = "analysis/results_tor_bridges_%d_n_lb.csv" % n

    f = open(filename,"w+")
    flb = open(flb_name,"w+")

    (bridgesplitter_hashring, httpsDistributor) = createBridgeRings()
    print("Bridges loaded: %d" % len(bridgesplitter_hashring))

    httpsDistributor.prepopulateRings() # create default rings
    bridges = generateFakeBridges(n) # generate n bridges
    print(len(bridges))
    [bridgesplitter_hashring.insert(bridge) for bridge in bridges]
    print("Bridges loaded: %d" % len(bridgesplitter_hashring))

    print("Bridges allotted for %s distribution: %d"
                 % (httpsDistributor.name, len(httpsDistributor.hashring)))

    print("\tNum bridges:\tFilter set:")
    for (ringname, (filterFn, subring)) in httpsDistributor.hashring.filterRings.items():
        filterSet = ' '.join(httpsDistributor.hashring.extractFilterNames(ringname))
        print("\t%2d bridges\t%s" % (len(subring), filterSet))

    print("Total subrings for %s: %d"
                 % (httpsDistributor.name, len(httpsDistributor.hashring.filterRings)))


    # Run trials
    bridge = collections.namedtuple('bridge', 'index load num_in_draw trial')
    df_all = pd.DataFrame(columns=bridge._fields)
    trials = 100
    n=n-1 # always this discrepancy from tor bridges
    # Make multiple client requests, record how many hits to the same bridge (load)
    for current_trial in range(0,trials):
        bridges = [bridge(index=i,load=0,num_in_draw=0,trial=current_trial) for i in range(n)]
        # fill up the data frame with default bridges
        df = pd.DataFrame(bridges, columns=bridge._fields)
        enum_bridges = []
        i = 0
        index = 0
        num_tries = 0
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! len((enum_bridges)) %d" % len(enum_bridges))
        while (len(enum_bridges) < n):
            #print("LENGTH IS %d" %len(enum_bridges))
            client_request = randomClientRequest()
            responses = httpsDistributor.getBridges(client_request, 1)
            for i in range(0, len(responses)):
                address = int(responses[i].address)
                print("WHAT IS ADDRESS IS IT IN ENUM")
                print(address)
                print(enum_bridges)
                print("what is n %d" %n)
                if (address not in enum_bridges):
                    enum_bridges.append(address)
                    # store this bridge at the current index in the dataframe
                    df.at[index,'index'] = address
                    df.at[index,'load'] = df.at[index,'load'] + 1
                    index = index + 1
                else:
                    # find the bridge index
                    #print("collision")
                    bridge_index = enum_bridges.index(address)
                    #print("bridge index %d" %bridge_index)
                    # increment the load of this bridge
                    df.at[bridge_index,'load'] = df.at[bridge_index,'load'] + 1

                num_tries = num_tries + 1
        # Calculate the "optimal load"
        optimal_load = num_tries/n
        print("optimal_load = %d / %d = %d" %(num_tries, n, optimal_load) )
        # Sum up the optimal load deviation with a number for all above and another for all below
        # so that min bins don't cancel out max bins
        #min_optimal = (df.load < optimal_load).sum()
        sorted_loads = df.load.values.sort()
        loads = ",".join(str(x) for x in df.load.values)
        print(loads)
        flb.write("%d,%d,%d,%s\r\n" % (n,num_tries,optimal_load,loads))

        df_all = df_all.append(df, ignore_index=True)

    print(df_all)
    df_all_group = df_all.groupby('trial', as_index=False, sort=False)['load'].sum()
    print(df_all_group.load.describe())
    mean_samples = df_all_group.load.mean()

    print("*****************     Sample mean = %d n = %d *********************" % (mean_samples, n))
    #print(df_all)
    # The max load in each trial (not the max load over all trials)
    #df_all_max = df_all.groupby('trial', as_index=False, sort=False)['load'].max()
    #print("maximum loads average")
    #print(df_all_max)

    # nH_n Formula using Euler Mascheroni Constant
    H_n = (math.log(n) + 0.5772156649) + 1/(2*n)
    #print("H_n %f" % H_n)
    nH_n = n * H_n
    print("Calculated mean nH_n = %f" % (nH_n))
    # ln n / ln ln n
    ur_max_load = math.log(n) / (math.log(math.log(n)))
    #print("Calculated max load for uniform random %f where m=n" % ur_max_load)
    # ln ln n / ln 2
    pod_max_load = math.log(math.log(n))/math.log(2)
    #print("Calculated max load for power of 2 choice %f where m=n" % pod_max_load)
    # O(ln ln n) + m/n
    pod_max_load_m_sgr_n = math.log(math.log(n)) + mean_samples/n
    #print("Calculated max load for power of 2 choice %f where m >> n" % pod_max_load_m_sgr_n)

    max = df_all_group.load.max()
    min = df_all_group.load.min()
    std = df_all_group.load.std()
    print("%d,%d,%d,%d,%d,%d\r\n" % (n,trials,mean_samples,max,min,std))
    f.write("%d,%d,%d,%d,%d,%d\r\n" % (n,trials,mean_samples,max,min,std))

    f.flush()
    f.close()

def randomClientRequest():
    bridgeRequest = HTTPSBridgeRequest(addClientCountryCode=False)
    bridgeRequest.client = randomValidIPv4String()
    bridgeRequest.isValid(True)
    bridgeRequest.generateFilters()
    return bridgeRequest

if __name__ == '__main__':
    n = 61 # because of frozenset (probably) bridges are cached somewhere
    # so don't run this in a loop
    run(n)
