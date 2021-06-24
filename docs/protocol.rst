.. SeedLink documentation master file

.. _protocol:

Protocol
========

Abstract
--------
The SeedLink protocol is an application-level protocol for transferring time-series data of seismological and environmental applications in near-real time. A time series is represented as a sequence of variable length packets and is identified by a network, station, location, and channel code according to `FDSN Source Identifiers <http://docs.fdsn.org/projects/source-identifiers/en/v1.0/definition.html>`_.

SeedLink communication takes place over TCP/IP connections. The default port is TCP 18000 in case of unencrypted connection and 18500 when using TLS. Several time series can be multiplexed in a single connection.

The current document specifies version 4 of the SeedLink protocol. Earlier version numbers refer to software implementation. There is no formal specification of earlier versions of the SeedLink protocol.

Requirements
------------
The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in `RFC 2119 <https://datatracker.ietf.org/doc/html/rfc2119>`_ and `RFC 8174 <https://datatracker.ietf.org/doc/html/rfc8174>`_.

Overall Operation
-----------------
A SeedLink session starts with opening a TCP/IP connection and ends with closing the connection. The state of each session is independent of other sessions.

A session has two phases:

* Handshaking
* Data transfer

In handshaking phase, the client sends commands to the server and receives a response to those commands. In data transfer phase, the client receives a stream of SeedLink packets. No data, except the INFO command, is sent from client to server in data transfer phase.

Authentication
--------------
Users MAY be authenticated using their IP address or AUTH command. Access to some stations MAY be restricted to selected users. If a user does not have access to a station, then all commands SHOULD behave as if the station does not exist.

Data formats
------------
The payload of a SeedLink packet is usually a miniSEED record, but other formats are possible, as long as they include time and stream identification and are supported by the server and client. Format of the payload is determined by an 8-bit code in packet header. Code range (**TBD**) is reserved for frequently used formats, rest can be dynamically assigned. The list of data formats supported by the server can be requested with "INFO FORMATS". The list of data formats supported by the client can be announced with ACCEPT.

The payload of an INFO packet, which is sent in response to INFO command, is in JavaScript Object Notation (JSON) [`RFC7159 <https://datatracker.ietf.org/doc/html/rfc7159>`_] format. The payload is not influenced by ACCEPT.

Start and end time of packets
------------------------------
Each packet has a start time and an end time for its data. If a packet contains N samples, the start time is the time of the first sample and the end time is the time of the (N+1)th sample, e.g., the expected time of the first sample of the *next* packet in the same time series.

Start time of a log packet is defined as the timestamp of the first log message and end time of a log packet is defined as the timestamp of the last log message.

Sequence numbers
----------------
Each SeedLink packet has a 64-bit sequence number that identifies the position of the packet within the data stream of a station. Sequence numbers of a single station within a single server MUST be unique and monotonically increasing and SHOULD be consecutive--during the data transfer phase, each packet received by a client MUST have greater sequence number than the previous packet of the same station. By capturing the current sequence number of each requested station, a client can resume data transfer in a different session without data loss when using the same server.

The current specification has no opinion about whether sequence numbers retain meaning across separate servers.

Handshaking
-----------
When the TCP/IP connection has been established, the server MUST NOT send any data to client before receiving a command from the client. If the first command is a HTTP verb, the server MAY switch to HTTP protocol (see :ref:`websocket`).

SeedLink commands consist of an ASCII string followed by zero or more arguments separated by spaces and terminated with carriage return (<cr>, ASCII code 13) followed by linefeed (<lf>, ASCII code 10).

The server MUST also accept a single <cr> or <lf> as a command terminator. Empty command lines MUST be ignored.

All commands, except HELLO, INFO, GETCAPABILITIES, and END, respond with ``OK<cr><lf>`` if accepted by the server. If the command was not accepted, then the server MUST respond with ``ERROR`` followed by error code (:ref:`error-codes`) and optionally error description on a single line. The response MUST be terminated by ``<cr><lf>``.

