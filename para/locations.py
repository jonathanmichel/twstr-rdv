import geopy.distance
from firebase_admin import db
from enum import Enum

class Locations:
    class LocationType(Enum):
        TAKEOFF = 1
        LANDING = 2

    def __init__(self) -> None:
        pass
        
    def create(self, name, latitude, longitude, radius, type: LocationType, description=""):
        locations_ref = db.reference('locations')

        new_location_ref = locations_ref.push({
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'radius': radius,
            'type': str(type),
            'description': description
        })

        return new_location_ref.key

    def get(self, id):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(key == str(id)):
                value ["ID"] = key
                return value
        return None
    
    def update(self, id, data={}):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(key == str(id)):
                ref.child(key).update(data)
                return True
        return False

    def delete(self, id):      
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(key == str(id)):
                ref.child(key).set({})
                return True
        return False
    
    def get_byName(self, name):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(value["name"] == name):
                value ["id"] = key
                return value
        return None
    
    def update_byName(self, name, data={}):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(value["name"] == name):
                ref.child(key).update(data)
                return True
        return False

    def delete_byName(self, name):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            if(value["name"] == name):
                ref.child(key).set({})
                return True
        return False
    
    def get_byCoordinates(self, latitude, longitude):
        ref = db.reference("locations")
        locations = ref.get()
        for key, value in locations.items():
            distance = self.getDistanceBetweenTwoGPSPoints((value["latitude"], value["longitude"]), (latitude, longitude))
            if (distance <= value["radius"]) :
                return value
        return None
    
    def getDistanceBetweenTwoGPSPoints(self, coords_1, coords_2):
        distance = geopy.distance.geodesic(coords_1, coords_2).meters

        return distance
    
    def getAll(self):
        ref = db.reference("locations")
        locations = ref.get()
        return locations
    
    def printAll(self):
        locations_list = self.getAll()
        for locations_id in  locations_list:
            loc = locations_list[locations_id]
            print(f"{loc['type']} at {loc['name']} ({loc['latitude']}, {loc['longitude']}) - {loc['description']}")
