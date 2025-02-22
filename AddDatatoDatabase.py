import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred,{
        'databaseURL': "your-database-url"
    })

ref=db.reference("Students")
data = {
        "your-id":
            {
                "name": "student-name",
                "major": "branch-name",
                "starting_year": "starting-year",
                "total_attendance": "total-attendance",
                "standing": "G",
                "year": "year",
            },
        "your-id 2":
            {
                "name": "student-name 2",
                "major": "branch-name 2",
                "starting_year": "starting-year",
                "total_attendance": "total-attendance",
                "standing": "E",
                "year": "year",
            },
}
for key,value in data.items():
    ref.child(key).set(value)