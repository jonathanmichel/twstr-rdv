from para import Pilots, Locations, FlightEvents, Flights
from services import FirebaseDb
from datetime import datetime

if __name__ == "__main__" :

    firebase_db_url = "https://twstr-bot-default-rtdb.europe-west1.firebasedatabase.app/"
    firebase_credentials = "twstr-bot-firebase-adminsdk.key.json"
    
    FirebaseDb(firebase_db_url, firebase_credentials)

    pilots = Pilots()
    locations = Locations()
    flights = Flights()
    flightEvents = FlightEvents()

    # pilots.create(648038516, "Jonathan", "Michel")
    # jon = pilots.get(648038516)
    # print(jon)

    # id = locations.create(
    #    "Chalais", 46.27172040675529, 7.513411380269101, 10, Locations.LocationType.LANDING, "Atterrissage Twist'Air"
    # )
    # id = locations.create(
    #    "Vercorin", 46.2594986975, 7.52886659101, 10, Locations.LocationType.LANDING, "Décollage Twist'Air"
    # )
    # id = locations.create(
    #    "Crêt-du-Midi, Est", 46.2290154521, 7.53006109551, 50, Locations.LocationType.TAKEOFF, "Décollage Twist'Air"
    # )
    # id = locations.create(
    #    "Crêt-du-Midi, Sud", 46.2291281506, 7.52848488535, 28, Locations.LocationType.TAKEOFF, "Décollage Twist'Air"
    # )
    # id = locations.create(
    #    "Crêt-du-Midi, Nord3", 46.2295200582, 7.52839678166, 20, Locations.LocationType.TAKEOFF, "Décollage Twist'Air"
    # )

    # locations.update_byName(
    #     "Vercorin", {"type" : str(Locations.LocationType.TAKEOFF)}
    # )

    # locations.printAll()

    # chalais = locations.get_byName("Chalais")
    # print(chalais)

    # vercorin = locations.get_byName("Vercorin")
    # print(vercorin)

    # res = locations.get_byCoordinates(46.27233341643151, 7.513559959478219)
    # print(res)

    # timestamp = datetime.now().timestamp()

    # flightEvents.create(648038516, vercorin["id"], timestamp)
    # flightEvents.create(648038516, chalais["id"], timestamp + 900, "Vol mouvementé")

    jonathan = pilots.get_byFirstAndLastName("Jonathan", "Michel")
    print(jonathan)
    flights = flights.getAllFlightsForPilot(jonathan["id"])
