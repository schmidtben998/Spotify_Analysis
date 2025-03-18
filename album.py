import song as songModule

class Album():
    def __init__(self):
        self.name = ""
        self.artist = []
        self.id = ""
        
        self.songs = []

    def toString(self, id=False):
        if not id:
            return f"{self.name} by {", ".join([artist.toString() for artist in self.artist])}"
        return f"{self.name} by {", ".join([artist.toString() for artist in self.artist])} ({self.id})"
    
    def addSong(self, song):
        if not isinstance(song, songModule.Song):
            raise ValueError 

        self.songs.append(song)

    def timeListened(self):
        sum = 0
        for song in self.songs:
            sum += song.timeListened

        return sum