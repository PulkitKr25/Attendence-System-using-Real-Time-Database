# AddDataToDatabase.py




#Connecting to the real time firebase database
#The Firebase Admin SDK, specifically, is a server-side SDK that allows developers to interact with Firebase 
#services from a server environment, such as a Node.js server or a Python script.
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#Loading the service acccount key from file to gain access to real time database
cred = credentials.Certificate("serviceAccountKey.json")
#Initializing the SDK with loaded service key and the databse url which we have to give in json format(initializing a connection with firebase)
firebase_admin.initialize_app(cred,{
    'databaseURL' : "https://faceattendancerealtime-7e7ea-default-rtdb.firebaseio.com/"
})  

ref = db.reference('Students')  #This will create a reference to Students directory to read from and write to.It 
#will create the directory if it doesn't already exist.

data = {
    '321654' :
    {
            "name": "Mark Zuckerberg",
            "major": "Robotics",
            "starting_year": 2019,
            "total_attendance": 7,
            "standing": "G",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34"
    },
    '852741' :
    {
            "name": "Emily Blunt",
            "major": "Economics",
            "starting_year": 2020,
            "total_attendance": 12,
            "standing": "B",
            "year": 3,
            "last_attendance_time": "2022-12-11 00:54:34"
    },
    '963852' :
    {
            "name": "Elon Musk",
            "major": "Physics",
            "starting_year": 2021,
            "total_attendance": 12,
            "standing": "B",
            "year": 2,
            "last_attendance_time": "2022-12-11 00:54:34"
    },
}


#this will create directories if they dont already exist

for key,value in data.items():
    ref.child(key).set(value)       #ref variable is a reference to parent node in real time database. the child
    #method creates a reference to a specific child node with key as its name ,the set method is called on the 
    #child reference this will write the given value in the child node