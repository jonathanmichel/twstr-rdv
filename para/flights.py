from firebase_admin import db
from para import Locations
from datetime import datetime

class Flights:
    def __init__(self) -> None:
        pass

    def getAllFlightsForPilot(self, pilotId):
        events = self.getAllEventsForPilot(pilotId)
        for event in events:
            locations = Locations()
            loc = locations.get(event["locationId"])
            
            dt = datetime.fromtimestamp(event["timestamp"])

            print(f"{loc['type']} at {loc['name']} on {dt} - {event['notes']}" )

    def getAllEventsForPilot(self, pilotId):
        ref = db.reference("events")
        events = ref.get()
        flights = []
        for key, value in events.items():
            if(str(value["pilotId"]) == str(pilotId)):
                value["id"] = key
                flights.append(value)
        return flights
