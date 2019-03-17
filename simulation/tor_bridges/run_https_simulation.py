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
from bridges import Bridge
from httpsdistributor import HTTPSDistributor
from testutil import generateFakeBridges
from testutil import randomValidIPv4String
import capitalbridges
from bridgerequest import BridgeRequestBase
from httpsrequest import HTTPSBridgeRequest

key = 'aQpeOFIj8q20s98awfoiq23rpOIjFaqpEWFoij1X'
key_bytes = b'aQpeOFIj8q20s98awfoiq23rpOIjFaqpEWFoij1X'
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
    bridgesplitter_hashring = capitalbridges.BridgeSplitter(key_bytes)
    #<class 'capitalbridges.BridgeSplitter'>
    print("Created bridgesplitter_hashring: %r" % bridgesplitter_hashring)

    # Create ring parameters.
    ringParams = capitalbridges.BridgeRingParameters(needPorts=[(443, 1)],
                                              needFlags=[("Stable", 1)])

    # TODO open-socks-proxies.txt
    proxyList = []
    httpsDistributor = HTTPSDistributor(
        4, # like the eample in httpsdistributor
        crypto.getHMAC(key_bytes, b"HTTPS-IP-Dist-Key"),
        proxyList,
        answerParameters=ringParams)
    HTTPS_SHARE = 10
    bridgesplitter_hashring.addRing(httpsDistributor.hashring, "https", HTTPS_SHARE)

    return bridgesplitter_hashring, httpsDistributor

def run():
    """
    This is BridgeDB's main entry point and main runtime loop.
    """
    (bridgesplitter_hashring, httpsDistributor) = createBridgeRings()
    print("Bridges loaded: %d" % len(bridgesplitter_hashring))

    httpsDistributor.prepopulateRings() # create default rings
    bridges = generateFakeBridges()
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


    enum_bridges = [] # an array of tuples (bridge, load)
    # Make multiple client requests, record how many hits to the same bridge (load)
    for i in range(1, 1200):
        client_request = randomClientRequest()
        responses = httpsDistributor.getBridges(client_request, 1)

        for i in range(0, len(responses)):
            print(responses[i])
            if (responses[i] not in enum_bridges):
                enum_bridges.append(responses[i])
            else:
                enum_bridges[responses[i]] = enum_bridges[responses[i]] + 1

    for i in range(0, len(enum_bridges)):
        print(enum_bridges[i])

    print(len(enum_bridges))

def randomClientRequest():
    bridgeRequest = HTTPSBridgeRequest(addClientCountryCode=False)
    bridgeRequest.client = randomValidIPv4String()
    bridgeRequest.isValid(True)
    bridgeRequest.generateFilters()
    return bridgeRequest

if __name__ == '__main__':
    run()
