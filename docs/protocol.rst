.. SeedLink documentation master file

.. _protocol:

Protocol
========

A SeedLink session starts with opening the TCP/IP connection and ends with
closing the TCP/IP connection. During the session, the following steps are
performed:

* Opening the connection
* Handshaking
* Transferring SeedLink packets

.. |4| unicode:: 0x2463

New features of SeedLink v4 are marked with |4| in the following text.
Features related to a certain capability (other than SLPROTO:4.0) are marked
with {CAP:*capability*}.

Handshaking
-----------

When the TCP/IP connection has been established the server will wait for the
client to start handshaking without initially sending any data to the client.
During handshaking, the client sends SeedLink commands to the server. The
commands are used to set the connection into particular mode, setup stream
selectors, request a packet sequence number to start with and eventually start
data transmission. SeedLink commands consist of an ASCII string followed by
zero or several arguments separated by spaces and terminated with carriage
return (<cr>, ASCII code 13) followed by an optional linefeed
(<lf>, ASCII code 10).

Commands can be divided into two categories: "action commands" and "modifier
commands". Action commands perform a function such as starting data transfer.
Modifier commands are used to specialize or modify the function performed by
the action commands that follow. Some commands can work as both action
commands or modifier commands, depending on whether "uni-station" or
"multi-station" mode is used.

When a server receives a modifier command, it normally responds with the ASCII
string "OK" followed by a carriage return and a line feed to acknowledge that
the command has been accepted. If the command was not recognized by the server
or has invalid parameters, then the ASCII string "ERROR" is sent as a response
to the client followed by a carriage return and a line feed. A second line with
error description will follow if {CAP:EXTREPLY} is supported and enabled by
client. Unless asynchronous handshaking {CAP:ASYNC} is explicitly supported by
the server, the client should not send any further commands before it has
received a response to the previous modifier command.

In case of batch handshaking {CAP:BATCH}, triggered by the BATCH command,
responses to STATION, SELECT, DATA, FETCH, TIME and CAPABILITIES commands will
not be sent. In this case, errors will be silently ignored. Using BATCH is
generally not recommended, unless talking to a known server implementation.

The client should check server's response to the BATCH command itself as
usual -- if the response is ERROR, then batch mode is not supported by the
server and normal handshaking should be used further on.

If a network error or timeout occurs the client should close the connection and
start a new session. Data transmission is started when the server receives the
commands DATA, FETCH, TIME or END as described in section
:ref:`seedlink-commands`. Once the data transfer has been started, no more
commands, except INFO, should be sent to the server. Flowchart of
handshaking is shown in :ref:`seedlink-handshaking`.

.. _seedlink-handshaking:

.. figure::  Handshaking_flowchart.svg

   Handshaking flowchart

Example v3 handshaking
^^^^^^^^^^^^^^^^^^^^^^

::

    > HELLO\r\n
    < SeedLink v4.0 (MySeedLink v1.0) :: SLPROTO:4.0 CAP GETCAP\r\n
    < GEOFON\r\n
    > BATCH\r\n
    < ERROR\r\n
    > STATION APE GE\r\n
    < OK\r\n
    > SELECT 00BH?.D\r\n
    < OK\r\n
    > DATA FF890D\r\n
    < OK\r\n
    > SATION WLF GE\r\n
    < OK\r\n
    > SELECT 00HH?.D\r\n
    < OK\r\n
    > DATA 51B73D\r\n
    < OK\r\n
    > END\r\n

