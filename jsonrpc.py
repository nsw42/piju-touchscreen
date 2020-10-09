import logging

import requests


def jsonrpc(method):
    request = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': method
    }
    response = requests.post('http://localhost:6680/mopidy/rpc', json=request)
    if response.ok:
        return response.json()['result']
    else:
        logging.error('Failed to get response from mopidy: status=%u, error=%s', response.status_code, response.text)
        return None
