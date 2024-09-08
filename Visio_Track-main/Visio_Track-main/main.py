import os
import pickle
import cvzone
import cv2
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://visiotrack-realtime-default-rtdb.firebaseio.com/",
    "storageBucket":"visiotrack-realtime.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)

# Set the resolution
cap.set(3, 500)
cap.set(4, 500)


imgBackground = cv2.imread('Resources/bg_visiotrack.png')
#Importing the mode images into list.
folderModePath = 'Resources/modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
#print(len(imgModeList))
imgModeList[1] = cv2.resize(imgModeList[1], (429, 583))
imgModeList[2] = cv2.resize(imgModeList[2], (429, 583))

# load the encoding file

print("Loading encode file..")
file = open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
#print(studentIds)
print("Encode file loaded!")


modeType = 0
counter = 0 # to display student data only in the first frame..
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[220:220+480,55:55+640] = img
    imgBackground[90:90+583,815:815+429] = imgModeList[modeType]

    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame,faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)

            #print("matches", matches)
            #print("faceDis",faceDis)

            matchIndex = np.argmin(faceDis)
            #print("MatchIndex",matchIndex)....prints the matched array index value

            if matches[matchIndex]:
                #print(studentIds[matchIndex])
                y1,x2,y2,x1 = faceLoc
                y1, x2, y2, x1=y1*4,x2*4,y2*4,x1*4 #multiply by 4 for bounding box(rectangle) as we resized the image for 1/4th..
                bbox = 55+x1,162+y1, x2-x1,y2-y1
                imgBackground=cvzone.cornerRect(imgBackground, bbox, rt=0) # rt-->rectangle thickness
                id = studentIds[matchIndex]

                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading",(275,400))# to reduce the lag
                    cv2.imshow("Visio Track",imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType=1
        if counter!=0:
            if counter == 1: #download data from firebase storage and display in the information page
                #Get the Data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                #Get the image from the storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)

                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                #resizing the image according to the background
                imgStudent = cv2.resize(imgStudent, (200, 160))

                #updating the attendance data

                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                #print(secondsElapsed)
                if secondsElapsed>30:#convert when you want to take the next attendance into seconds here..
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance']+=1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:#for already marked mode..
                    modeType = 3
                    counter = 0
                    imgBackground[90:90 + 583, 815:815 + 429] = imgModeList[modeType]
            if modeType!=3:

                if 10<counter<20:
                    modeType = 2

                imgBackground[90:90 + 583, 815:815 + 429] = imgModeList[modeType]

                if counter<=10:
                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(870,177),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,0,0),1)


                    cv2.putText(imgBackground, str(studentInfo['major']), (1036, 555),
                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 1)

                    cv2.putText(imgBackground, str(id), (1006,493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,0,0), 1)

                    cv2.putText(imgBackground, str(studentInfo['standing']), (930, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,0,0), 1)

                    cv2.putText(imgBackground, str(studentInfo['year']), (1038, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,0,0), 1)

                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1138, 625),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,0,0), 1)

                    (w,h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1 ,1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground, str(studentInfo['name']), (867+offset, 455),
                                cv2.FONT_HERSHEY_COMPLEX, 0.8, (0, 0, 0), 1)

                    imgBackground[249:249+160, 923:923+200] = imgStudent



            counter += 1

            if counter >= 20:
                counter = 0
                modeType = 0
                studentInfo = []

                imgStudent = []
                imgBackground[90:90 + 583, 815:815 + 429] = imgModeList[modeType]
    else:
        modeType=0
        counter=0
    #cv2.imshow("Webcam", img)
    cv2.imshow("Visio Track",imgBackground)
    cv2.waitKey(1)