Example v4 handshaking (async)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    > HELLO\r\n
    < SeedLink v4.0 (MySeedLink v1.0) :: SLPROTO:4.0 CAP GETCAP\r\n
    < GEOFON\r\n
    > USERAGENT slinktool/4.3 (libslink/2020.046)\r\n
    < OK\r\n
    > GETCAPABILITIES\r\n
    < SLPROTO:4.0 WEBSOCKET:13 ASYNC MULTISTATION TIME INFO:ID INFO:CAPABILITIES INFO:STATIONS INFO:STREAMS\r\n
    > ACCEPT 51 50\r\n
    < OK\r\n
    > STATION APE GE\r\n
    > SELECT 00:BH?.D\r\n
    < OK\r\n
    < OK\r\n
    > DATA 0000000016FF890D\r\n
    > STATION WLF GE\r\n
    > SELECT 00:HH?.D\r\n
    < OK\r\n
    < OK\r\n
    < OK\r\n
    > DATA 000000001551B73D\r\n
    < OK\r\n
    > END\r\n

Data Transfer
-------------

When handshaking has been completed, the server starts sending data packets. In
legacy data mode, each packet consists of 8-byte SeedLink header followed by a
512-byte miniSEED record. The SeedLink header is an ASCII string consisting of
the letters "SL" followed by a six-digit hexadecimal packet sequence number.

In extended data mode |4|, enabled by the ACCEPT command, each packet consists
of 16-byte SeedLink header, followed by variable length data. The SeedLink
header consists of the letters "SE" followed by data format code (1 byte),
reserved byte, binary, 32-bit, little-endian length of the following data (4
bytes), and binary, 64-bit, little-endian sequence number (8 bytes). This is
illustrated by the table below.

+-------------------------------------------+----------------------------------------------------------------------+
| Standard format                           | Extended format                                                      |
+===========================================+======================================================================+
| “SL”                                      | “SE”                                                                 |
+-------------------------------------------+----------------------------------------------------------------------+
|                                           | Data format code (1 byte)                                            |
+-------------------------------------------+----------------------------------------------------------------------+
|                                           | Reserved byte (1 byte)                                               |
+-------------------------------------------+----------------------------------------------------------------------+
|                                           | Binary length (4 bytes / 32 bits), little-endian                     |
+-------------------------------------------+----------------------------------------------------------------------+
| ASCII sequence number (6 bytes / 24 bits) | Binary sequence number (8 bytes / 64 bits), little-endian            |
+-------------------------------------------+----------------------------------------------------------------------+
| 512 bytes data                            | Variable length data                                                 |
+-------------------------------------------+----------------------------------------------------------------------+

The following data format codes have been reserved:

50 (ASCII "2")
  MiniSEED 2.x

51 (ASCII "3")
  MiniSEED 3.x
  
73 (ASCII "I")
  INFO packets (XML or JSON?)

In order to receive data in those formats, 50, 51 and/or 73 must be used as
argument(s) to the ACCESS command.

A SeedLink server that receives data from another SeedLink server may re-assign
sequence numbers for technical reasons. It is generally not possible to use the
same sequence numbers when communicating with alternative servers.

Sequence numbers may contain gaps (eg., if some packets have been lost or
filtered out).  In this case the first packet is not necessarily the one
requested, but the nearest packet (not older than requested) that matches the
selectors. Sequence numbers wrap around when the maximum sequence number (eg.,
2^24-1 in legacy data mode) has been reached.

When the server has sent all available data, the server sends new data as soon
as it arrives ("real-time mode") or appends ASCII string "END" to the last
packet and waits for the client to close connection ("dial-up mode"). Due to
signature "SL" or "SE", A SeedLink packet can never start with "END", so there
is no ambiguity.

.. _seedlink-commands:

Commands
--------

HELLO
    responds with a two-line message (both lines terminated with <cr><lf>). For compatibility reasons, the first line should be structured as ``SeedLink v4.0 (implementation) :: SLPROTO:4.0 CAP GETCAP``, where "v4.0" is protocol version and "implementation" is software implementation and version, such as "MySeedLink v1.0". The second line contains station or data center description specified in the configuration. Handshaking typically starts with HELLO, but using HELLO is not mandatory.
    
USERAGENT program/version (library/version)
    optionally identifies client software used. Argument is free string, but it is recommended to use given format, for example ``USERAGENT slinktool/4.3 (libslink/2020.046)``. The command has no effect on functionality, but helps with logging and statistics on the server side.

