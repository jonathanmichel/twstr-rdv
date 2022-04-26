import requests

class Healthchecks:
    def __init__(self, uuid, url="https://hc-ping.com/"):
        self.uuid = uuid
        self.url = url

    def post(self, path="", data=""):
        try:
            requests.post(self.url + self.uuid + path, timeout=10, data=data)
        except requests.RequestException as e:
            # Log ping failure here...
            print("Ping failed: %s" % e)

    def success(self, data=""):
        self.post(data=data)

    def start(self, data=""):
        self.post("/start", data=data)

    def fail(self, data=""):
        self.post("/fail", data=data)

    def exit(self, code, data=""):
        self.post(f"/{code}", data=data)
