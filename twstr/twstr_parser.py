import requests
import dateparser
from bs4 import BeautifulSoup
from datetime import datetime, time
from enum import Enum


class TwstrParser:
    class DateCheck(Enum):
        NO_TOMORROW = 1
        TOMORROW = 2
        NO_TODAY = 3
        TODAY = 4
    
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
            rdvs = div_children[1]
            rendezvous = rdvs.find("div", {"class": "alert-primary"})
            rendezvous_date = rendezvous.find("h2").text.replace("  ", "").replace("\n", "")
            # Converte date format
            rendezvous_date = datetime.strptime(rendezvous_date, '%d.%m.%Y').date().strftime('%d/%m/%Y')

            rdv_p = rendezvous.findAll("p")
            rdv_text = ""
            for p in rdv_p:
                rdv_text += p.text + "\n"
            if rdv_text:
                return {
                    "date": rendezvous_date,
                    "content": rdv_text
                }
        
        return None

    def get_forecast(self, index=0):
        forecasts_html = self.get_forecasts_html()
        return self.parse_forecast_data(forecasts_html[index])

    def get_all_forecasts(self):
        forecasts_html = self.get_forecasts_html()
        forecasts = []
        for i in range(0, len(forecasts_html)):
            forecasts.append(self.parse_forecast_data(forecasts_html[i]))

        return forecasts

    def parse_forecast_data(self, forecast):
        section = forecast.findChildren("h2", recursive=False)[0].text.replace("  ", "").replace("\n", "")
        situation = forecast.findChildren("p", recursive=False)[0].text
        table = forecast.findChildren("table", recursive=False)[0]
        lines = table.findChildren("tr", recursive=False)

        weather_icons = []
        imgs = forecast.findChildren("img", recursive=True)
        for i in imgs:
            asset = i['src'].split("/")[3]
            weather_icons.append(asset)
        
        elements = []

        for l in lines:
            columns = l.findChildren("td", recursive=False)
            elements.append({
                "key": columns[0].text,
                "content": columns[1].text
            })

        date_title = section.split("·")

        date_time = dateparser.parse(date_title[0]).date().strftime("%d/%m/%Y")

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

    def check_date(self, date, date_format='%d/%m/%Y'):
        rendezvous_date = datetime.strptime(date, date_format).date()

        today = datetime.today()
        day_dif = (rendezvous_date - today.date()).days

        if today.time() > time(8,0,0):
            if day_dif != 1:
                return self.DateCheck.NO_TOMORROW
            else:
                return self.DateCheck.TOMORROW
        else:
            if day_dif != 0:
                return self.DateCheck.NO_TODAY
            else:
                return self.DateCheck.TODAY

    def format_rendezvous(self, rendezvous, new=False):
        message = ""

        if new:
            message += "❗Mise a jour "

        check_date = self.check_date(rendezvous["date"])
        
        if check_date == self.DateCheck.NO_TOMORROW:
            if new: # Rendezvous is supposed to be new but date does not correspond
                return None
            message += "⚠️ Aucun rendez-vous publié pour demain\n\n"
        if check_date == self.DateCheck.TOMORROW:
            message += "✔️ Rendez-vous pour demain\n\n"
        if check_date == self.DateCheck.NO_TODAY:
            if new: # Rendezvous is supposed to be new but date does not correspond
                return None
            message += "⚠️ Aucun rendez-vous publié pour aujourd'hui\n\n"
        if check_date == self.DateCheck.TODAY:
                message += "✔️ Rendez-vous pour aujourd'hui\n\n"

        message += f"📅  <u>Rendez-vous du {rendezvous['date']}</u>\n\n"
        
        message += f"{rendezvous['content']}"

        message += f"<a href='{self.base_url + self.path_rendez_vous}'>🔗 Consuler le site</a>"
        
        return message

    def format_meteo(self, meteo, new=False):
        # @todo Check meteo format !
        message = ""
        
        emojis = [
            [ "Sunny-128-2510f9e2f167b9304bcebecc7a54d5f3e2ff8b863de8bf0c48a954ec1c5e6c8d.png", "☀️" ],
            [ "Sunny-Period-128-b89aa66c7d6863bb2572d95a5bfc664bd59897681b5c2d8b45026241bc3fb239.png", "🌤" ],
            [ "Sunny-Interval-128-71f71ae3a4c64eab72e509d2d8d4c5103fe2993b9022e16c3bc89e3efefc094c.png", "⛅️" ],
            [ "Overcast-128-124228bb6aefbd6a5e44a2c8dbedc9c50ab35e3929b6ecdd0dea5a73a24a4891.png", "☁️" ]
        ]

        if new:
            message += "❗Mise a jour "

        check_date = self.check_date(meteo["date"])

        if check_date == self.DateCheck.NO_TOMORROW:
            if new: # Rendezvous is supposed to be new but date does not correspond
                return None
            message += "⚠️ Aucune météo publiée pour demain\n"
        if check_date == self.DateCheck.TOMORROW:
            message += "✔️ Météo pour demain\n"
        if check_date == self.DateCheck.NO_TODAY:
            if new: # Rendezvous is supposed to be new but date does not correspond
                return None
            message += "⚠️ Aucune météo publiée pour aujourd'hui\n"
        if check_date == self.DateCheck.TODAY:
            message += "✔️ Météo pour aujourd'hui\n"

        weather_emojis = ""
        if "icons" in meteo:
            for ic in meteo["icons"]:
                weather_emojis += self.emoji_converter(emojis, ic) + " "

        message += f"""
<u>Météo de Tonio du {meteo["date"]}</u> {weather_emojis}{meteo["title"]}
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