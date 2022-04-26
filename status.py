import json 
from datetime import datetime


class Status:
    """
    Handle status save locally in a json file
    """
    def __init__(self, status_file) -> None:
        self.status_file = status_file

        self.get_status()

    def get_datetime(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def get_status(self):
        """
        Get status from file and create it if not valid/existing
        """
        default_status = {
            "last_check": "",
            "last_forecast_udpate": "",
            "last_rendezvous_udpate": "",
            "rendezvous": "",
            "forecast": {
                "section": ""
            }
        }

        try:
            with open(self.status_file, "r") as file:
                status = json.load(file)
        except FileNotFoundError as e:
            status = {}
        except json.JSONDecodeError as e:
            status = {}

        # If status file is empty or no not exist
        if status == {} or status == "":
            self.set_status(default_status)
            status = default_status

        return status

    def set_status(self, status):
        """
        Write status json file from dictionnary
        """
        with open(self.status_file, "w") as file:
            json.dump(status, file)
            return status

    def get_saved_rendezvous(self):
        """
        Get rendezvous from the local status file
        """
        return self.get_status()["rendezvous"]

    def get_saved_forecast(self):
        """
        Get forecast section from the local status file
        """
        return self.get_status()["forecast"]

    def update_status(self, **kwargs):
        """
        Update local status file with new datas
        """
        status = self.get_status()

        for key, value in kwargs.items():
            status[key] = value

        return self.set_status(status)

    def update_rendezvous(self, new_rendezvous):
        """
        Update local file with new rendez_vous
        """
        return self.update_status(
            last_rendezvous_udpate=self.get_datetime(),
            rendezvous=new_rendezvous,
        )

    def update_forecast(self, forecast):
        """
        Update local file with new forecast
        """
        return self.update_status(
            last_forecast_udpate=self.get_datetime(),
            forecast=forecast,
        )
    
    def update_check(self):
        """
        Update local file with new check time
        """
        return self.update_status(
            last_check=self.get_datetime(),
        )
