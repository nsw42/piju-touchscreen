import logging
import requests


class ArtworkCache:
    def __init__(self):
        self.current_track_uri = None
        self.current_image_uri = None
        self.current_image = None
        self.current_image_width = None
        self.current_image_height = None

    def update(self, jsonrpc, new_track_uri):
        if new_track_uri == self.current_track_uri:
            # nothing to do
            return

        image_dict = jsonrpc.request("core.library.get_images", {
            "uris": [new_track_uri]
        })
        image_list = image_dict[new_track_uri] if image_dict else None
        image_dict = image_list[0] if image_list else None
        image_uri = jsonrpc.base_uri + image_dict['uri'] if image_dict else None
        image_width = image_dict['width'] if image_dict else None
        image_height = image_dict['height'] if image_dict else None

        if image_uri == self.current_image_uri:
            # nothing to do
            return

        # if we get here, we need to update our cache
        if image_uri:
            logging.debug("Fetching new artwork: %s", image_uri)
            response = requests.get(image_uri, allow_redirects=True)
            ok = response.ok
        else:
            response = None
            ok = False

        if ok:
            self.current_image = response.content
            self.current_track_uri = new_track_uri
            self.current_image_uri = image_uri
        else:
            self.current_image = None
            self.current_track_uri = None
            self.current_image_uri = None
        self.current_image_width = image_width
        self.current_image_height = image_height
