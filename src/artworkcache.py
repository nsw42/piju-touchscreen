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

        if artwork := self.update_inner(apiclient, new_image_uri):
            self.current_image_uri = new_image_uri
            self.current_image = artwork
        else:
            self.current_image_uri = None
            self.current_image = None

    def update_inner(self, apiclient: ApiClient, new_image_uri: str):
        """
        Returns the artwork bytes or None if there is None
        """
        if new_image_uri is None:
            return None

        # if we get here, we need to update our cache
        logging.debug("Fetching new artwork: %s", new_image_uri)
        return apiclient.get_artwork(new_image_uri)  # returns artwork bytes or None