CAT
    shows the station list. Used mainly for testing a SeedLink server with "telnet".

BYE
    closes the connection. Used mainly for testing a SeedLink server with "telnet".

BATCH
    supresses output of STATION, SELECT, DATA, FETCH, TIME and CAPABILITIES commands (deprecated).

AUTH type argument_list {CAP:AUTH} |4|
    authentication as an alternative to IP-based ACL. Successful authentication un-hides restricted stations/streams that the user is authorized to access. Responds with "OK" if authentication was successful, "ERROR" if authentication failed or command not supported. In any case, access to non-restricted stations is granted. Type can be TOKEN or USERPASS, possibly more in the future.

ACCEPT format_list | * |4|
    enables extended data mode. format_list is a space separated list of formats accepted by the client. Each element of the list is a number from 1 to 255. ``ACCEPT *`` tells the server that all formats are accepted.

ENABLE capability |4|
    enables additional capabilities of the server. Only EXTREPLY can be enabled in the current version of the protocol.

CAPABILITIES capability_list {CAP:CAP}
    specifies capabilities supported by the client. Equivalent of ENABLE when EXTREPLY is included, other capabilities have no effect. This command is included for backwards compatibility.

GETCAPABILITIES {CAP:GETCAP}
    returns space-separated server capabilities as a single line.

STATION station_code [network_code] {CAP:MULTISTATION}
    enables multi-station mode, which is used to transfer data of multiple stations over a single TCP connection. The STATION command, followed by SELECT (optional) and FETCH, DATA or TIME commands is repeated for each station and the handshaking is finished with END.
    
    In multi-station mode, all stations should use either DATA, FETCH or TIME. Mixing different commands results in undefined behaviour.

    If the network code is omitted, default network code is used for backwards compatibility.

    Some servers may support wildcards "\*" and "?" in station_code and network_code {CAP:NSWILDCARD}. In this case, the following SELECT, DATA, FETCH and TIME command will be implicitly repeated for all matching stations that are not requested explicitly, including stations that are added to the server in future. Sequence number must not be used unless the server supports {CAP:NSWILDCARDSEQ}.
    
    Number of stations and wildcards that a client can request may be limited to prevent denial of service.
    
    STATION responds with "OK" if the command was accepted, "ERROR" oterwise. "OK" does not imply that the station already exists or is known to the server. "ERROR" may have several reasons, including:
    
    * multi-station mode not supported;
    * station not found;
    * limits exceeded.
    
END {CAP:MULTISTATION}
    end of handshaking in multi-station mode. No explicit response is sent.

SELECT [pattern]
    when used without pattern, all selectors are canceled. Otherwise, the pattern is a positive selector to enable matching miniSEED stream transfer. The pattern can be used as well as a negative selector with a leading "!" to prevent the transfer of some miniSEED streams. Only one selector can be used in a single SELECT request. A SeedLink packet is sent to the client if it matches any positive selector and doesn’t match any negative selectors.

    Format of the pattern is LL:CCC.T |4|, where LL is location, CCC is channel, and T is type (one of DECOTL for data, event, calibration, blockette, timing, and log records). "LL", ".T", and "LL:CCC." can be omitted, meaning "any". If the location code is exactly 2 characters and channel code is exactly 3 characters, then ":" should be omitted, because it may not be supported by all servers. Supported wildcards are "\*" and "?". "-" stands for space (eg., "--" can be used to denote empty location code), but may not be supported by all servers. Number of selectors may be limited to prevent denial-of-service.

    SELECT responds with "OK" on success, "ERROR" otherwise.

