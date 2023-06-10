from firebase_admin import db

class FlightEvents:
    def __init__(self) -> None:
        pass
        
    def create(pilotId, locationId, timestamp, notes=""):
        events_ref = db.reference('events')

        new_event_ref = events_ref.push({
            'pilotId': pilotId,
            'locationId': locationId,
            'timestamp': timestamp,
            "notes": notes
        })

        return new_event_ref.key

    def get(id):
        ref = db.reference("events")
        events = ref.get()
        for key, value in events.items():
            if(key == str(id)):
                value["id"] = key
                return value
        return None
    
    def update(id, data={}):
        ref = db.reference("events")
        events = ref.get()
        for key, value in events.items():
            if(key == str(id)):
                ref.child(key).update(data)
                return True
        return False

    def delete(id):      
        ref = db.reference("events")
        events = ref.get()
        for key, value in events.items():
            if(key == str(id)):
                ref.child(key).set({})
                return True
        return False
    