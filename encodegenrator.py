#We will import the training images that we have and encode them
import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

#Loading the service acccount key from file to gain access to real time database
cred = credentials.Certificate("serviceAccountKey.json")
#Initializing the SDK with loaded service key and the databse/storage url which we have to give in json format
firebase_admin.initialize_app(cred,{
    'databaseURL' : "https://faceattendancerealtime-7e7ea-default-rtdb.firebaseio.com/",
    'storageBucket' : 'faceattendancerealtime-7e7ea.appspot.com'
})  



#Importing the student images 
folderPath = 'Images'
PathList = os.listdir(folderPath)   #This will list all the files presnet inside the path given
studentIds = []
imgList = []

#This loop will convert all the images presnt in Images folder to numpy array and store in imgList
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))   #Images/321654.png (example)
    studentIds.append((os.path.splitext(path)[0])) #This will split the path in 2 parts and return the first part and 
    #since the images are stored in 321654.png format it will be splitted into id and .png and we will get 
    
    filename = f'{folderPath}/{path}'       #created to get the local path of the file using f string
    bucket = storage.bucket()               #creating a reference to default storage for our project
    blob = bucket.blob(filename)            #This creates a new blob in bucket with the same name as filename(blob is just a container also stands for binary large objects)
    blob.upload_from_filename(filename)     #This will upload the file present in file name to storage

print(len(imgList))
print(studentIds)

def findEncodings(imageList):
    encodeList =[]
    for img in imageList:
        #Converting the color scheme as open-cv uses BGR and face_recognition uses RGB
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]    #Getting the encoding of the image, [0] means only 1 face's encdoing will be done(since there is only one face in the image)
        encodeList.append(encode)
    
    return encodeList

print("Encoding Started.....")
encodeListKnown = findEncodings(imgList)    #Known means all the know faces
#print(encodeListKnown)
encodeListKnownWithIds = [encodeListKnown,studentIds]
#print(encodeListKnownWithIds)
print("Encoding Complete")

#We have createad a binary file and open it in write binary mode(wb) and put the 
#encodeListKnwonwithIDs to it
file = open("EncodingFile.p","wb")
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File Saved")