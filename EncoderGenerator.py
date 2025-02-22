import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import pandas as pd

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "Add your database URL",
    'storageBucket': "Add your storage bucket url",
})

# Importing student images
folderPath = 'Images'
PathList = os.listdir(folderPath)
print(PathList)
imageList = []
studentIds=[]
for path in PathList:
    imageList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

    fileName=f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)


    #print(os.path.splitext(path)[0])
print(studentIds)

def findencodings(imageslist):
    encodeList = []
    for img in imageslist:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
print("Encoding Started...")
encodeListKnown = findencodings(imageList)
encodeListKnownWithIds =[encodeListKnown,studentIds]
#print(encodeListKnown)
print("Encoding Done")

file = open("EncodeFile.p", "wb")
pickle.dump(encodeListKnownWithIds,file)
file.close()
print("File Saved")