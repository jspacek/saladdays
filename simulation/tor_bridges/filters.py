# -*- coding: utf-8 ; test-case-name: bridgedb.test.test_filters ; -*-
#_____________________________________________________________________________
#
# This file is part of BridgeDB, a Tor bridge distribution system.
#
# :authors: Nick Mathewson <nickm@torproject.org>
#           Isis Lovecruft 0xA3ADB67A2CDB8B35 <isis@torproject.org>
#           please also see AUTHORS file
# :copyright: (c) 2007-2017, The Tor Project, Inc.
#             (c) 2013-2017, Isis Lovecruft
# :license: see LICENSE for licensing information
#_____________________________________________________________________________

"""Functions for filtering :class:`Bridges <bridgedb.bridges.Bridge>`."""

from ipaddr import IPv4Address
from ipaddr import IPv6Address

from parse.addr import isIPv


_cache = {}


def bySubring(hmac, assigned, total):
    """Create a filter function which filters for only the bridges which fall
    into the same **assigned** subhashring (based on the results of an **hmac**
    function).

    :type hmac: callable
    :param hmac: An HMAC function, i.e. as returned from
        :func:`bridgedb.crypto.getHMACFunc`.
    :param int assigned: The subring number that we wish to draw bridges from.
        For example, if a user is assigned to subring 2of3 based on their IP
        address, then this function should only return bridges which would
        also be assigned to subring 2of3.
    :param int total: The total number of subrings.
    :rtype: callable
    :returns: A filter function for :class:`Bridges <bridgedb.bridges.Bridge>`.
    """
    logging.debug(("Creating a filter for assigning bridges to subhashring "
                   "%s-of-%s...") % (assigned, total))

    name = "-".join([str(hmac("")[:8]).encode('hex'),
                     str(assigned), "of", str(total)])
    try:
        return _cache[name]
    except KeyError:
        def _bySubring(bridge):
            position = int(hmac(bridge.identity)[:8], 16)
            which = (position % total) + 1
            return True if which == assigned else False
        # The `description` attribute must contain an `=`, or else
        # dumpAssignments() will not work correctly.
        setattr(_bySubring, "description", "ring=%d" % assigned)
        _bySubring.__name__ = ("bySubring%sof%s" % (assigned, total))
        _bySubring.name = name
        _cache[name] = _bySubring
        return _bySubring

def byFilters(filtres):
    """Returns a filter which filters by multiple **filtres**.

    :param list filtres: A list (or other iterable) of callables which some
        :class:`Bridges <bridgedb.bridges.Bridge>` should be filtered
        according to.
    :rtype: callable
    :returns: A filter function for :class:`Bridges <bridgedb.bridges.Bridge>`.
    """
    name = []
    for filtre in filtres:
        name.extend(filtre.name.split(" "))
    name = " ".join(set(name))

    try:
        return _cache[name]
    except KeyError:
        def _byFilters(bridge):
            results = [f(bridge) for f in filtres]
            if False in results:
                return False
            return True
        setattr(_byFilters, "description",
                " ".join([getattr(f, "description", "") for f in filtres]))
        _byFilters.name = name
        _cache[name] = _byFilters
        return _byFilters

def byIPv(ipVersion=None):
    """Return ``True`` if at least one of the **bridge**'s addresses has the
    specified **ipVersion**.

    :param int ipVersion: Either ``4`` or ``6``.
    """
    # only IPv4 in this simulation
    def _byIPv(bridge):
        """Determine if the **bridge** has an IPv{0} address.

        :type bridge: :class:`bridgedb.bridges.Bridge`
        :param bridge: A bridge to filter.
        :rtype: bool
        :returns: ``True`` if the **bridge** has an address with the
            correct IP version; ``False`` otherwise.
        """
        if isIPv(ipVersion, bridge.address):
            return True
        else:
            for address, port, version in bridge.allVanillaAddresses:
                if version == ipVersion or isIPv(ipVersion, address):
                    return True
        return False
    setattr(_byIPv, "description", "ip=%d" % 4)
    _byIPv.__name__ = "byIPv%d()" % 4
    #_byIPv.func_doc = _byIPv.func_doc.format(4)
    name = "ipv%d" % 4
    _byIPv.name = name
    _cache[name] = _byIPv
    return _byIPv

byIPv4 = byIPv(4)
byIPv6 = byIPv(6)

def byTransport(methodname=None, ipVersion=None):
    """Returns a filter function for a :class:`~bridgedb.bridges.Bridge`.

    The returned filter function should be called on a
    :class:`~bridgedb.bridges.Bridge`.  It returns ``True`` if the
    :class:`~bridgedb.bridges.Bridge` has a
    :class:`~bridgedb.bridges.PluggableTransport` such that:

    1. The :data:`methodname <bridgedb.bridges.PluggableTransport.methodname>`
       matches **methodname**, and,

    2. The :attr:`bridgedb.bridges.PluggableTransport.address.version`
       equals the **ipVersion**.

    :param str methodname: A Pluggable Transport
        :data:`~bridgedb.bridges.PluggableTransport.methodname`.
    :param int ipVersion: Either ``4`` or ``6``. The IP version that the
        ``Bridge``'s ``PluggableTransport``
        :attr:`address <bridgedb.bridges.PluggableTransport.address>` should
        have.
    :rtype: callable
    :returns: A filter function for :class:`Bridges <bridgedb.bridges.Bridge>`.
    """
    # the only filter method in this simulation is by IPv4
    ipVersion = 4
    return byIPv(ipVersion)
