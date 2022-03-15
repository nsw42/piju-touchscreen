import logging

from apiclient import ApiClient


class ArtworkCache:
    def __init__(self):
        self.current_info_uri = None
        self.current_image_uri = None
        self.current_image = None
        self.current_image_width = None
        self.current_image_height = None

    def update(self, apiclient: ApiClient, new_info_uri: str):
        if new_info_uri == self.current_info_uri:
            # nothing to do
            return

        if new_info_uri is None:
            self.current_info_uri = new_info_uri
            self.current_image_uri = None
            self.current_image = None
            self.current_image_width = None
            self.current_image_height = None
            return

        artwork_info = apiclient.get_artwork_info(new_info_uri)

        image_uri = artwork_info.imageuri
        image_width = artwork_info.width
        image_height = artwork_info.height

        if image_uri == self.current_image_uri:
            # nothing to do
            return

        # if we get here, we need to update our cache
        if image_uri:
            logging.debug("Fetching new artwork: %s", artwork_info.imageuri)
            artwork = apiclient.get_artwork(artwork_info.imageuri)
        else:
            artwork = None

        self.current_info_uri = new_info_uri
        self.current_image_uri = image_uri
        self.current_image = artwork
        self.current_image_width = image_width
        self.current_image_height = image_height
