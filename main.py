import pickle
import cv2
import os
import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "add-your-database-url",
    'storageBucket': "add-your-storage-bucket-url"
})

bucket=storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
imgBackground = cv2.imread('Resources/gg.png')

# Importing the mode images into a list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imageModeList = []
for path in modePathList:
    imageModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imageModeList))

#Load the encoding file
print("Loading Encode File...")
file=open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
#print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent=[]
while True:
    success, img = cap.read()
    imgS= cv2.resize(img,(0,0),None, 0.25,0.25)
    imgS= cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[204:204 + 480, 97:97 + 640] = img
    imgBackground[53:53 + 758, 883:883 + 540] = imageModeList[modeType]

    if faceCurFrame:

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDistances = face_recognition.face_distance(encodeListKnown,encodeFace)
            #print("matches",matches)
            #print("facedis",faceDistances)


            matchIndex = np.argmin(faceDistances)
            #print("matchIndex",matchIndex)

            if matches[matchIndex]:
                #print("Known Face Detected")
                #print(studentIds[matchIndex])
                y1,x2,y2,x1 = faceLoc
                y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
                bbox = 80+x1,180+y1,x2-x1,y2-y1
                imgBackground=cvzone.cornerRect(imgBackground,bbox,rt=0)
                id = studentIds[matchIndex]
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading...",(275,650))
                    cv2.imshow('Face_Attendance', imgBackground)
                    cv2.waitKey(1)
                    counter=1
                    modeType=1
        if counter!= 0:
            if counter ==1:
                studentInfo=db.reference(f'Students/{id}').get()
                print(studentInfo)
                #Get the Image from the storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array=np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent=cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                #update data of attendance
                datetimeObject=datetime.strptime(studentInfo['last_attendance_time'],'%Y-%m-%d %H:%M:%S')
                secondsElapsed=(datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed>30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance']+=1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    modeType=3
                    counter=0
                    imgBackground[53:53 + 758, 883:883 + 540] = imageModeList[modeType]
            if modeType!=3:
                if 10<counter<20:
                    modeType=2
                imgBackground[53:53 + 758, 883:883 + 540] = imageModeList[modeType]

                if counter <=10:
                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(955,162),
                                cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1150, 620),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1100, 548),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['standing']), (1050, 750),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (100,100,100), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1200, 750),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (100,100,100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1350, 750),
                                cv2.FONT_HERSHEY_COMPLEX, 0.7, (100, 100,100), 1)
                    (w, h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset=(340-w)//2
                    cv2.putText(imgBackground,str(studentInfo['name']),(1025+offset,508),
                                cv2.FONT_HERSHEY_COMPLEX,0.7,(50,50,50),1)
                    imgBackground[210:210+262,1034:1034+236]= imgStudent
                counter+=1
                if counter >=20:
                    counter=0
                    modeType=0
                    studentInfo= []
                    imgStudent= []
                    imgBackground[53:53 + 758, 883:883 + 540] = imageModeList[modeType]
    else:
        modeType=0
        counter=0
    cv2.imshow('Face_Attendance', imgBackground)
    key=cv2.waitKey(1)
    if key == ord('q'):  # Check if 'q' key is pressed
        break  # Break out of the loop if 'q' is pressed
cv2.destroyAllWindows()