In order to speed up handshaking, especially over high-latency links, the client MAY send next command before receiving response to previous one (asynchronous handshaking).

Flowchart and an example are shown below.

# .. figure::  Handshaking_flowchart.svg

Example handshaking
^^^^^^^^^^^^^^^^^^^

::

    > HELLO<cr><lf>
    < SeedLink v4.0 (MySeedLink v1.0) :: SLPROTO:4.0 CAP GETCAP<cr><lf>
    < GEOFON<cr><lf>
    > SLPROTO 4.0<cr><lf>
    < OK<cr><lf>
    > USERAGENT slinktool/4.3 (libslink/2020.046)<cr><lf>
    < OK<cr><lf>
    > GETCAPABILITIES<cr><lf>
    < SLPROTO:4.0 TIME<cr><lf>
    > ACCEPT 2 3<cr><lf>
    < OK<cr><lf>
    > STATION APE GE<cr><lf>
    < OK<cr><lf>
    > SELECT *.BH?.D.2<cr><lf>
    < OK<cr><lf>
    > DATA 0000000016FF890D<cr><lf>
    < OK<cr><lf>
    > STATION WLF GE<cr><lf>
    < OK<cr><lf>
    > SELECT *.HH?.D.3<cr><lf>
    < OK<cr><lf>
    > DATA 000000001551B73D<cr><lf>
    < OK<cr><lf>
    > END<cr><lf>

Data Transfer
-------------

When handshaking has been finished with ``END``, the server starts sending data packets. Each packet consists of a 16-byte SeedLink header, followed by variable length data. The SeedLink header consists of the letters "SE" followed by data format code (1 byte), reserved (1 byte), length of the following data (4 bytes), and sequence number (8 bytes). All numbers are binary, little-endian, and unsigned. This is illustrated by the table below.

+----------------------------------------+
| "SE"                                   |
+----------------------------------------+
| Data format code (1 byte)              |
+----------------------------------------+
| Reserved (1 byte)                      |
+----------------------------------------+
| Length of the following data (4 bytes) |
+----------------------------------------+
| Sequence number (8 bytes)              |
+----------------------------------------+
| Variable length data                   |
+----------------------------------------+

The data format code must be a single ASCII character in the range '0'..'9' or 'A'..'Z':

'0'..'1'
  Reserved.

'2'
  MiniSEED 2.x

'3'
  MiniSEED 3.x

'4'..'9'
  Reserved for standard formats.

'A'..'H'
  User-defined.

'I'
  INFO packets (JSON).

'J'..'Z'
  User-defined.

In "dial-up mode" (FETCH command), only queued data is transferred. When transferring packets of all requested stations has completed, the server MUST append ASCII string ``END`` (without <cr><lf>) to the last packet and wait for the client to close connection.

In "real-time mode" (DATA command), the data transfer phase never ends unless the client aborts the connection or a network error occurs.

.. _seedlink-commands:

Commands
--------

All of the following commands are mandatory in version 4, except when marked with {CAP:*}. In the latter case, the command is supported if the server implements indicated capability.

Where a command allows or requires additional arguments, there MUST be simple white space between the command and its argument or arguments. Simple whitespace is one or more space (ASCII code 32) or horizontal tab (ASCII code 9) characters.

HTTP verbs OPTIONS, GET, HEAD, POST, PUT, DELETE, TRACE, and CONNECT are reserved.

HELLO
    responds with a two-line message (both lines terminated with <cr><lf>). For compatibility reasons, the first line MUST start with ``SeedLink v4.0 (implementation) :: SLPROTO:4.0``, where "v4.0" is protocol version and "*implementation*" is software implementation and version, such as "MySeedLink v1.0". If the server supports earlier SeedLink protocol versions, legacy capabilities may be added to this line. The second line contains station or data center description specified in the configuration. Handshaking SHOULD start with HELLO.

SLPROTO 4.0
    Request protocol version. This command MUST be used before any other commands except HELLO.

