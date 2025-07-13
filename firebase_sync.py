import pyrebase

# 🔐 Your Firebase Configuration (copied from Firebase Console)
firebase_config = {
    "apiKey": "AIzaSyCHr2tqI8S_VhkjdrXk44Gvki0eu0iFH7I",
    "authDomain": "drawroom-realtime.firebaseapp.com",
    "databaseURL": "https://drawroom-realtime-default-rtdb.firebaseio.com",
    "projectId": "drawroom-realtime",
    "storageBucket": "drawroom-realtime.appspot.com",
    "messagingSenderId": "484427967158",
    "appId": "1:484427967158:web:4f5bbc4eb57bb756249417",
    "measurementId": "G-L4JHC0Y9S9"
}

# 🔗 Initialize connection to Firebase
firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()

# ⬆️ Upload canvas data to Firebase
def upload_canvas_data(room_code, canvas_json):
    db.child("rooms").child(room_code).set(canvas_json)

# ⬇️ Get canvas data from Firebase
def get_canvas_data(room_code):
    data = db.child("rooms").child(room_code).get()
    if data.val():
        return data.val()
    return None
