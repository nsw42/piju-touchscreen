from collections import namedtuple


NowPlaying = namedtuple('NowPlaying', ['artist_name',
                                       'track_name',
                                       'track_number',
                                       'album_tracks',
                                       'current_state',
                                       'current_volume',
                                       'image',
                                       'image_width',
                                       'image_height'])
