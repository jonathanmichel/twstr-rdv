import geopy.distance
from firebase_admin import db
from enum import Enum

class Locations:
    class LocationType(Enum):
        TAKEOFF = "Takeoff"
        LANDING = "Landing"

    def __init__(self) -> None:
        pass
        
    def create(name, latitude, longitude, radius, type: LocationType, description=""):
        locations_ref = db.reference('locations')

        new_location_ref = locations_ref.push({
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius,
            'type': type.value,
            'description': description
        })

        return new_location_ref.key

    def get(id):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(key == str(id)):
                value ["ID"] = key
                return value
        return None
    
    def update(id, data={}):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(key == str(id)):
                ref.child(key).update(data)
                return True
        return False

    def delete(id):      
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(key == str(id)):
                ref.child(key).set({})
                return True
        return False
    
    def get_byName(name):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(value["name"] == name):
                value ["id"] = key
                return value
        return None
    
    def update_byName(name, data={}):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(value["name"] == name):
                ref.child(key).update(data)
                return True
        return False

    def delete_byName(name):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(value["name"] == name):
                ref.child(key).set({})
                return True
        return False
    
    def get_byCoordinates(latitude, longitude):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            distance = Locations.getDistanceBetweenTwoGPSPoints((value["latitude"], value["longitude"]), (latitude, longitude))
            if (distance <= value["radius"]) :
                return value
        return None
    
    def getDistanceBetweenTwoGPSPoints(coords_1, coords_2):
        distance = geopy.distance.geodesic(coords_1, coords_2).meters

        return distance
    
    def getAll():
        ref = db.reference("locations")
        locations = ref.get()
        return locations
    
    def printAll():
        locations_list = Locations.getAll()
        for locations_id in  locations_list:
            loc = locations_list[locations_id]
            print(type(loc["type"]))
            print(f"{loc['type']} at {loc['name']} ({loc['latitude']}, {loc['longitude']}) - {loc['description']}")
