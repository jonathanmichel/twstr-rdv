import requests
from bs4 import BeautifulSoup


class TwstrRdv:
    """
    Get last rendez-vous on the Twistair website
    """
    def __init__(self, url) -> None:
        self.url = url

    def get_last_message(self):
        # Get html content and parse it with BeautifulSoup
        html_text = requests.get(self.url).text
        html = BeautifulSoup(html_text, 'html.parser')

        # Get page content and divs
        page_content = html.find("div", {"id": "page-content"})
        div_children = page_content.findChildren("div", recursive=False)
        # @todo Check content 

        # Small check, rendez-vous page contains two divs
        # The last message is in the second one
        if len(div_children) == 2:
            rdv = div_children[1]
            rdv_text = rdv.p.text
            if rdv_text:
                return rdv_text
        
        return None