.. SeedLink documentation master file

.. _versions:

Versions
========

4.0
---

*2020*

The goal of SeedLink v4 is to unify and standardize the extensions
added since v3.1, and to define new protocol extensions to allow for
support of a new version of miniSEED and FDSN identifiers.

SeedLink v4 is designed to be compatible with v3 -- any v3 client can
connect to v4 server (albeit missing the new features) and any v4
client can connect to v3 server.

Planned new features include:

* Support for multiple type data types beyond miniSEED 2.
* Variable record length.
* Network and station wildcards.
* Extended DATA/FETCH/TIME commands to make time-windowed requests resumable.
* Extended time resolution (up to nanoseconds).
* User ID and token-based authentication with SSL support for accessing restricted data.

3.1
---

*2010*

* Add BATCH command to disable otherwise requires respones to modifier
  commands.  Reduces negotiation messages, speeding up negotiations.

3.0
---

*~2003*

2.93
----

* Allow packet time to be included with a stream sequence number.

2.92
----

* Add TIME command for time windowed request
* Add INFO requests

2.5
---

* Support multi-station protocol mode
