#!/usr/bin/env python
#
# Copyright (C) 2013 Michael Rodler contact (at) f0rki (dot) at
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import sys
import os
import argparse
import random
import logging
import mpd


MPD_CONNECTION_TIMEOUT = 10


class mpd_connect(object):
    """
    use this with the with statement to create a MPDClient and connect to it.
    e.g.::

      with mpd_connect("localhost", 6600) as client:
          print(client.status())

    """

    def __init__(self, host, port, password=None):
        self.host = host
        self.port = port
        self.password = password

    def __enter__(self):
        self.client = mpd.MPDClient()
        self.client.timeout = MPD_CONNECTION_TIMEOUT
        try:
            self.client.connect(self.host, self.port)
        except ConnectionRefusedError as e:
            logging.error("Couldn't connect to MPD at {}:{} ({})"
                    .format(self.host, self.port, e))
            return None
        if self.password is not None:
            try:
                self.client.password(self.password)
            except mpd.CommandError as e:
                logging.error("MPD didn't accept the password")
                return None
        logging.debug("connected to MPD version: {}"
                .format(self.client.mpd_version))
        return self.client

    def __exit__(self, type, value, traceback):
        if self.client is not None:
            self.client.close()
            self.client.disconnect()


class AlbumList(object):
    """
    Class which wraps functionality to maintain a list of all albums in the
    current playlist
    """

    def __init__(self, client):
        self.client = client
        self.albums = None
        self.refresh()

    def refresh(self):
        """fetch a list of albums from the mpd playlist"""
        # newly seed the rng for less predictibility
        random.seed()
        # fetch albums
        self.albums = set()
        for song in self.client.playlistinfo():
            if "album" in song:
                album = song["album"]
                if isinstance(album, list):
                    album = album[0]
                self.albums.add(album)
            else:
                #TODO: every song without album info should be considered to be
                # in a separate album
                logging.debug("no album information, ignoring entry: {}"
                        .format(song))

    def find_album_boundaries(self, albumname):
        """returns a tuple of the positions of the first and last song of the
        passed album name. If the album isn't found (None, None) is returned.
        """
        entries = self.client.playlistfind("album", albumname)
        if entries:
            return int(entries[0]["pos"]), int(entries[-1]["pos"])
        else:
            return None, None  # TODO: or raise Exception?

    def get_current_album(self):
        return self.client.currentsong()["album"]

    def choose_random_album(self, current):
        """picks a random album from the current playlist, while trying to
        avoid the current album.
        """
        if self.albums:
            if len(self.albums) == 1:
                return current
            else:
                new = random.choice(list(self.albums))
                while current == new:
                    new = random.choice(list(self.albums))
                return new
        else:
            logging.warn("No albums found")
            return None

    def play_random(self):
        """Play first song of a random album in the current playlist."""
        current = self.get_current_album()
        new = self.choose_random_album(current)
        if new is not None:
            logging.info("Choosing random album \"{}\"".format(new))
            entries = self.client.playlistfind("album", new)
            if entries:
                self.client.play(entries[0]["pos"])
            else:
                logging.warn("Couldn't find entry for album {}".format(new))
                self.refresh()
                self.play_random()
        else:
            logging.error("Playlist seems to be empty")

    def shuffle_albums(self):
        """Essentially do a random.shuffle over all albums and sort the
        playlist accordingly. This assumes that the playlist is already
        sorted by albums.
        """
        logging.info("shuffling albums")
        albumlist = list(self.albums)
        random.shuffle(albumlist)
        logging.info("chosen album order is {}".format(albumlist))
        for album in albumlist:
            first, last = self.find_album_boundaries(album)
            if first is None or last is None:
                logging.error("No boundaries for album {}".format(album))
            else:
                logging.debug("moving {}:{} to position 0".format(first, last))
                songrange = "{}:{}".format(first, last + 1)
                self.client.move(songrange, 0)


def extract_mpd_credentials(string, defaults=None):
    """split a string of format "password@host:port" into individual values. If
    a defaults parameter is given, the values will be returned if no """
    host, port, pw = None, None, None
    if defaults is not None:
        host, port, pw = defaults[0], defaults[1], defaults[2]
    logging.debug("{} {} {}".format(host, port, pw))
    if string:
        if "@" in string:
            pw, con = string.split("@")
        else:
            con = string
        if con:
            if ":" in con:
                host, port = con.split(":")
            else:
                host = con
    logging.debug("{} {} {}".format(host, port, pw))
    return host, port, pw


def main():
    parser = argparse.ArgumentParser(description=
            "Randomly play or sort the albums in the current mpd playlist")
    parser.add_argument("-v", "--verbose", action="store_true",
            help="increase verbosity of output")
    parser.add_argument("-vv", dest="debug", action="store_true",
            help="turn on debug output (really really verbose)")
    parser.add_argument("-p", "--port", nargs=1, type=int,
            help="the port to connect to")
    parser.add_argument("-H", "--host", nargs=1,
            help="the hostname to connect to")
    parser.add_argument("-P", "--password", nargs=1,
            help="the password")
    parser.add_argument("command", choices=["play", "sort"])
    args = parser.parse_args(sys.argv[1:])

    fmt = "%(message)s"
    if args.debug:
        loglevel = logging.DEBUG
        fmt = "%(levelname)s:%(name)s - %(message)s"
    elif args.verbose:
        loglevel = logging.INFO
    else:
        loglevel = logging.WARN
    logging.basicConfig(level=loglevel, format=fmt)

    # fetch mpd credentials
    host, port, pw = ("localhost", 6600, None)
    mpdenv = os.getenv("MPD_HOST")
    if mpdenv:
        logging.debug("found MPD_HOST in env {}".format(mpdenv))
        host, port, pw = extract_mpd_credentials(mpdenv, (host, port, pw))
    if args.port:
        port = args.port[0]
    if args.password:
        pw = args.password[0]
    if args.host:
        host = args.host[0]
    logging.debug("connecting to host: {} port: {} pw: {}"
            .format(host, port, pw))

    try:
        with mpd_connect(host, port, pw) as client:
            if client is None:
                return -1
            al = AlbumList(client)
            al.refresh()
            if args.command == "play":
                al.play_random()
            elif args.command == "sort":
                al.shuffle_albums()
            else:
                logging.error("invalid command {}".format(parser.command))
                return -1
    except mpd.ConnectionError as e:
        logging.error("Couldn't connect to MPD ({})".format(e))
    return 0

if __name__ == "__main__":
    sys.exit(main())
