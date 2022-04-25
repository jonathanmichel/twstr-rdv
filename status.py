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
            "last_udpate": "",
            "message": "",
        }

        try:
            with open(self.status_file, "r") as file:
                status = json.load(file)
        except FileNotFoundError as e:
            status = {}

        # If status file is empty or no not exist
        if status == {}:
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

    def get_saved_message(self):
        """
        Get message from the local status file
        """
        return self.get_status()["message"]

    def update_message(self, new_message):
        """
        Update local file with new message
        """
        status = {
            "last_check": self.get_datetime(),
            "message": new_message,
            "last_udpate": self.get_datetime(),
        }

        return self.set_status(status)

    def update_check(self):
        """
        Update local file with new check time
        """
        status = self.get_status()
        status["last_check"] = self.get_datetime()
        return self.set_status(status)




