# -*- coding: utf-8 ; test-case-name: bridgedb.test.test_email_distributor -*-
#
# This file is part of BridgeDB, a Tor bridge distribution system.
#
# :authors: Nick Mathewson
#           Isis Lovecruft 0xA3ADB67A2CDB8B35 <isis@torproject.org>
#           Matthew Finkel 0x017DD169EA793BE2 <sysrqb@torproject.org>
# :copyright: (c) 2013-2017, Isis Lovecruft
#             (c) 2013-2017, Matthew Finkel
#             (c) 2007-2017, The Tor Project, Inc.
# :license: see LICENSE for licensing information

"""
.. py:module:: bridgedb.distributors.email.distributor
    :synopsis: A Distributor which hands out Bridges via an email interface.

bridgedb.distributors.email.autoresponder
============================

A :class:`~bridgedb.distribute.Distributor` which hands out :class:`bridges
<bridgedb.bridges.Bridge>` to clients via an email interface.

.. inheritance-diagram:: IgnoreEmail TooSoonEmail EmailRequestedHelp EmailRequestedKey EmailDistributor
    :parts: 1
"""

import logging
import time

#import storage

from capitalbridges import BridgeRing
from capitalbridges import FilteredBridgeSplitter
from crypto import getHMAC
from crypto import getHMACFunc
from distribute import Distributor
from filters import byFilters
from filters import byIPv4
from filters import byIPv6
from parse import addr

class EmailDistributor(Distributor):
    """Object that hands out bridges based on the email address of an incoming
    request and the current time period.

    :type hashring: :class:`~bridgedb.Bridges.BridgeRing`
    :ivar hashring: A hashring to hold all the bridges we hand out.
    """
    def __init__(self, key, domainmap, domainrules,
                 answerParameters=None, whitelist=None):
        """Create a bridge distributor which uses email.

        :type emailHmac: callable
        :param emailHmac: An hmac function used to order email addresses
            within a ring. See :func:`~bridgedb.crypto.getHMACFunc`.
        :param dict domainmap: A map from lowercase domains that we support
            mail from to their canonical forms. See `EMAIL_DOMAIN_MAP` option
            in `bridgedb.conf`.
        :param domainrules: DOCDOC
        :param answerParameters: DOCDOC
        :type whitelist: dict or ``None``
        :param whitelist: A dictionary that maps whitelisted email addresses
            to GnuPG fingerprints.
        """
        super(EmailDistributor, self).__init__(key)

        self.domainmap = domainmap
        self.domainrules = domainrules
        self.whitelist = whitelist or dict()
        self.answerParameters = answerParameters

        key1 = getHMAC(key, "Map-Addresses-To-Ring")
        key2 = getHMAC(key, "Order-Bridges-In-Ring")

        self.emailHmac = getHMACFunc(key1, hex=False)
        #XXX cache options not implemented
        self.hashring = FilteredBridgeSplitter(key2, max_cached_rings=5)

        self.name = "Email"

    def bridgesPerResponse(self, hashring=None):
        return 3

    def getBridges(self, bridgeRequest, interval, clock=None):
        """Return a list of bridges to give to a user.

        .. hint:: All checks on the email address (which should be stored in
            the ``bridgeRequest.client`` attribute), such as checks for
            whitelisting and canonicalization of domain name, are done in
            :meth:`bridgedb.distributors.email.autoresponder.getMailTo` and
            :meth:`bridgedb.distributors.email.autoresponder.SMTPAutoresponder.runChecks`.

        :type bridgeRequest:
            :class:`~bridgedb.distributors.email.request.EmailBridgeRequest`
        :param bridgeRequest: A
            :class:`~bridgedb.bridgerequest.BridgeRequestBase` with the
            :data:`~bridgedb.bridgerequest.BridgeRequestBase.client` attribute
            set to a string containing the client's full, canonicalized email
            address.
        :type interval: str
        :param interval: The time period when we got this request. This can be
            any string, so long as it changes with every period.
        :type clock: :api:`twisted.internet.task.Clock`
        :param clock: If given, use the clock to ask what time it is, rather
            than :api:`time.time`. This should likely only be used for
            testing.
        :rtype: :any:`list` or ``None``
        :returns: A list of :class:`~bridgedb.bridges.Bridges` for the
            ``bridgeRequest.client``, if allowed.  Otherwise, returns ``None``.
        """

        print("Attempting to get bridges for %s..." % bridgeRequest.client)

        pos = self.emailHmac("<%s>%s" % (interval, bridgeRequest.client))
        print("Position in ring is %d"% pos)
        ring = None
        filtres = frozenset(bridgeRequest.filters)
        if filtres in self.hashring.filterRings:
            print("Cache hit %s" % filtres)
            _, ring = self.hashring.filterRings[filtres]
        else:
            print("Cache miss %s" % filtres)
            key = getHMAC(self.key, "Order-Bridges-In-Ring")
            ring = BridgeRing(key, self.answerParameters)
            self.hashring.addRing(ring, filtres, byFilters(filtres),
                                  populate_from=self.hashring.bridges)

        returnNum = self.bridgesPerResponse(ring)
        result = ring.getBridges(pos, returnNum, filterBySubnet=False)

        return result

    def prepopulateRings(self):
        """Prepopulate this distributor's hashrings and subhashrings with
        bridges.
        """
        print("Prepopulating %s distributor hashrings..." % self.name)

        #for filterFn in [byIPv4, byIPv6]:
            #ruleset = frozenset([filterFn])
            #key = getHMAC(self.key, "Order-Bridges-In-Ring")
            #ring = BridgeRing(key, self.answerParameters)
            #self.hashring.addRing(ring, ruleset, byFilters([filterFn]),
                                #  populate_from=self.hashring.bridges)

        # Only v4 for this simulation
        key = getHMAC(self.key, "Order-Bridges-In-Ring")
        ring = BridgeRing(key, self.answerParameters)
        self.hashring.addRing(ring, 'IPv4', None,
                            populate_from=self.hashring.bridges)

        print("Bridges allotted for %s distribution: %d"
                     % (self.name, len(self.hashring)))
