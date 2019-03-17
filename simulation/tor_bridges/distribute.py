# -*- coding: utf-8 ; test-case-name: bridgedb.test.test_distribute ; -*-
#_____________________________________________________________________________
#
# This file is part of BridgeDB, a Tor bridge distribution system.
#
# :authors: Isis Lovecruft 0xA3ADB67A2CDB8B35 <isis@torproject.org>
#           please also see AUTHORS file
# :copyright: (c) 2013-2017, Isis Lovecruft
#             (c) 2007-2017, The Tor Project, Inc.
# :license: see LICENSE for licensing information
#_____________________________________________________________________________


"""Classes for creating bridge distribution systems.
"""
import math

from zope import interface
from zope.interface import Attribute
from zope.interface import implements

from interfaces import IName
from interfaces import Named


class IDistribute(IName):
    """An interface specification for a system which distributes bridges."""

    _bridgesPerResponseMin = Attribute(
        ("The minimum number of bridges to distribute (if possible), per "
         "client request."))
    _bridgesPerResponseMax = Attribute(
        ("The maximum number of bridges to distribute (if possible), per "
         "client request."))
    _hashringLevelMin = Attribute(
        ("The bare minimum number of bridges which should be in a hashring. "
         "If there less bridges than this, then the implementer of "
         "IDistribute should only distribute _bridgesPerResponseMin number "
         "of bridges, per client request."))
    _hashringLevelMax = Attribute(
        ("The number of bridges which should be in a hashring for the "
         "implementer of IDistribute to distribute _bridgesPerResponseMax "
         "number of bridges, per client request."))

    hashring = Attribute(
        ("An implementer of ``bridgedb.hashring.IHashring`` which stores the "
         "entirety of bridges allocated to this ``Distributor`` by the "
         "BridgeDB.  This ``Distributor`` is only capable of distributing "
         "these bridges to its clients, and these bridges are only "
         "distributable by this ``Distributor``."))

    key = Attribute(
        ("A master key which is used to HMAC bridge and client data into "
         "this Distributor's **hashring** and its subhashrings."))

    def __str__():
        """Get a string representation of this Distributor's ``name``."""

    def bridgesPerResponse(hashring):
        """Get the current number of bridges to return in a response."""

    def getBridges(bridgeRequest):
        """Get bridges based on a client's **bridgeRequest**."""


class Distributor(Named):
    """A :class:`Distributor` distributes bridges to clients.

    Inherit from me to create a new type of ``Distributor``.
    """
    #implements(IDistribute)

    _bridgesPerResponseMin = 1
    _bridgesPerResponseMax = 3
    _hashringLevelMin = 20
    _hashringLevelMax = 100

    def __init__(self, key=None):
        """Create a new bridge Distributor.

        :param key: A master key for this Distributor. This is used to HMAC
            bridge and client data in order to arrange them into hashring
            structures.
        """
        super(Distributor, self).__init__()
        self._hashring = None
        self.key = key

    def __str__(self):
        """Get a string representation of this ``Distributor``'s ``name``.

        :rtype: str
        :returns: This ``Distributor``'s ``name`` attribute.
        """
        return self.name

    @property
    def hashring(self):
        """Get this Distributor's main hashring, which holds all bridges
        allocated to this Distributor.

        :rtype: :class:`~bridgedb.hashring.Hashring`.
        :returns: An implementer of :interface:`~bridgedb.hashring.IHashring`.
        """
        return self._hashring

    @hashring.setter
    def hashring(self, ring):
        """Set this Distributor's main hashring.

        :type ring: :class:`~bridgedb.hashring.Hashring`
        :param ring: An implementer of :interface:`~bridgedb.hashring.IHashring`.
        :raises TypeError: if the **ring** does not implement the
            :interface:`~bridgedb.hashring.IHashring` interface.
        """
        # if not IHashring.providedBy(ring):
        #     raise TypeError("%r doesn't implement the IHashring interface." % ring)

        self._hashring = ring

    @hashring.deleter
    def hashring(self):
        """Clear this Distributor's hashring."""
        if self.hashring:
            self.hashring.clear()

    @property
    def name(self):
        """Get the name of this Distributor.

        :rtype: str
        :returns: A string which identifies this :class:`Distributor`.
        """
        return self._name

    @name.setter
    def name(self, name):
        """Set a **name** for identifying this Distributor.

        This is used to identify the distributor in the logs; the **name**
        doesn't necessarily need to be unique. The hashrings created for this
        distributor will be named after this distributor's name, and any
        subhashrings of each of those hashrings will also carry that name.

        >>> from bridgedb.distribute import Distributor
        >>> dist = Distributor()
        >>> dist.name = 'Excellent Distributor'
        >>> dist.name
        'Excellent Distributor'

        :param str name: A name for this distributor.
        """
        self._name = name

        try:
            self.hashring.distributor = name
        except AttributeError:
            logging.debug(("Couldn't set distributor attribute for %s "
                           "Distributor's hashring." % name))

    def bridgesPerResponse(self, hashring=None):
        """Get the current number of bridge to distribute in response to a
        client's request for bridges.
        """
        if hashring is None:
            hashring = self.hashring

        if len(hashring) < self._hashringLevelMin:
            n = self._bridgesPerResponseMin
        elif self._hashringLevelMin <= len(hashring) < self._hashringLevelMax:
            n = int(math.ceil(
                (self._bridgesPerResponseMin + self._bridgesPerResponseMax) / 2.0))
        elif self._hashringLevelMax <= len(hashring):
            n = self._bridgesPerResponseMax

        logging.debug("Returning %d bridges from ring of len: %d" %
                      (n, len(hashring)))

        return n

    def getBridges(self, bridgeRequest):
        """Get some bridges in response to a client's **bridgeRequest**.

        :type bridgeRequest: :class:`~bridgedb.bridgerequest.BridgeRequestBase`
        :param bridgeRequest: A client's request for bridges, including some
            information on the client making the request, whether they asked
            for IPv4 or IPv6 bridges, which type of
            :class:`~bridgedb.bridges.PluggableTransport` they wanted, etc.
        """
        # XXX generalise the getBridges() method
