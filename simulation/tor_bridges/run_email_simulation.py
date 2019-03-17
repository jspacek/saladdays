# -*- coding: utf-8 ; test-case-name: bridgedb.test.test_Main -*-
#
# This file is part of BridgeDB, a Tor bridge distribution system.
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
from emaildistributor import EmailDistributor
from testutil import generateFakeBridges
import capitalbridges

key = 'aQpeOFIj8q20s98awfoiq23rpOIjFaqpEWFoij1X'
domainmap = {
    'example.com':      'example.com',
    'dkim.example.com': 'dkim.example.com',
}
domainrules = {
    'example.com':      ['ignore_dots'],
    'dkim.example.com': ['dkim', 'ignore_dots']
}

def createBridgeRings(key):
    """
    Create the bridge distributors (only the email)
    """
    # Create a BridgeSplitter to assign the bridges to the different distributors.
    bridgesplitter_hashring = capitalbridges.BridgeSplitter(b'aQpeOFIj8q20s98awfoiq23rpOIjFaqpEWFoij1X')
    #<class 'capitalbridges.BridgeSplitter'>
    print("Created bridgesplitter_hashring: %r" % bridgesplitter_hashring)

    # Create ring parameters.
    ringParams = capitalbridges.BridgeRingParameters(needPorts=[(443, 1)],
                                              needFlags=[("Stable", 1)])

    emailDistributor = EmailDistributor(key, domainmap, domainrules)
    bridgesplitter_hashring.addRing(emailDistributor.hashring, "email", 2)

    return bridgesplitter_hashring, emailDistributor

def run():
    """
    This is BridgeDB's main entry point and main runtime loop.
    """
    (bridgesplitter_hashring, emailDistributor) = createBridgeRings(key)
    print("Bridges loaded: %d" % len(bridgesplitter_hashring))

    emailDistributor.prepopulateRings() # create default rings
    bridges = generateFakeBridges()
    [bridgesplitter_hashring.insert(bridge) for bridge in bridges]
    print("Bridges loaded: %d" % len(bridgesplitter_hashring))

    # Dump bridge pool assignments to disk.
    #writeAssignments(hashring, state.ASSIGNMENTS_FILE)

    # Make a client request for a bridge

def writeAssignments(hashring, filename):
    """Dump bridge distributor assignments to disk.

    :type hashring: A :class:`~bridgedb.Bridges.BridgeSplitter`
    :ivar hashring: A class which takes an HMAC key and splits bridges
        into their hashring assignments.
    :param str filename: The filename to write the assignments to.
    """
    print("Dumping pool assignments to file: '%s'" % filename)

    try:
        with open(filename, 'a') as fh:
            fh.write("bridge-pool-assignment %s\n" %
                     time.strftime("%Y-%m-%d %H:%M:%S"))
            hashring.dumpAssignments(fh)
    except IOError:
        logging.info("I/O error while writing assignments to: '%s'" % filename)

if __name__ == '__main__':
    run()