USERAGENT program/version (library/version)
    optionally identifies client software used. Argument SHOULD follow the given format, for example ``USERAGENT slinktool/4.3 (libslink/2020.046)``. The command has no effect on functionality, but helps with logging and statistics on the server side.

BYE
    tells the server to close connection. Using this command is OPTIONAL.

AUTH *type* *argument_list* {CAP:AUTH}
    authenticates a user. Successful authentication un-hides restricted stations/streams that the user is authorized to access. Responds with "OK" if authentication was successful, "ERROR AUTH" (see :ref:`error-codes`) if authentication failed or "ERROR UNSUPPORTED" if command not supported. In any case, access to non-restricted stations is granted. Currently *type* can be either "TOKEN" or "USERPASS". Additional values may be allowed in future versions of this protocol.

ACCEPT *format_list*
    *format_list* is a space separated list of formats accepted by the client. Each element of the list is a number from 0 to 9 or a letter from A to Z. By default all formats are accepted.

GETCAPABILITIES
    returns space-separated server capabilities (:ref:`capabilities`) as a single line terminated by <cr><lf>.

STATION *station_pattern* *network_pattern*
    requests given station(s) from the server.

    Supported wildcards are "\*" and "?". Any following SELECT, DATA, or FETCH commands apply to all stations that match the given pattern, including stations that are added to the server in the future.

    If a station matches multiple STATION commands, then the first one takes effect.

    The number of station requests MAY be limited by the server to prevent excessive resource consumption.

    STATION may return ERROR for any implementation-defined reason. In this case, SELECT, DATA and FETCH commands up to next STATION must be ignored.

END
    ends handshaking and switches to data transfer phase.

SELECT *location_pattern*.*channel_pattern*[.*type_pattern*[.*format_pattern*]]
    requests streams that match given pattern. By default (if SELECT is omitted), all streams are requested. Streams that are not in ACCEPTed format are excluded.

    Supported wildcards are "\*" and "?". If the argument starts with "!", then streams matching the pattern are excluded.

    * *location_pattern* and *channel_pattern* are mandatory.

    * *location_pattern* can be empty, matching empty location code in the data.

    * *type_pattern* is one single character specifying the desired type of record. Currently it may be one of "D", "E", "C", "O", "T", or "L" for data, event, calibration, opaque, timing, or log records. Default is "\*".

    SELECT can be used multiple times per station. A stream is selected if it matches any SELECT without "!" and does **not** match any SELECT with "!".

    The number of SELECT commands per station MAY be limited by the server to prevent excessive resource consumption.

    The following example SELECT statements are valid::

        > SELECT .BHZ
        > SELECT .BH?
        > Select .BHZ
        > SELECT 0.BHZ

    The following are not valid, and a server MUST respond with "ERROR ARGUMENTS"::

        > SELECT BHZ

DATA [*seq*]
    sets the starting sequence number of station(s) that match previous STATION command. If *seq* is -1 or omitted, then transfer starts from the next available packet. If the sequence number is in the future or too distant past, then it MAY be considered invalid by the server and -1 MAY be used instead. If a packet with given sequence number is not available, then the sequence number of the next available packet MUST be used by the server. Transfer of packets continues in real-time when all queued data of the station(s) have been transferred ("real-time mode").

DATA *seq* *start_time* [*end_time*] {CAP:TIME}
    requests a time window from station(s) that match previous STATION command. Only packets that satisfy the following conditions are considered:

    #. packet.seq >= *seq* (if *seq* != -1)
    #. packet.start_time < *end_time* (if *end_time* given)
    #. packet.end_time > *start_time*

    *start_time* and *end_time* should be in the form of 6 or 7 decimal numbers separated by commas: year,month,day,hour,minute,second,nanosecond. Nanoseconds are optional. Note that there MUST be *no* space between each number.

    Using *seq*, it is possible to resume transfer of a time window in a new session.

FETCH [*seq*]
    same as DATA [*seq*], except transfer of packets stops when all queued data of the station(s) have been transferred ("dial-up mode").

