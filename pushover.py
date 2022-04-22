import http.client, urllib


class Pushover:
    """
    Send notification to pushover
    """
    def __init__(self, token, user) -> None:
        self.conn = http.client.HTTPSConnection("api.pushover.net:443")
        self.token = token
        self.user = user

    def send_message(self, message, title="", url="", url_title=""):
        """
        Send message
        Optionnal title, url and url title
        """
        self.conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": self.token,
                "user": self.user,
                "message": message,
                "title": title,
                "url": url,
                "url_title": url_title
            }), 
            { "Content-type": "application/x-www-form-urlencoded" })

        self.conn.getresponse()

