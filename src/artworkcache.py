import logging

from apiclient import ApiClient


class ArtworkCache:
    def __init__(self):
        self.current_image_uri = None
        self.current_image = None

    def update(self, apiclient: ApiClient, new_image_uri: str):
        if new_image_uri == self.current_image_uri:
            # nothing to do
            return

        if new_image_uri is None:
            self.current_image_uri = None
            self.current_image = None
            return

        # if we get here, we need to update our cache
        logging.debug("Fetching new artwork: %s", new_image_uri)
        artwork = apiclient.get_artwork(new_image_uri)

        if apiclient.connection_error:
            # maybe it's a transient error - retry
            self.current_image_uri = None
            self.current_image = None
            return

        self.current_image_uri = new_image_uri
        self.current_image = artwork
