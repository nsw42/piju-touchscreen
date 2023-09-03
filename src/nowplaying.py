
class NowPlaying:
    def __init__(self):
        self.refresh_countdown = 0
        self.artist_name = None
        self.is_track = None
        self.track_name = None
        self.track_number = None
        self.album_tracks = None
        self.stream_name = None
        self.current_state = None
        self.current_volume = None
        self.image_uri = None
        self.image = None
        self.image_width = None
        self.image_height = None
        self.scanning_active = None

    def __str__(self):
        return ('NowPlaying('
                f'{self.refresh_countdown}, '
                f'{self.artist_name}, '
                f'{self.is_track}, '
                f'{self.track_name}, '
                f'{self.track_number}, '
                f'{self.album_tracks}, '
                f'{self.stream_name}, '
                f'{self.current_state}, '
                f'{self.current_volume}, '
                f'{self.image_uri}, '
                f'{self.image_width}, '
                f'{self.image_height}, '
                f'{self.scanning_active})')
