# MPD Album Shuffling

Small program to randomly play and sort albums in the mpd playlist, for people
who want to shuffle whole albums and not songs. Uses the `MPD_HOST` environment
variable if it exits. Also accepts host, port and password as command-line
parameters.

## Usage

To sort the albums randomly.
```
$ mpd-album-shuffle sort
```

To play a random album:
```
$ mpd-album-shuffle play
```

Help output
```
usage: mpd-album-shuffle [-h] [-v] [-vv] [-p PORT] [-H HOST] [-P PASSWORD]
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
```

## Install

You can install with pip from github:

```
$ pip install git+https://github.com/f0rki/mpd-album-shuffle.git
```
