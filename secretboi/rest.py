import json
import urllib.error
import urllib.request


class HostDown(Exception):
    pass


class NotFound(Exception):
    pass


class BadRequest(Exception):
    def __init__(self, message, data):
        super().__init__(message)
        self.data = data


def open_response(request):
    request.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(request) as response:
            data = response.read()
            return json.loads(data)
    except urllib.error.HTTPError as e:
        if e.status == 404:
            raise NotFound(f'host {request.host} returned a 404 for path {request.selector}')

        if e.status == 400:
            message = e.read().decode('utf-8')
            data = json.loads(message)
            raise BadRequest(f'host {request.host} replied "Bad Request"', data)
        raise e
    except urllib.error.URLError as e:
        if type(e.reason) is ConnectionRefusedError:
            raise HostDown(f'connection to {request.host} refused: {e}')

        raise e


def get(url, headers={}):
    request = urllib.request.Request(url, method='GET', headers=headers)
    return open_response(request)


def post(url, data={}, headers={}):
    if type(data) is dict:
        data = json.dumps(data)

    if type(data) is str:
        data = data.encode("utf-8")

    request = urllib.request.Request(url, method='POST', headers=headers, data=data)
    return open_response(request)
