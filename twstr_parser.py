import requests
import dateparser
from bs4 import BeautifulSoup


class TwstrParser:
    """
    Get last rendez-vous on the Twistair website
    """
    def __init__(self, base_url, path_rendez_vous, path_meteo) -> None:
        self.base_url = base_url
        self.path_rendez_vous = path_rendez_vous
        self.path_meteo = path_meteo

        self.weather_src = set()


    def get_last_rendez_vous(self):
        # Get html content and parse it with BeautifulSoup
        html_text = requests.get(self.base_url + self.path_rendez_vous).text
        html = BeautifulSoup(html_text, 'html.parser')

        # Get page content and divs
        page_content = html.find("div", {"id": "page-content"})
        # Get div children
        div_children = page_content.findChildren("div", recursive=False)

        # Small check, rendez-vous page contains two divs
        # The last message is in the second one
        if len(div_children) == 2:
            rdv = div_children[1]
            rdv_text = rdv.p.text
            if rdv_text:
                return rdv_text
        
        return None

    def get_forecast(self, index=0):
        forecasts_html = self.get_forecasts_html()
        return self.parse_forecast_data(forecasts_html[index])

    def get_all_forecasts(self):
        forecasts_html = self.get_forecasts_html()
        forecasts = []
        # print(len(forecasts))
        for i in range(0, len(forecasts_html)):
            forecasts.append(self.parse_forecast_data(forecasts_html[i]))

        return forecasts

    def parse_forecast_data(self, forecast):
        # print(forecast)

        section = forecast.findChildren("h2", recursive=False)[0].text.replace("  ", "").replace("\n", "")
        situation = forecast.findChildren("p", recursive=False)[0].text
        table = forecast.findChildren("table", recursive=False)[0]
        lines = table.findChildren("tr", recursive=False)

        weather_icons = []
        imgs = forecast.findChildren("img", recursive=True)
        for i in imgs:
            asset = i['src'].split("/")[3]
            weather_icons.append(asset)

        # print("=" * 10 + "forecast")
        # print(section)
        # print("=" * 10 + "situation")
        # print(situation)
        # print(len(lines))

        elements = []

        for l in lines:
            columns = l.findChildren("td", recursive=False)
            elements.append({
                "key": columns[0].text,
                "content": columns[1].text
            })
            # print("*" * 5 + columns[0].text + "*" * 5)
            # print(columns[1].text)

        date_title = section.split("·")

        date_time = dateparser.parse(date_title[0]).date()

        return {
            "date": date_time,
            "title": date_title[1],
            "section": section,
            "situation": situation,
            "elements": elements,
            "icons": weather_icons
        }


    def get_forecasts_html(self):
        # Get html content and parse it with BeautifulSoup
        html_text = requests.get(self.base_url + self.path_meteo).text
        html = BeautifulSoup(html_text, 'html.parser')

        page_content = html.find("div", {"id": "page-content"})
        div_children = page_content.findChildren("div", recursive=False)
        box = div_children[0].findChildren("div", recursive=False)
        forecasts_div = box[0].findChildren("div", recursive=False)
        forecasts = forecasts_div[0].findChildren("div", recursive=False)

        return forecasts

    def format_meteo(self, meteo):
        emojis = [
            [ "Sunny-128-2510f9e2f167b9304bcebecc7a54d5f3e2ff8b863de8bf0c48a954ec1c5e6c8d.png", "☀️" ],
            [ "Sunny-Period-128-b89aa66c7d6863bb2572d95a5bfc664bd59897681b5c2d8b45026241bc3fb239.png", "🌤" ],
            [ "Sunny-Interval-128-71f71ae3a4c64eab72e509d2d8d4c5103fe2993b9022e16c3bc89e3efefc094c.png", "⛅️" ],
            [ "Overcast-128-124228bb6aefbd6a5e44a2c8dbedc9c50ab35e3929b6ecdd0dea5a73a24a4891.png", "☁️" ]
        ]

        weather_emojis = ""
        for ic in meteo["icons"]:
            weather_emojis += self.emoji_converter(emojis, ic) + " "

        message = f"""
<u>Météo de Tonio du {meteo["date"].strftime("%d/%m/%Y")}</u> {weather_emojis}{meteo["title"]}
\n{meteo["situation"]}\n
"""
        emojis = [
            ["Vent", "🌬️"], 
            ["Thermique", "🌡️"],
            ["Danger", "⚠️"],
            ["Habits", "🧤"],
            ["Infos", "ℹ️"]
        ]

        for el in meteo["elements"]:
            header = self.emoji_converter(emojis, el['key']) + " " * 3 + el['key']
            message += f"\n<b>{header}</b>\n{el['content']}\n"

        message += f"\n<a href='{self.base_url + self.path_meteo}'>🔗 Voir sur le site</a>"
        
        return message

    def emoji_converter(self, emojis, text, default=""):
        for em in emojis:
            if text == em[0]:
                return em[1]
        
        return default