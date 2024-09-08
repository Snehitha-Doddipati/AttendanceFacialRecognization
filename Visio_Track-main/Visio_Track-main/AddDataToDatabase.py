import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://visiotrack-realtime-default-rtdb.firebaseio.com/"
})

ref = db.reference('Students')

# adding the data
data = {
    '2103A52064':
        {
            "name":"Abhinandana Polepally",
            "major":"CSE-AI&ML",
            "starting_year":"2021",
            "total_attendance":88,
            "standing":"Good",
            "year":3,
            "last_attendance_time":"2024-04-12 00:50:48"
        },
'2103A52137':
        {
            "name":"Sri Harshini Gumpula",
            "major":"CSE-AI&ML",
            "starting_year":"2021",
            "total_attendance":88,
            "standing":"Good",
            "year":3,
            "last_attendance_time":"2024-04-12 00:50:48"
        },
'2103A52166':
        {
            "name":"Varsha Peddi",
            "major":"CSE-AI&ML",
            "starting_year":"2021",
            "total_attendance":88,
            "standing":"Good",
            "year":3,
            "last_attendance_time":"2024-04-12 00:50:48"
        },
'2103A52055':
        {
            "name":"Dheeraj Manchala",
            "major":"CSE-AI&ML",
            "starting_year":"2021",
            "total_attendance":95,
            "standing":"Good",
            "year":3,
            "last_attendance_time":"2024-04-12 00:50:48"
        },
'2103A52175':
        {
            "name":"Sravani Varanganti",
            "major":"CSE-AI&ML",
            "starting_year":"2021",
            "total_attendance":88,
            "standing":"Good",
            "year":3,
            "last_attendance_time":"2024-04-12 00:50:48"
        },
'2103A52099':
        {
            "name":"Neha Myneni",
            "major":"CSE-AI&ML",
            "starting_year":"2021",
            "total_attendance":60,
            "standing":"Bad",
            "year":3,
            "last_attendance_time":"2024-04-12 00:50:48"
        },
'2103A52087':
        {
            "name":"Nihanth Keesara",
            "major":"CSE-AI&ML",
            "starting_year":"2021",
            "total_attendance":92,
            "standing":"VG",
            "year":3,
            "last_attendance_time":"2024-04-12 00:50:48"
        }

}
#adds data to the real time data base in the format of keys and values, sub keys and sub values.
for key,value in data.items():
    ref.child(key).set(value)
