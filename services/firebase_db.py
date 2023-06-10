import firebase_admin
from firebase_admin import db, credentials


class FirebaseDb:
    def __init__(self, url, credentials_file) -> None:
        cred = credentials.Certificate(credentials_file)
        firebase_admin.initialize_app(cred, {
            'databaseURL': url
            })
               
    