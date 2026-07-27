import requests


class HttpModule:

    def __init__(self):
        self.functions = {
            "get": self.get,
            "post": self.post,
        }

    def get(self, url):
        return requests.get(url).text

    def post(self, url, data):
        return requests.post(url, json=data).text