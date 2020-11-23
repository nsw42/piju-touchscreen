import logging

import requests


class JsonRPC:
    def __init__(self, base_uri):
        self.base_uri = base_uri
        self.connection_error = False

    def request(self, method, args=None):
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': method
        }
        if args:
            request['params'] = args
        try:
            response = requests.post(self.base_uri + '/mopidy/rpc', json=request)
        except requests.exceptions.ConnectionError:
            logging.error("Unable to connect to mopidy")
            self.connection_error = True
            return None
        self.connection_error = False
        if response.ok:
            response_body = response.json()
            if response_body:
                try:
                    return response_body['result']
                except KeyError:
                    logging.error(response.content)
        else:
            logging.error('Failed to get response from mopidy: status=%u, error=%s',
                          response.status_code,
                          response.text)
        return None
