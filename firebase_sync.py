import pyrebase
import json

firebase_config = {
  "apiKey": "AIzaSyCHr2tqI8S_VhkjdrXk44Gvki0eu0iFH7I",
  "authDomain": "drawroom-realtime.firebaseapp.com",
  "databaseURL": "https://drawroom-realtime-default-rtdb.firebaseio.com",
  "projectId": "drawroom-realtime",
  "storageBucket": "drawroom-realtime.firebasestorage.app",
  "messagingSenderId": "484427967158",
  "appId": "1:484427967158:web:4f5bbc4eb57bb756249417",
  "measurementId": "G-L4JHC0Y9S9"
}

firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

def upload_canvas_data(room_code, canvas_json):
    """Save canvas JSON data to Firebase for this room"""
    db.child("rooms").child(room_code).set({"canvas": canvas_json})

def get_canvas_data(room_code):
    """Retrieve canvas JSON data from Firebase"""
    result = db.child("rooms").child(room_code).get()
    if result.val():
        return result.val().get("canvas", None)
    return None
