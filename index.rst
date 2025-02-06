.. SeedLink documentation master file


Overview
========

SeedLink is a protocol designed for the transmission of seismological,
and related, data in the miniSEED format.  The protocol is TCP-based
and has been used operationally in a wide variety of environments for
many years.

The core protocol is designed to be very small with a number of
optional capabilities defined for enhanced use.  This allows for
operation in a wide range of hardware and environments, from simple
microcontrollers used in digitizers to powerful servers in a datacentre.

See :ref:`protocol` for details.

History
-------

SeedLink protocol was originally created in GFZ Potsdam around 2000. Version 3,
the first widely used version of the protocol, was a result of the development
within the MEREDIAN EC project under the lead of GEOFON/GFZ Potsdam and
ORFEUS/KNMI. Later, a number of extensions to SeedLink v3 were added by GFZ
Potsdam and IRIS DMC.

See the :ref:`versions` for a history of protocol changes.

.. toctree::
   :maxdepth: 2

   self
   protocol
   versions
   software
   FDSN home <https://www.fdsn.org/>
