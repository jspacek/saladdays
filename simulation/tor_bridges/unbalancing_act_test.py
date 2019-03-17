# -*- coding: utf-8 -*-
#
# This file is a modified version of test_email_distributor from BridgeDB,
# a Tor bridge distribution system.
#
# Original authors are:
# :authors: Isis Lovecruft 0xA3ADB67A2CDB8B35 <isis@torproject.org>
# :copyright: (c) 2013-2017 Isis Lovecruft
#             (c) 2007-2017, The Tor Project, Inc.
# :license: see included LICENSE for information

"""Tor bridge simulation in The Unbalancing Act """
import tempfile
import os
import unittest

from bridges import Bridge
from emaildistributor import EmailDistributor
from testutil import generateFakeBridges
from bridgerequest import BridgeRequestBase
from bridgerequest import EmailBridgeRequest

bridges = generateFakeBridges()
key = 'aQpeOFIj8q20s98awfoiq23rpOIjFaqpEWFoij1X'
domainmap = {
    'example.com':      'example.com',
    'dkim.example.com': 'dkim.example.com',
}
domainrules = {
    'example.com':      ['ignore_dots'],
    'dkim.example.com': ['dkim', 'ignore_dots']
}

class unbalancing_act_test(unittest.TestCase):

    def test_default_client_request(self):

        dist = EmailDistributor(key, domainmap, domainrules)
        [dist.hashring.insert(bridge) for bridge in bridges]

        # The "default" client is literally the string "default", see
        # bridgedb.bridgerequest.BridgeRequestBase.
        bridgeRequest = EmailBridgeRequest()
        bridgeRequest.client = 'default'
        bridgeRequest.isValid(True)
        bridgeRequest.generateFilters()

        self.assertTrue(bridgeRequest.ipVersion==4)
        print(bridgeRequest)

    def test_prepopulate_rings(self):
        """Calling prepopulateRings() should add one ring (IPv4) to the
        EmailDistributor.hashring.
        """

        dist = EmailDistributor(key, domainmap, domainrules)
        # dist has hashring <class 'capitalbridges.FilteredBridgeSplitter'>

        #There shouldn't be any subrings yet.
        self.assertEqual(len(dist.hashring.filterRings), 0)

        dist.prepopulateRings()

        #There should be one subring byIPv4, but the subring should be empty.
        self.assertEqual(len(dist.hashring.filterRings), 1)
        for (filtre, subring) in dist.hashring.filterRings.values():
            self.assertEqual(len(subring),0)

        # There should be an IPv4 subring:
        ringnames = dist.hashring.filterRings.keys()
        self.assertIn("IPv4", "".join([str(ringname) for ringname in ringnames]))

        [dist.hashring.insert(bridge) for bridge in bridges]
        # There should still be one subring.
        self.assertEqual(len(dist.hashring.filterRings), 1)
        # There should be some bridges in the subring
        for (filtre, subring) in dist.hashring.filterRings.values():
            self.assertGreater(len(subring), 0)

        # Ugh, the hashring code is so gross looking. :D
        subrings = dist.hashring.filterRings
        subring1 = subrings.get('IPv4')# dicts are now unordered
        print(dist.hashring)

        self.assertEqual(len(subring1), 50)

        #subring2 = subrings.values()[1][1]
        # Each subring should have roughly the same number of bridges.
        # (Having ±10 bridges in either ring, out of 500 bridges total, should
        # be so bad.)
        #self.assertApproximates(len(subring1), len(subring2), 10)

if __name__ == '__main__':
    unittest.main()
