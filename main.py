
# Importing libraries
import cv2      #different naming convention for open cv
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

#Loading the service acccount key from file to gain access to real time database
cred = credentials.Certificate("serviceAccountKey.json")
#Initializing the SDK wiht loaded service key and the databse url which we have to give in json format
firebase_admin.initialize_app(cred,{
    'databaseURL' : "https://faceattendancerealtime-7e7ea-default-rtdb.firebaseio.com/",
    'storageBucket' : 'faceattendancerealtime-7e7ea.appspot.com'
})  

bucket = storage.bucket()   #creates a refrence to firebase storage


cap = cv2.VideoCapture(0)   #Creating a videoacpture object that will capture images, 0 is for webcam

#This means that the video frame captured will have a resolution of 640x480
cap.set(3,640)    #Setting the Height of video frame 
cap.set(4,480)      #Setting the Width of video frame


#Creating the GUI
imgBackground = cv2.imread('Resources/background.png')  #This will read an image from a specified path and return
#it in form of numpy array

#Importing the mode images 
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)   #This will list all the files presnet inside the path given
imgModeList = []

#This loop will convert all the images presnt in Resources/Modes folder to numpy array and store in imgModeList
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))   #Resources/Modes/1.png (example)

#print(len(imgModeList))


#Load the encodings from the file:
file = open('EncodingFile.p','rb')          #opening the file in read binary mode
encodeListKnownWithIds = pickle.load(file)  #loading the content  of file in the encodeListKnownWithIds variable
file.close()    #closing the file
encodeListKnown,studentIds = encodeListKnownWithIds #This will put the first index of list in encodeListKnown and
#the second list in studentIds variable
#print(studentIds)   #for testing


modetype = 0
counter = 0
id = -1
imgStudent = []

while True:
    #This method reads one frame from the video stream and returns 2 values: a boolean value based on wether it 
    #was able to capture the image or not and the frame captured in the form of numpy array.
    success, img = cap.read()  

    imgS = cv2.resize(img,(0,0),None,0.25,0.25)     #This is used to resize the image the first argument is the 
    #image to be resized , 2nd is (0,0) which specifies the new size which means that it is not defined here and
    #will be decided by other arguments, 3rd is None which means the aspect ration should not be changed 4th & 5th
    #is the scaling factor fo widht and height which means it will be decreased to 25 perrcen of its orignal size
    imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    #The first method returns a tuple of all the face locations and the second method returns an array of encoding
    #of all faces detected. both of them are iterable

    faceCurrFrame = face_recognition.face_locations(imgS)   #Detetcts the location of face in the image
    encodeCurrFrame =face_recognition.face_encodings(imgS,faceCurrFrame) #Here we are giving boht the image and the
    #location of faces in image, because of we only want to find the encoding of the face and not the whole image


    imgBackground[162:162+480,55:55+640] = img  #This selects a rectangular region of imgBackground with a height
    #of 480 pixels and a width of 640 pixels, starting from the top-left corner at coordinates (55, 162). AND
    #INSERTS IMG THERE
    imgBackground[44:44+633,808:808+414] = imgModeList[modetype] #overlaying mode images on imgBackground

    if faceCurrFrame:
        for encodeFace, faceLoc in zip(encodeCurrFrame,faceCurrFrame):
            #This function compares the encoding of the unkown photo with the list that contains the encodings of the
            #known faces and returns the boolean value corresponding to who it mathces with. takes 2 args
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace) #Lesser distance means that it mathces
            #returns the euclidean distance of the unkown encoding compared to the known encoding
            # print("matches",matches)
            # print("FaceDis",faceDis)

            matchIndex = np.argmin(faceDis) 
            # print("match index ",matchIndex)

            if(matches[matchIndex]):
                #print("Known Face Detected")
                #print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc        #coordinates of face location(top,right,bottom,left)
                y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4     #Multiplying by 4 as we decreased the screen size by 25%
            
                #coordinates of bbox, as the image detetcted is inside the imgBackground we have to give the +51 and 
                #the +162 cause thats where the detected image is in imgBackground. x2-x1 is the width and y2-y1 is h
                bbox = 55 + x1 ,  162+y1, x2-x1, y2-y1  
                imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0)  #It returns the image with a block drawn on
                #it
                id = studentIds[matchIndex]


                if (counter==0):
                    counter = 1
                    modetype = 1
        
        if counter != 0:
            if counter ==1 :
                #get the data
                studentInfo  = db.reference(f'Students/{id}').get()     #creates a refrence to given path and gets the info

                #get the image from the storage
                blob = bucket.get_blob(f'Images/{id}.png')  #gets the the file from the specified path from the storage
                # download_as_string() downloads the contents of blob as byte buffer(sequence of bytes) and then frombuffer
                #creates a numpy array of 8 bit unsinged integers
                array = np.frombuffer(blob.download_as_string(),np.uint8)   
                print(studentInfo)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                #update the data
                #We create a datetime.datetime object parsed from the input string
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")

                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed>30:
                    ref = db.reference(f'Students/{id}')    #reference of student id in database
                    studentInfo['total_attendance'] +=1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])   #we get the reference of child
                    #total_attendace of student id and update it
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modetype = 3
                    imgBackground[44:44+633,808:808+414] = imgModeList[modetype]
                    counter = 0

            if modetype!=3:
                if 10<counter<20:
                    modetype =2 
                    imgBackground[44:44+633,808:808+414] = imgModeList[modetype]

                if (counter <= 10):
                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imgBackground,str(studentInfo['major']),(1006,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(imgBackground,str(id),(1006,493),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(imgBackground,str(studentInfo['standing']),(910,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgBackground,str(studentInfo['year']),(1025,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgBackground,str(studentInfo['starting_year']),(1125,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)

                    #returns width, height and one other thing that we dont need
                    (w,h),_ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1) 

                    offset = (414 - w)//2    #414 is width of image, w is width of text when we subtract it we have distance of
                    #the area remaining from the border to text so we divide it by 2 and now we have the distance from the border
                    #to text

                    cv2.putText(imgBackground,str(studentInfo['name']),(808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)

                    imgBackground[175:175+216,909:909+216] = imgStudent


                counter += 1

                if counter>20:
                    counter = 0
                    modetype = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44+633,808:808+414] = imgModeList[modetype]
    else:
        counter = 0
        modetype = 0


    #This will display the captured image and takes 2 arguments, a string that
    #that is the tittle of the window in whhic image is displayed and the image
    cv2.imshow("Face Attendace",imgBackground)

    key = cv2.waitKey(1)  # waits indefinitely until a key is pressed
    # Check if the 'q' key was pressed
    if key == ord('q'):
        # Destroy the window
        break