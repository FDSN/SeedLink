.. SeedLink documentation master file


Overview
========

The goal of SeedLink v4, described in the present document, is to unify and
standardize the extensions, and to define a new, extended data format, which is
required to support the new version of Mini-SEED and extended FDSN identifiers.
SeedLink v4 is designed to be compatible with v3 -- any v3 client can connect to
v4 server (albeit missing the new features) and any v4 client can connect to v3
server.

SeedLink can be implemented in a wide range of hardware, from simple
microcontrollers used in digitizers to powerful servers in a datacentre.
Therefore the core protocol is kept very small and a number of optional
"capabilities" are defined.


History
-------

SeedLink protocol was originally created in GFZ Potsdam around 2000. Version 3,
the first widely used version of the protocol, was a result of the development
within the MEREDIAN EC project under the lead of GEOFON/GFZ Potsdam and
ORFEUS/KNMI. Later, a number of extensions to SeedLink v3 were added by GFZ
Potsdam and IRIS DMC.

.. toctree::
   :maxdepth: 2

   self
   protocol
   FDSN home <https://www.fdsn.org/>
