import os, pandas as pd, requests, json, song as songModule, math, spotipy, artist as artistModule, album as albumModule
from datetime import datetime
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyParser():
    def __init__(self, folderName, year=None, client_id=None, client_secret=None, reparse=False):
        self.client_id = client_id
        self.client_secret = client_secret
        
        self.songDict = None
        self._songList = None
        self._sortType = None
        self.artistDict = None
        self._artistList = None
        self.albumDict = None
        self._albumList = None
        
        self.tracksParsed = False
        self.artistsParsed = False
        self.albumsParsed = False
        
        if not reparse:
            songData = self.getSpotifyData(folderName, year)[0]
            self.songDict = self.convertToSongs(songData)
            self._songList = list(self.songDict.values())
            self.artistDict = {}
            self.albumDict = {}
        else:
            folderFiles = os.listdir(folderName)
            if "song_data.txt" in folderFiles and "artist_data.txt" in folderFiles:
                raise NotImplementedError("TODO") 
            else:
                raise ValueError("Unable to find data from previous SpotifyParser (expected to find files song_data.txt and artist_data.txt)")

            self.tracksParsed = True
            self.artistsParsed = True

    def getSpotifyData(self, folderName, year=None):
        data = []
        unknownData = []
        for fileName in os.listdir(folderName):
            if not fileName.endswith(".json"):
                continue
                
            with open(os.path.join(folderName, fileName), encoding="utf-8") as file:
                tempData = json.load(file)
    
            if year == None:
                for song in tempData:
                    name = song["master_metadata_track_name"]
                    artist = song["master_metadata_album_artist_name"]
                    uri = song["spotify_track_uri"]
                    if name == None or artist == None or uri == None:
                        unknownData.append(song)
                    else:
                        data.append(song)
                        
            else:
                for song in tempData:
                    if datetime.fromisoformat(song["ts"]).year == year:
                        name = song["master_metadata_track_name"]
                        artist = song["master_metadata_album_artist_name"]
                        uri = song["spotify_track_uri"]
                        if name == None or artist == None or uri == None:
                            unknownData.append(song)
                        else:
                            data.append(song)
    
        print("Data contains", len(unknownData), "listens of unknown songs")
        return data, unknownData

    def convertToSongs(self, data):
        songDict = {}
        for song in data:
            try:
                tempVar = song
                song = songModule.Song(song)
                if song.id not in songDict:
                    songDict[song.id] = song
                else:
                    songDict[song.id].addListen(song)
            except Exception as e:
                print(e)
                print("Caused exception:", tempVar)
                continue
    
        return songDict

    #TODO: need to change how lists (like for artists) are handled
    # def convertSongListToDataFrame(self, songs):
    #     data = {
    #         "song_id": list(songs.keys()),
    #         "song_name": [songs[id].name for id in songs],
    #         "artist": [songs[id].artist for id in songs],
    #         "album": [songs[id].album for id in songs],
    #         "time_listened": [songs[id].timeListened for id in songs],
    #         "song_length": [songs[id].length for id in songs],
    #         "times_listened_actual": [len(songs[id].dates) for id in songs],
    #         "times_listened_estimate": [songs[id].timeListened // songs[id].length if songs[id].length != 0 else 0 for id in songs]
    #     }
    
    #     return pd.DataFrame(data).set_index("song_id")

    def getTimeListened(self):
        sum = 0
        for song in self._songList:
            sum += song.timeListened

        return sum

    def getTotalListens(self, listenType="actual"):
        if listenType not in ["actual", "estimate"]:
            raise ValueError("Listen type must be 'actual' or 'estimate'")
            
        sum = 0
        for song in self._songList:
            sum += song.getListens(listenType)

        if listenType == "estimate":
            return round(sum, 2)
        else:
            return sum

    def getUniqueSongCount(self):
        return len(self._songList)

    def timeListened(self, listenType="actual"):
        if listenType not in ["actual", "estimate"]:
            raise ValueError("Listen type must be 'actual' or 'estimate'")
            
        print(f"You listened to {self.getUniqueSongCount()} songs for {round(self.getTimeListened() / 60000, 2)} minutes with {self.getTotalListens(listenType)} listens")

    def getTopSongs(self, compare="actual_listens", num=5, reverse=False):
        compareTypes = ["listens", "actual_listens", "estimate_listens", "time_listened", "popularity", "first_listen", "last_listen", "range_listened"]
        if compare not in compareTypes:
            raise ValueError(f"Cannot compare with \"{compare}\"")
        elif num > len(self._songList):
            num = len(self._songList)

        if compare in ["listens", "actual_listens"]:
            if self._sortType not in ["listens", "actual_listens"]:
                self._songList.sort(key=lambda song: song.getListens(), reverse=True)
                self._sortType = "actual_listens"
        elif compare == "estimate_listens":
            if self._sortType != "estimate_listens":
                self._songList.sort(key=lambda song: song.getEstimatedListens(), reverse=True)
                self._sortType = "estimate_listens"
        elif compare == "time_listened":
            if self._sortType != "time_listened":
                self._songList.sort(key=lambda song: song.timeListened, reverse=True)
                self._sortType = "time_listened"
        elif compare == "first_listen":
            if self._sortType != "first_listen":
                self._songList.sort(key=lambda song: song.dates[0][0])
                self._sortType = "first_listen"
        elif compare == "last_listen":
            if self._sortType != "last_listen":
                self._songList.sort(key=lambda song: song.dates[-1][0])
                self._sortType = "last_listen"
        else:
            raise NotInplementedError("Need to implement 'popularity', 'first_listen', and 'range_listened'")

        if reverse:
            if num == len(self._songList):
                return self._songList[::-1]
            return self._songList[: (len(self._songList) - 1) - num :-1]
        else:
            if num == len(self._songList):
                return self._songList
            return self._songList[:num]
    
    def topSongs(self, compare="actual_listens", num=5, reverse=False):
        songs = self.getTopSongs(compare=compare, num=num)

        for i in range(len(songs)):
            if reverse == True:
                place = len(self._songList) - i
            else:
                place = i + 1
                
            if compare in ["listens", "actual_listens"]:
                print(f"{place}. {songs[i].toString()}: {songs[i].getListens()} listens")
            elif compare == "estimate_listens":
                print(f"{place}. {songs[i].toString()}: {songs[i].getEstimatedListens()} listens")
            elif compare == "time_listened":
                print(f"{place}. {songs[i].toString()}: {round(songs[i].timeListened / 60000, 2)} minutes")
            else:
                raise NotInplementedError("Need to implement 'popularity', 'first_listen', and 'range_listened'")

    def getSpotipyApp(self):
        if self.client_id == None or self.client_secret == None:
            raise ValueError("No client secret or client id specified")
            
        auth_manager = SpotifyClientCredentials(client_id=self.client_id, client_secret=self.client_secret)
        return spotipy.Spotify(auth_manager=auth_manager)

    def getSpotipyUser(self):
        raise NotImplementedError("TODO") 
    
    def parseWithSpotify(self):
        self._parseTrackInfo()
        print("Tracks Parsed")
        self._parseArtistInfo()
        print("Artists Parsesd")
    
    def _parseTrackInfo(self):
        sp = self.getSpotipyApp()
        MAX_IDS = 50

        tracks = []
        for i in range(math.ceil(len(self.songDict) / MAX_IDS)):
            tracks.append([])

        trackIds = list(self.songDict.keys())
        for i in range(len(trackIds)):
            tracks[i % len(tracks)].append(trackIds[i])

        albumUpdates = []
        for trackList in tracks:
            trackInfo = sp.tracks(trackList)["tracks"]
            if len(trackInfo) != len(trackList):
                raise ValueError("Spotify did not return enough tracks (during track parsing)")

            for i in range(len(trackInfo)):
                currentSong = self.songDict[trackList[i]]
                currentSong.length = trackInfo[i]["duration_ms"]
                try:
                    currentSong.isrc = trackInfo[i]["external_ids"]["isrc"]
                except:
                    currentSong.isrc = None
                currentSong.popularity = trackInfo[i]["popularity"]

                currentSong.artist = []
                for artist in trackInfo[i]["artists"]:
                    if artist["id"] not in self.artistDict:
                        self.artistDict[artist["id"]] = artistModule.Artist(artist)

                    currentSong.artist.append(self.artistDict[artist["id"]])
                    self.artistDict[artist["id"]].songs.append(currentSong)

                if trackInfo[i]["album"]["album_type"] == "single":
                    currentSong.album = "single"
                else:
                    albumId = trackInfo[i]["album"]["id"]
                    if albumId not in self.albumDict:
                        notAdded = self._addAlbumData(trackInfo[i]["album"])
                        if len(notAdded) > 0:
                            albumUpdates += notAdded
                    self.albumDict[albumId].songs.append(currentSong)
                    currentSong.album = self.albumDict[albumId]
                    
                currentSong.parsedTrack = True

        for album in albumUpdates:
            if album[1] in self.artistDict:
                self.albumDict[album[0]].artist.append(self.artistDict[album[1]])
        
        self.tracksParsed = True
        self._artistList = list(self.artistDict.values())
        self._albumList = sorted(list(self.albumDict.values()), key=lambda x: x.timeListened(), reverse=True)

    def _addAlbumData(self, albumData):
        self.albumDict[albumData["id"]] = albumModule.Album()
        self.albumDict[albumData["id"]].name = albumData["name"]
        self.albumDict[albumData["id"]].id = albumData["id"]

        needAdding = []
        for artist in albumData["artists"]:
            if artist["id"] not in self.artistDict:
                needAdding.append((albumData["id"], artist["id"]))
            else:
                self.albumDict[albumData["id"]].artist.append(self.artistDict[artist["id"]])

        return needAdding
    
    def _parseArtistInfo(self):
        if not self.tracksParsed:
            raise ValueError("Parse tracks first before getting artists")

        sp = self.getSpotipyApp()
        MAX_IDS = 50

        artists = []
        for i in range(math.ceil(len(self.artistDict) / MAX_IDS)):
            artists.append([])

        artistIds = list(self.artistDict.keys())
        for i in range(len(artistIds)):
            artists[i % len(artists)].append(artistIds[i])

        for artistList in artists:
            artistInfo = sp.artists(artistList)["artists"]
            if len(artistInfo) != len(artistList):
                raise ValueError("Spotify did not return enough tracks (during track parsing)")

            for i in range(len(artistInfo)):
                currentArtist = self.artistDict[artistList[i]]
                currentArtist.genres = artistInfo[i]["genres"]
                currentArtist.popularity = artistInfo[i]["popularity"]
                currentArtist.fullInfo = True

        self.artistsParsed = True
        self._artistList.sort(key=lambda x: x.timeListened(), reverse=True)

    def getTopArtists(self, num=5):
        if not self.artistsParsed:
            return "Artists have not been parsed" 
        return self._artistList[:num]

    def topArtists(self, num=5):
        if not self.artistsParsed:
            return "Artists have not been parsed" 
        artists = self.getTopArtists(num)

        if isinstance(artists, str):
            return artists

        for i in range(len(artists)):
            place = i + 1

            print(f"{place}. {artists[i].toString()}: {round(artists[i].timeListened() / 60000, 2)} minutes")

    def getTopAlbums(self, num=5):
        if not self.artistsParsed:
            return "Albums have not been parsed" 
        return self._albumList[:num]

    def topAlbums(self, num=5):
        if not self.artistsParsed:
            return "Albums have not been parsed" 
        albums = self.getTopAlbums(num)

        if isinstance(albums, str):
            return albums

        for i in range(len(albums)):
            place = i + 1

            print(f"{place}. {albums[i].toString()}: {round(albums[i].timeListened() / 60000, 2)} minutes")

    def saveData(self):
        if self.tracksParsed:
            with open("song_data.csv", "w") as f:
                f.write("song_id,song_name,song_artist_id,song_album,song_length,song_irsc," + "popularity,time_listened,listen_dates")
                for song in self._songList:
                    try:
                        f.write(song.__repr__())
                    finally:
                        print(song.__repr__())
            
        if self.artistsParsed:
            with open("artist_data.csv", "w") as f:
                f.write("artist_id,artist_name,artist_genres,popularity,time_listened,song_ids")
                for song in self._songList:
                    f.write(song.__repr__())

    def searchSongs(self, search, by="name", id=False):
        if not isinstance(search, str):
            raise ValueError("Search term must be a string")
        if by not in ["name", "artist", "album"]:
            raise ValueError("\"by\" must be 'name', 'artist', or 'album'")
        
        songsFound = []
        for song in self._songList:
            if by == "name":
                if search.lower() in song.name.lower():
                    songsFound.append(song)
            elif by == "artist":
                if self.artistsParsed:
                    for artist in song.artist:
                        if search.lower() in artist.name.lower():
                            songsFound.append(song)
                            break
                elif search.lower() in song.artist.lower():
                    songsFound.append(song)
            elif by == "album":
                if self.tracksParsed:
                    if song.album == "single":
                        continue
                    if search.lower() in song.album.name.lower():
                        songsFound.append(song)
                elif search.lower() in song.album.lower():
                    songsFound.append(song)
                    

        songName, songArtist, songAlbum, timeListened, actualListens, estimateListens, ids = [], [], [], [], [], [], []
        for song in songsFound:
            songName.append(song.name)
            if self.artistsParsed:
                songArtist.append("/".join([artist.name for artist in song.artist]))
            else:
                songArtist.append(song.artist)
            if self.tracksParsed:
                if song.album == "single":
                    songAlbum.append("single")
                else:
                    songAlbum.append(song.album.name)
            else:
                songAlbum.append(song.album)
            actualListens.append(song.getListens())
            estimateListens.append(song.getEstimatedListens())
            timeListened.append(round(song.timeListened / 60000, 2))
            ids.append(song.id)
        
        data = {
            "Title": songName,
            "Artist": songArtist,
            "Album": songAlbum,
            "Actual Listens": actualListens,
            "Estimated Listens": estimateListens,
            "Time Listened (min)": timeListened
        }

        if id:
            data["ID"] = ids

        return pd.DataFrame(data).sort_values(by="Time Listened (min)", ascending=False)

    def searchArtists(self, search, by="name", id=False):
        if not self.artistsParsed:
            return "Artists have not be parsed"
        if not isinstance(search, str):
            raise ValueError("Search term must be a string")
        if by not in ["name", "genre"]:
            raise ValueError("\"by\" must be 'name' or 'genre'")
        
        artistsFound = []
        for artist in self._artistList:
            if by == "name":
                if search.lower() in artist.name.lower():
                    artistsFound.append(artist)
            elif by == "genre":
                for genre in artist.genres:
                    if search.lower() in genre.lower():
                        artistsFound.append(artist)
                        break

        artistName, timeListened, genres, ids = [], [], [], []
        for artist in artistsFound:
            artistName.append(artist.name)
            timeListened.append(round(artist.timeListened() / 60000, 2))
            genres.append("/".join(artist.genres))
            ids.append(artist.id)

        data = {
            "Name": artistName,
            "Time Listened (min)": timeListened,
            "Genres": genres
        }

        if id:
            data["ID"] = ids

        return pd.DataFrame(data)
            
    def searchAlbums(self, search, by="name", id=False):
        if not self.tracksParsed:
            return "Albums have not been parsed yet"
        if not isinstance(search, str):
            raise ValueError("Search term must be a string")
        if by not in ["name", "artist"]:
            raise ValueError("\"by\" must be 'name' or 'genre'")
        
        albumsFound = []
        for album in self._albumList:
            if by == "name":
                if search.lower() in album.name.lower():
                    albumsFound.append(album)
            elif by == "artist":
                for artist in album.artist:
                    if search.lower() in artist.name.lower():
                        albumsFound.append(album)
                        break

        albumName, timeListened, artistName, ids = [], [], [], []
        for album in albumsFound:
            albumName.append(album.name)
            artistName.append("/".join([artist.name for artist in album.artist]))
            timeListened.append(round(album.timeListened() / 60000, 2))
            ids.append(album.id)

        data = {
            "Name": albumName,
            "Artist(s)": artistName,
            "Time Listened (min)": timeListened
        }

        if id:
            data["ID"] = ids

        return pd.DataFrame(data)

    def getTopGenres(self, num=5):
        if not self.artistsParsed:
            return "Genres are from artists, and artists have not been parsed" 
        
        print("Genres are from artists, so times used for rankings are only time listened to an artist")

        genres = {}
        for artist in self._artistList:
            for genre in artist.genres:
                if genre not in genres:
                    genres[genre] = 0
                genres[genre] += artist.timeListened()

        genres = sorted([(genre, time) for genre, time in genres.items()], key=lambda x: x[1], reverse=True)
        return genres[:num]

    def topGenres(self, num=5):
        genres = self.getTopGenres(num)

        if isinstance(genres, str):
            return genres

        for i in range(len(genres)):
            place = i + 1

            print(f"{place}. {genres[i][0].capitalize()} ({round(genres[i][1] / 60000, 2)} minutes)")

    def popularity(self, fromCategory="all", fromSearch=None):
        songMax = None
        songMaxList = []
        songMin = None
        songMinList = []
        songSum = 0

        if not (self.artistsParsed and self.tracksParsed):
            return "Tracks and artist need to be parsed to determine popularity"
        if fromCategory not in ["all", "artist", "album"]:
            raise ValueError(f"'fromCategory' not 'all', 'artist', or 'album' but was instead {fromCategory}")

        if fromCategory == "all":
            source = self._songList
        elif fromCategory in ["artist" or "album"]:
            if fromSearch == None:
                raise ValueError("Must enter an artist or album if getting popularity of songs from one")
            songTable = self.searchSongs(fromSearch, by=fromCategory)
            if len(songTable) == 0:
                return f"No songs found from {fromCategory} named {fromSearch}"

            source = []
            for i in range(len(songTable)):
                source.append(self.songDict[songTable.loc[i, "ID"]])
            
        for song in source:
            if song.popularity != None:
                if songMax == None or song.popularity > songMax:
                    songMax = song.popularity
                    songMaxList = [song]
                elif songMax == song.popularity:
                    songMaxList.append(song)
                
                if songMin == None or song.popularity < songMin:
                    songMin = song.popularity
                    songMinList = [song]
                elif songMin == song.popularity:
                    songMinList.append(song)

                songSum += song.popularity

        if fromCategory == "all":
            print("Popularity Stats from all songs:")
        else:
            print(f"Popularity Stats from {fromCategory.capitalize()}:")

        print(f"\tMax Popularity: {songMax}", end=" ")
        if len(songMaxList) == 1:
            print(f"({songMaxList[0].toString()})")
        else:
            print(f"({len(songMaxList)} songs, like {", ".join([song.toString() for song in songMaxList])})")

        print(f"\tMin Popularity: {songMin}", end=" ")
        if len(songMinList) == 1:
            print(f"({songMinList[0].toString()})")
        else:
            print(f"({len(songMinList)} songs, like {", ".join([song.toString() for song in songMinList])})")

        print(f"\tAverage Popularity: {round(songSum / len(source), 2)}")
                    
        if fromCategory != "all":
            return
            
        artistMax = None
        artistMaxList = []
        artistMin = None
        artistMinList = []
        artistSum = 0
        for artist in self._artistList:
            if artist.popularity != None:
                if artistMax == None or artist.popularity > artistMax:
                    artistMax = artist.popularity
                    artistMaxList = [artist]
                elif artistMax == artist.popularity:
                    artistMaxList.append(artist)
                
                if artistMin == None or artist.popularity < artistMin:
                    artistMin = artist.popularity
                    artistMinList = [artist]
                elif artistMin == artist.popularity:
                    artistMinList.append(artist)

                artistSum += artist.popularity

        print()
        print("Popularity Stats from all artists:")
        
        print(f"\tMax Popularity: {artistMax}", end=" ")
        if len(artistMaxList) == 1:
            print(f"({artistMaxList[0].toString()})")
        else:
            print(f"({len(artistMaxList)} artist, like {", ".join([artist.toString() for artist in artistMaxList])})")

        print(f"\tMin Popularity: {artistMin}", end=" ")
        if len(artistMinList) == 1:
            print(f"({artistMinList[0].toString()})")
        else:
            print(f"({len(artistMinList)} artist, like {", ".join([artist.toString() for artist in artistMinList])})")

        print(f"\tAverage Popularity: {round(artistSum / len(self._artistList), 2)}")
            
    def graphListenCounts(self):
        ax = self.searchSongs("").plot.hist(column="Actual Listens")
        ax.set_xlabel("Amount of Listens")
    
    def _graphTotalTime(self, songSource=None, graphType="total", leapYear=False, existingGraph=None, label=None, changeDateRange=False):
        if songSource == None:
            songSource = self._songList
        
        days = {}
        for i in range(1, 13):
            for j in range(1, 32):
                if i == 2 and j > 29 and leapYear:
                    break
                if i == 2 and j > 28 and (not leapYear):
                    break
                if i in [4, 6, 9, 11] and j > 30:
                    break
                
                if i < 10:
                    month = "0" + str(i)
                else:
                    month = str(i)
                    
                if j < 10:
                    day = "0" + str(j)
                else:
                    day = str(j)
                    
                date = datetime.fromisoformat(f"2024-{month}-{day}")
                days[date.date()] = 0

        for song in songSource:
            for date in song.dates:
                if date[0].date() not in days:
                    raise KeyError("Date linked to song list not found in date dictionary")
                days[date[0].date()] += date[1]

        data = {
            "Date": [date.isoformat() for date in list(days.keys())],
            "Time Listened": list(days.values())
        }

        if graphType == "total":
            for i in range(len(data["Date"]) - 1):
                data["Time Listened"][i + 1] += data["Time Listened"][i]

        if changeDateRange:
            startDate = -1
            endDate = -1
            for i in range(len(data["Time Listened"])):
                if data["Time Listened"][i] == 0:
                    continue
                else:
                    startDate = i
                    break

            for i in range(len(data["Time Listened"]) - 1, -1, -1):
                if data["Time Listened"][i] == 0:
                        continue
                else:
                    endDate = i
                    break

            
            if startDate == -1 and endDate == -1:
                raise ValueError("No dates with listening data are found")
            elif endDate == -1:
                data["Date"] = data["Date"][startDate:]
                data["Time Listened"] = data["Time Listened"][startDate:]
            else:
                data["Date"] = data["Date"][startDate:endDate]
                data["Time Listened"] = data["Time Listened"][startDate:endDate]
            print("Date range on graph has been changed; don't use 'existingGraph' to overlay another graph on this one\n")

        data["Time Listened"] = [round(time / 60000, 2) for time in data["Time Listened"]]

        if label != None:
            return pd.DataFrame(data).plot.line(x="Date", y="Time Listened", figsize=(10, 5), ax=existingGraph, label=label)
        return pd.DataFrame(data).plot.line(x="Date", y="Time Listened", figsize=(10, 5), ax=existingGraph)
    
    def graphTimeListened(self, search="", by="total_total", leapYear=False, existingGraph=None, changeDateRange=False):
        if by == "total_total" or by == "total_byday":
            return self._graphTotalTime(graphType=by[6:], leapYear=leapYear, existingGraph=existingGraph)
            
        elif by == "artist_total" or by == "artist_byday":
            if search not in self.artistDict:
                raise ValueError("Must use artist ID to search (or id is not found)")
            return self._graphTotalTime(songSource=self.artistDict[search].songs, graphType=by[7:], leapYear=leapYear, existingGraph=existingGraph, label=self.artistDict[search].name, changeDateRange=changeDateRange)

        elif by == "album_total" or by == "album_byday":
                    if search not in self.albumDict:
                        raise ValueError("Must use album ID to search (or id is not found)")
                    return self._graphTotalTime(songSource=self.albumDict[search].songs, graphType=by[6:], leapYear=leapYear, existingGraph=existingGraph, label=self.albumDict[search].toString(), changeDateRange=changeDateRange)

        elif by == "song_total" or by == "song_byday":
            if search not in self.songDict:
                raise ValueError("Must use song ID to search (or id is not found)")
            return self._graphTotalTime(songSource=[self.songDict[search]], graphType=by[5:], leapYear=leapYear, existingGraph=existingGraph, label=self.songDict[search].toString(), changeDateRange=changeDateRange)
        





