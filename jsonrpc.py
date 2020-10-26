import logging

import requests


class JsonRPC:
    def __init__(self, base_uri):
        self.base_uri = base_uri

    def request(self, method, args=None):
        request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': method
        }
        if args:
            request['params'] = args
        response = requests.post(self.base_uri + '/mopidy/rpc', json=request)
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
