import logging

import requests

BASE_URI = 'http://localhost:6680'


def jsonrpc(method, args=None):
    request = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': method
    }
    if args:
        request['params'] = args
    response = requests.post(BASE_URI + '/mopidy/rpc', json=request)
    if response.ok:
        response_body = response.json()
        if response_body:
            try:
                return response_body['result']
            except KeyError:
                logging.error(response.content)
    else:
        logging.error('Failed to get response from mopidy: status=%u, error=%s', response.status_code, response.text)
    return None
