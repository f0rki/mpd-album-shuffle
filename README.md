Small program to randomly play and sort albums in the mpd playlist. Uses the
MPD\_HOST environment variable if it exits. Also accepts host, port and password
as commandline parameters.

Usage
-----

To sort the albums randomly.
<pre>
$ mpd-album-shuffle.py sort
</pre>

To play a random album:
<pre>
$ mpd-album-shuffle.py play
</pre>

Help output
<pre>
usage: mpd-album-shuffle.py [-h] [-v] [-vv] [-p PORT] [-H HOST] [-P PASSWORD]
                            {play,sort}

Randomly play or sort the albums in the current mpd playlist

positional arguments:
  {play,sort}

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase verbosity of output
  -vv                   turn on debug output (really really verbose)
  -p PORT, --port PORT  the port to connect to
  -H HOST, --host HOST  the hostname to connect to
  -P PASSWORD, --password PASSWORD
                        the password
</pre>