DATA [seq [begin_time [end_time]]]
    enables real-time mode and optionally sets the sequence number and time window {CAP:TIME}. In uni-station mode, data transfer is started immediately, in multi-station mode, the response is "OK" or "ERROR". If sequence number is -1 |4| or omitted, then transfer starts from the next available packet. If time window is specified, any packets that are outside of the window are filtered out. end_time |4| may not be supported by older servers.

    Apart from the special value -1 |4|, sequence number can be 64-bit (16 hexadecimal numbers) |4| or 24-bit (6 hexadecimal numbers). The latter is equivalent to largest available 64-bit sequence number with matching 24 least significant bits.

    Time should be in the form of 6 or 7 |4| decimal numbers separated by commas: year,month,day,hour,minute,second,nanosecond. Nanoseconds |4| may not be supported by older servers.

FETCH [seq [begin_time [end_time]]]
    works like DATA but enables dial-up mode instead of real-time mode.

TIME [begin_time [end_time]] {CAP:TIME}
    equivalent of "DATA -1 begin_time end_time".

INFO level {CAP:INFO}
    requests an INFO packet containing XML data embedded in a miniSEED log record. level should be one of the following: ID, CAPABILITIES, STATIONS, STREAMS, GAPS, CONNECTIONS, ALL. The XML document conforms to the Document Type Definition (DTD) shown in section ???. The amount of info available depends on the configuration of the SeedLink server.

GET arg {CAP:WEBSOCKET}
    HTTP GET, when used as the very first command, switches to WebSocket encapsulation. Argument is ignored.
    
STARTTLS {CAP:STARTTLS}
    when used as the very first command, switches to TLS. Note: STARTTLS is incompatible with WebSocket; secure WebSocket can be used only with dedicated TLS port.


Capabilities
------------

SeedLink 3.x defined 2 sets of capabilities. The original GFZ version defined
"dialup", "multistation", "window-extraction", "info\:id", "info\:capabilities",
"info\:stations", "info\:streams", "info\:gaps", "info\:connections" and
"info\:all" (lower-case), which were listed by the INFO CAPABILITIES command.

The IRIS DMC version defined "SLPROTO", "CAP", "EXTREPLY", "NSWILDCARD",
"BATCH" and "WS", which were added to HELLO response.

In SeedLink 4, HELLO should return a fixed set of capabilities for backwards
compatibility. Using INFO CAPABILITIES is deprecated. The recommended method of
determining the capabilities is the GETCAPABILITIES command.

A client may also determine supported capabilities by trial and error -- if the
server responds with ERROR, then it can be assumed that the particular
command/mode is not supported. This method works with all protocol versions.

V4 capabilities
^^^^^^^^^^^^^^^

SLPROTO:#.#
    SeedLink protocol version.

WEBSOCKET:#
    WebSocket protocol version. This implies that WebSocket shares the same port
    with native SeedLink protocol.
    
STARTTLS
    Upgrading connection to TLS using the STARTTLS command.

CAP
    ENABLE/CAPABILITIES command.
    
GETCAP
    GETCAPABILITIES command.

EXTREPLY
    Extended reply messages. Must be enabled with the ENABLE (CAPABILITIES)
    command to take effect.

NSWILDCARD
    Network & station code wildcarding.

NSWILDCARDSEQ |4|
    Sequence numbers in combination with wildcards. Implies NSWILDCARD.

BATCH
    Batch handshaking.

ASYNC |4|
    Asynchronous handshaking.

AUTH\:type |4|
    Authentication (AUTH command).

MULTISTATION
    Multi-station mode (STATION command).

TIME
    TIME and start_time of DATA/FETCH (1 second resolution). Same as
    "window-extraction" in SeedLink 3.x.

INFO\:level
    INFO level, where level is "ID", "CAPABILITIES", "STATIONS", "STREAMS",
    "GAPS", "CONNECTIONS", "ALL".

The following additional features are supported if the server implements
{CAP:SLPROTO:4.0}:

* ACCEPT

* SELECT: ":"

* DATA, FETCH: 64-bit sequence numbers, nanosconds, optional end time.

* TIME: nanoseconds
