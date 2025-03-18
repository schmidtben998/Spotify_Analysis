class Artist():
    def __init__(self, artistData):
        self.name, self.id = "", ""
        self.songs = []
        self.albums = []

        self.fullInfo = False
        self.genres = None
        self.popularity = None

        if isinstance(artistData, str):
            try:
                self.__parseArtistData(dict(artistData))
            except:
                self.name = artistData
        elif isinstance(artistData, dict):
            self.__parseArtistData(artistData)
        else:
            raise ValueError("Unable to parse given artist data")

    def __repr__(self):
        if self.fullInfo:
            return f"{self.id},{self.name},{"/".join(self.genres)},{self.popularity},{self.timeListened()},{"/".join([song.name if "," not in song.name else f"\"{song.name}\"" for song in self.songs])}"
        else:
            return f"{self.id},{self.name}"

    def toString(self, id=False):
        if id:
            return f"{self.name} ({self.id})"
        else:
            return f"{self.name}"
            

    def __parseArtistData(self, data):
        expectedKeys = ["name", "id"]
        if not all(key in data for key in expectedKeys):
            raise ValueError("Data doesn't contain expected data")

        self.name = data["name"]
        self.id = data["id"]

    def timeListened(self):
        sum = 0
        for song in self.songs:
            sum += song.timeListened

        return sum