FETCH *seq* *start_time* [*end_time*] {CAP:TIME}
    same as DATA *seq* *start_time* [*end_time*], except transfer of packets stops when all queued data of the station(s) have been transferred ("dial-up mode").

INFO *item* [*station_code* *network_code*]
    requests information about the server in JSON format. *item* should be one of the following: ID, DATATYPES, STATIONS, STREAMS, CONNECTIONS. *station_code* and *network_code* can contain wildcards "\*" and "?", default is "\*". The JSON schema is shown in Appendix B. INFO is allowed during both handshaking and data transfer phases. The response MUST be in the form of one single packet containing complete JSON document. If the expected size of the document would exceed an implementation-defined limit, a JSON document with error description MUST be sent instead (that is, no ERROR response or incomplete JSON may be sent by the server).

    The amount of info available depends on the server implementation and configuration. "INFO ID" is recommended for implementing keep-alive functionality.

.. _error-codes:

Error codes
-----------
UNSUPPORTED
    command not recognized or not supported

UNEXPECTED
    command not expected

LIMIT
    limit exceeded (e.g., too many STATION or SELECT commands were used)

ARGUMENTS
    incorrect arguments

AUTH
    authentication failed (invalid user, password or token were provided)

.. _capabilities:

Capabilities
------------
The current specification defines the following capabilities:

SLPROTO:#.#
    SeedLink protocol version.

AUTH\:*type*
    authentication *type* supported.

TIME
    time windows supported with DATA and FETCH.

.. _websocket:

Appendix A. WebSocket operation
-------------------------------
SeedLink can be used over WebSocket `RFC 6455 <https://tools.ietf.org/html/rfc6455>` if this is supported by the server.

Each command from client to server MUST be sent as a Unicode message consisting of 1 frame. Line terminator <cr><lf> is OPTIONAL.

Each command response from server to client MUST be sent as a Unicode message consisting of 1 frame. Each line MUST be terminated by <cr><lf>.

Each packet from server to client (including INFO packets) MUST be sent as a binary message consisting of 1 frame.

The final ``END`` (when "dial-up mode" is used) MUST be sent as a binary message.

Depending on the maximum frame size of a particular WebSocket implementation, the maximum size of SeedLink packet encapsulated in WebSocket frame may be smaller than 2^32+7 bytes, which is the theoretical maximum packet size supported by SeedLink.

Appendix B. JSON schema
-----------------------

**TBD**


Appendix C. Differences between SeedLink 3 and SeedLink 4
---------------------------------------------------------
SeedLink 4 protocol is not compatible with SeedLink 3 clients. However, SeedLink 4 is enabled by using the "SLPROTO 4.0" command, which is not known to SeedLink 3 clients, so a SeedLink 4 server can also support SeedLink 3 protocol.

.. |w| unicode:: 0x26A0

The following new features were added in SeedLink 4. Incompatible changes, where SeedLink 3 format or syntax is interpreted differently in SeedLink 4, are marked with |w|.

* New packet header, multiple payload formats and variable length are supported. |w|
* There is no explicit maximum length of network, station, location, and channel codes.
* Wildcards "\*" and "?" allowed in network, station, location, and channel codes.
* Sequence numbers are now 64-bit. |w|
* SELECT requires explicit location and channel codes, separated by a dot. |w|
* Optional end-time and sequence number (-1) with DATA and FETCH.
* SLPROTO, USERAGENT, AUTH, ACCEPT and GETCAPABILITIES commands added.
* INFO DATATYPES.
* INFO format is JSON instead of XML. |w|
* Extended ERROR response.
* Asynchronous handshaking.

The following commands present in some older versions of the SeedLink protocol were removed in SeedLink 4:

* CAT (same functionality provided by "INFO STATIONS").
* TIME (same functionality provided by extended DATA syntax).
* BATCH (same functionality provided by asynchronous handshaking).
* INFO GAPS (incompatible with unsorted data packets, performance issues).
* INFO CAPABILITIES (same functionality provided by GETCAPABILITIES).
* CAPABILITIES (similar functionality provided by SLPROTO).
