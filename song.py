import artist as artistModule
from datetime import datetime

class Song():
    def __init__(self, songData):
        self.name, self.artist, self.album, self.id = "", "", "", ""
        self.timeListened, self.length = 0, 0
        self.dates = []
        self.__parseSongData(songData)

        self.parsedTrack = False
        self.irsc = None
        self.popularity = None

    def __parseSongData(self, songData):
        if not isinstance(songData, dict):
            raise ValueError("Given song data not in correct format: " + str(type(songData)) + " should be <class 'dict'>")

        # Other Possible Keys:
        # platform, conn_country, ip_addr, episode_name, episode_show_name, spotify_episode_uri,
        # reason_start, reason_end, shuffle, skipped, offline, offline_timestamp, incognito_mode
        expectedKeys = set(["ts", "ms_played", "master_metadata_track_name", "master_metadata_album_artist_name", "master_metadata_album_album_name", 
                            "spotify_track_uri"])
        diffKeys = list(expectedKeys - set(songData.keys()))
        if len(diffKeys) != 0:
            raise ValueError("Given song data does not contain expected dictionary keys: " + str(diffKeys))

        #Fill song data
        if not self.name:
            self.name = songData["master_metadata_track_name"]
        if not self.artist:
            self.artist = songData["master_metadata_album_artist_name"]
        if not self.album:
            self.album = songData["master_metadata_album_album_name"]
        if not self.id:
            self.id = songData["spotify_track_uri"][-22:]
        if self.length < songData["ms_played"]:
            self.length = songData["ms_played"]

        #Fill song listen data
        self.timeListened += songData["ms_played"]
        self.dates.append((datetime.fromisoformat(songData["ts"]), songData["ms_played"]))

    def __repr__(self):
        #csv line of the song
        if "," in self.name:
            name = f"\"{self.name}\""
        else:
            name = self.name
            
        if self.parsedTrack:
            if self.album == "single":
                return f"{self.id},{name},{"/".join([artist.id for artist in self.artist])},single,{self.length},{self.irsc},{self.popularity},{self.timeListened},{"/".join([":".join([obj.isoformat()[:-6], str(date[1])]) for date in self.dates])}"
            return f"{self.id},{name},{"/".join([artist.id for artist in self.artist])},{self.album.name},{self.length},{self.irsc},{self.popularity},{self.timeListened},{"/".join([":".join([obj.isoformat()[:-6], str(date[1])]) for date in self.dates])}"
        else:
            return f"{self.id},{name},{self.artist},{self.album},{self.length},{self.timeListened},{"/".join([":".join([obj.isoformat()[:-6], str(date[1])]) for date in self.dates])}"

    def toString(self, id=False):
        if self.parsedTrack:
            if id:
                return f"{self.name} by {", ".join([artist.name for artist in self.artist])} ({self.id})"
            return f"{self.name} by {", ".join([artist.name for artist in self.artist])}"
        else:
            if id:
                return f"{self.name} by {self.artist} ({self.id})"
            return f"{self.name} by {self.artist}"

    def addListen(self, song):
        if not isinstance(song, Song):
            try:
                song = Song(song)
            except:
                raise ValueError("Comparing with a value that is not a Song object (and can't be converted into one)")
                
        if self.equals(song):
            if song.length > self.length:
                self.length = song.length

            #Fill song listen data
            self.timeListened += song.timeListened
            self.dates.append((song.dates[0][0], song.dates[0][1]))

    def equals(self, otherSong):
        if not isinstance(otherSong, Song):
            try:
                otherSong = Song(otherSong)
            except:
                raise ValueError("Comparing with a value that is not a Song object (and can't be converted into one)")

        if self.name == otherSong.name and self.artist == otherSong.artist and self.album == otherSong.album and self.id == otherSong.id:
            return True
        else:
            return False

    def getEstimatedListens(self):
        self.length = int(self.length)
        self.timeListened = int(self.timeListened)
        
        if self.length > 0 and self.timeListened > 0:
            return round(self.timeListened / self.length, 2)
        else:
            return 0

    def getListens(self, amountType="actual"):
        if amountType == "estimate":
            return self.getEstimatedListens()
        else:
            return len(self.dates)


