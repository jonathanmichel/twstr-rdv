from firebase_admin import db

class Pilots:
    def __init__(self) -> None:
        pass
        
    def create(self, telegramId, firstName, lastName):
        pilots_ref = db.reference('pilots')

        pilots_ref.child(str(telegramId)).set({
            'firstName': firstName,
            'lastName': lastName
        })

        return telegramId

    def get(self, id):
        ref = db.reference("pilots")
        pilots = ref.get()
        for key, value in pilots.items():
            if(key == str(id)):
                value["id"] = key
                return value
        return None
    
    def update(self, id, data={}):
        ref = db.reference("pilots")
        pilots = ref.get()
        for key, value in pilots.items():
            if(key == str(id)):
                ref.child(key).update(data)
                return True
        return False
    
    def delete(self, id):      
        ref = db.reference("pilots")
        pilots = ref.get()
        for key, value in pilots.items():
            if(key == str(id)):
                ref.child(key).set({})
                return True
        return False

    def get_byFirstAndLastName(self, firstName, lastName):
        ref = db.reference("pilots")
        pilots = ref.get()
        for key, value in pilots.items():
            if(value["firstName"] == firstName and value["lastName"] == lastName):
                value["id"] = key
                return value
        return None