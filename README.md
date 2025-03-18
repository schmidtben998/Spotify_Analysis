# Spotify_Analysis

Uses Python to analyze a Spotify user's "Extended Streaming History." (Go to Account Privacy to download data)

Use SpotifyParser object to analyze data. To use Spotify track data (from Spotify song's URIs), parser must be connected to the Spotify WebAPI. This can be done through a free account on [Spotify for Developers](https://developer.spotify.com/) and adding the `Client ID` and `Client secret` from a WebAPI project to the parser.

#### Notes on terminology:
- **Actual listens** are the count of unique listens; these listens can be any length (even 0 milliseconds) and can over estimate listening time.
- **Estimated listens** is the count of full listens, and is the total time listened to a song divided by the length of song. If returning functions with estimated listens before parsing songs with Spotify WebAPI, the length of the song may be incorrect.

**Reparse/Save data features currently work in progress**

## Spotify Data Format

A Spotify user's "Extended Streaming History" is a .json file, with this format (see Spotify's ReadMe):
```
{
"ts": "YYY-MM-DD 13:30:30",
"username": "_________",
"platform": "_________",
"ms_played": _________,
"conn_country": "_________",
"ip_addr_decrypted": "___.___.___.___",
"user_agent_decrypted": "_________",
"master_metadata_track_name": "_________,
"master_metadata_album_artist_name:_________",
"master_metadata_album_album_name:_________",
"spotify_track_uri:_________",
"episode_name": _________,
"episode_show_name": _________,
"spotify_episode_uri:_________",
"reason_start": "_________",
"reason_end": "_________",
"shuffle": null/true/false,
"skipped": null/true/false,
"offline": null/true/false,
"offline_timestamp": _________,
"incognito_mode": null/true/false,
}
```
So, as long as song data is in this format, the SpotifyParser should be able to return information on listening data. Of course, if there is no `spotify_track_uri`, the parser will be unable to return data from Spotify on the specific track. 

## SpotifyParser:
__init__(folderName, year=None, client_id=None, client_secret=None, reparse=False)\
> Creates a SpotifyParser object
> 
> Parameters:
> - folderName - name of folder with Spotify data
> - year - year to parse through (None for all data)
> - client_id - client id for Spotify WebAPI
> - client_secret - client secret for Spotify WebAPI

getSpotifyData(folderName, year=None)
> returns list of song data parsed from Spotify Data .json file
>
> Parameters:
> - folderName - name of folder with Spotify data
> - year - year of data to return (None for all data)

convertToSongs(data)
> returns list of Song objects from song data (a list of song dictionaries)
>
> Parameters:
> - data - a list of song dictionaries

getTimeListened()
> returns total time listened (in milliseconds)

getTotalListens(listenType="actual")
> returns total number of listens
>
> Parameters:
> - listenType - 'estimate' or 'actual' to calculate listens as such

getUniqueSongCount()
> returns number of unique songs listened

timeListened(listenType="actual")
> prints summary of listening data
>
> Parameters:
> - listenType - 'estimate' or 'actual' to calculate listens as such

getTopSongs(compare="actual_listens", num=5, reverse=False)
> returns a list of organized Songs
>
> Parameters:
> - compare - data Songs are organized by ("listens", "actual_listens", "estimate_listens", "time_listened", "first_listen", or "last_listen")
> - num - number of songs to return
> - reverse - False to return top of list (songs first when organized) or True to return bottom

topSongs(compare="actual_listens", num=5, reverse=False)
> prints an ordered list of Songs
>
> Parameters:
> - compare - data Songs are organized by ("listens", "actual_listens", "estimate_listens", "time_listened", "first_listen", or "last_listen")
> - num - number of songs to return
> - reverse - False to return top of list (songs first when organized) or True to return bottom

getSpotifyApp()
> returns a spotipy module's Spotify object with initialized client information

parsesWithSpotify()
> parses track and artist data using Spotify WebAPI

_parseTrackInfo()
> parses track data from Spotify WebAPI

_addAlbumData(albumData)
> associates album data with artist list

_parseArtistInfo()
> parses artist data from Spotify WebAPI

getTopArtists(num=5)
> returns a list of top artists
>
> Parameters:
> - num - number of artists returned

topArtists(num=5)
> prints an ordered list of top artists
>
> Parameters:
> - num - number of artists printed

getTopAlbums(num=5)

searchSongs(search, by="name", id=False)

searchArtists(search, by="name", id=False)

searchAlbums(search, by="name", id=False)

getTopGenres(num=5)

topGenres(num=5)

popularity(fromCategory="all", fromSearch=None)

graphListenCounts()

_graphTotalTime(songSource=None, graphType="total", leapYear=False, existingGraph=None, label=None, changeDateRange=False)

graphTimeListened(self, search="", by="total_total", leapYear=False, existingGraph=None, changeDateRange=False)
 
