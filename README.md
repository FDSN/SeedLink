
# SeedLink protocol specification

This specification defines the SeedLink protocol for near real-time data stream transmition used primarily for seismological networks.

This repository contains the source of the documentation and serves as a coordination point for additions and changes to the specification.

The documentation may be found at: https://docs.fdsn.org/projects/seedlink/

## Documentation source organization

* The `draft` branch contains the latest draft documentation
  * All changes are first applied to the `draft` branch and then merged with main for releases
* Specification releases are tags in the form `v.#.#.##` on the `main` branch, following a release:
  * The version and release values in conf.py, rendered by sphinx, are set using the tag value

## Versioning

The versioning scheme used in tags uses the following form: `vMAJOR.MINOR.DOC` where:
* `MAJOR.MINOR` are the version of the specification, and
* `DOC` is the version of this documentation.

The `DOC` version changes when the documentation has been updated with clarifications, typos,
etc. and does not imply any functional change to the specification.
