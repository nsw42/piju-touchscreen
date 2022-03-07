
class NowPlaying:
    def __init__(self):
        self.refresh_countdown = 0
        self.artist_name = None
        self.is_track = None
        self.track_name = None
        self.track_number = None
        self.album_tracks = None
        self.current_state = None
        self.current_volume = None
        self.image_uri = None
        self.image = None
        self.image_width = None
        self.image_height = None
        self.scanning_active = None

    def __str__(self):
        return 'NowPlaying(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' % (
            self.refresh_countdown,
            self.artist_name,
            self.is_track,
            self.track_name,
            self.track_number,
            self.album_tracks,
            self.current_state,
            self.current_volume,
            self.image_uri,
            self.image_width,
            self.image_height,
            self.scanning_active)
