import eel
import face_recognition
import os, sys
import cv2
import numpy as np
import math
from datetime import date
import time
import os
import os.path

eel.init('Web')

# The Del_Image function takes the Id parameter and deletes the picture saved in that name in Faces folder.
def Del_Image(x):
    os.remove("Faces/"+x+".png")
    # os.remove removes the file in particular location.

# Face_confidence calculates the similarity between the face shown in the active camera and the faces recorded in file.
def face_confidence(face_distance, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + '%'
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + '%'

# The Face Recognition function opens a camera and recognizes the face in thye frame and resposnes.
class FaceRecognition():
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_encodings = []
    known_face_names = []
    process_current_frame = True

    def __init__(self):
        self.encode_faces()

    def encode_faces(self):
        for image in os.listdir('faces'):
            face_image = face_recognition.load_image_file(f"faces/{image}")
            face_encoding = face_recognition.face_encodings(face_image)[0]


            self.known_face_encodings.append(face_encoding)
            self.known_face_names.append(image)

    def run_recognition(self, Type, Id_check):
        video_capture = cv2.VideoCapture(0)
        recog = False

        if not video_capture.isOpened():
            eel.Message("CAMERA IS NOT WORKING !")
            sys.exit('Video source not found...')

        while True:
            ret, frame = video_capture.read()

            # Only process every other frame of video to save time
            if self.process_current_frame:
                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = small_frame[:, :, ::-1]

                # Find all the faces and face encodings in the current frame of video
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame, self.face_locations)

                self.face_names = []
                for face_encoding in self.face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    Rname = "Unknown"
                    recog = False

                    # Calculate the shortest distance to face
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                    best_match_index = np.argmin(face_distances)
                    confidence = face_confidence(face_distances[best_match_index])
                    confidenceCheck = confidence.strip('%')
                   
                    if (matches[best_match_index] and float(confidenceCheck)>95) :
                        l = self.known_face_names[best_match_index]
                        Id_list = l.split(".")
                        Rname = getName(Id_list[0])
                        recog = True

                        if (Type == "Atnd"):
                            Check = Check_Recorded(Id_list[0])
                            if (Check == True):
                                Record_Attendance([],Id_list[0],'P')


                    self.face_names.append(f'{Rname}')

            self.process_current_frame = not self.process_current_frame

            # Display the results
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                top *= 2
                right *= 5
                bottom *= 5
                left *= 3

                # Create the frame with the name
                if recog == True:
                    cv2.rectangle(frame, (left, top), (right, bottom), (69,139,0), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (69,139,0), cv2.FILLED)
                    cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
               
                   

            # Display the resulting image
            cv2.imshow('Face Recognition', frame)

            # Hit 'Enter' on the keyboard to quit!
   
            if cv2.waitKey(1) == ord('\r'):
               
                if(Type == "Add" and recog == False):
                    Save = True
                    Image_name = "Faces/"+Id_check+".png".format()
                    cv2.imwrite(Image_name,frame)

                    img = cv2.imread(Image_name)
                    rgb_img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                    img_encoding = face_recognition.face_encodings(rgb_img)

                    if len(img_encoding) == 0:
                        Del_Image(Id_check)
                        Save = False
                    # If the length of img_encoding is 0 then it means there is no face in the image.
                   
                    # Release handle to the webcam
                    video_capture.release()
                    cv2.destroyAllWindows()

                    if (Save == True):
                        return "Saved"
                    else:
                        return "NO FACE DETECTION"

                if (Type == "Add" and recog == True):
                    # Release handle to the webcam
                    video_capture.release()
                    cv2.destroyAllWindows()
                    return Rname

                if (Type =="Atnd"):
                    video_capture.release()
                    cv2.destroyAllWindows()
                    break

#Loadrec is one of the most ussed function, it returns all the information of record file.
def Loadrec(FileName):
    f = open ("Files/"+FileName,'r')
    lines = f.readlines()
    f.close()

    return lines

# getName function gets the name of the face detected from its image path.
def getName(Id):
    lines = Loadrec("Data.txt")
   
    for i in lines:
        Temp = i.split(',')
        if (Temp[0] == Id):
            return Temp[1]
       
# getName_Attendance function gets the name of the Id given from its attendance file.
def getName_Attendance(Id):
    lines = Loadrec("Attendance.txt")
   
    for i in lines:
        Temp = i.split(',')
        if (Temp[1] == Id):
            return Temp[2]
       
#  getPassword() function get the password from the password file and returns the password.        
def getPassword():
    f = open('Files/Password.txt','r')
    lines = f.readlines()
    f.close()
    P = ''

    for i in lines:
        Temp = i.split('=')
        if (Temp[1] != None):
            P = Temp[1]
            break
    return P

# Lock_file is used to lock the csv file generated for attendance with verified password..      
def Lock_file(File, password):
    from win32com.client.gencache import EnsureDispatch
    from openpyxl import load_workbook
    from pathlib import PurePath
   
    csv_file = EnsureDispatch("Excel.Application")
    wb = csv_file.Workbooks.Open(File)
    csv_file.DisplayAlerts = False
    wb.Visiable = False
    wb.SaveAs(File, FileFormat=51, Password=password, WriteResPassword=password)
    wb.Close()
    csv_file.Quit()
         
# Generate_file is used to create a csv file to record attendance.
def Generate_file(Dates,Fac,Batch, Start_Date, Ends_Date):
    f = open("Attendance/"+Batch+'_'+Fac+'_'+Start_Date+'-'+Ends_Date+".csv",'w')
    String = ""

    for i in Dates:
       String = String + i + ','
       
    f.write('Name,' + 'Unique ID,'  + 'Attendance Rate,' + 'Leaves,' + String + '\n')
    f.close()



# Chech_Recorded function checks whether the face detected person's record has been recorded already or not.
def Check_Recorded(Id):
    lines = Loadrec("Attendance.txt")
    Date = date.today()
    Flag = True

    for i in lines:
        Temp = i.split(',')
        if (Temp[0] == str(Date) and Temp[1] == Id):
            Flag = False
        else:
            Flag = True

    return Flag

# Check_Record_Leave is used by the Add_Leave function to check whether the Id has already been recorded in given dates.
def Check_Recorded_Leave(Id, Dates):
    lines = Loadrec("Attendance.txt")
    Flag = True

    for i in Dates:
        for j in lines:
            Temp = j.split(',')
            if (Temp[0] == i and Temp[1] == Id):
                Flag = False
                eel.Message("THE ID HAS ALREADY BEEN RECORDED PRESENT IN :" + i)
                break
    return Flag
   
# Record_Attendance records the information os the person who's face has been detected.
def Record_Attendance(Dates,Add_Id,Type):
    lines = Loadrec("Data.txt")
    Date = date.today()

    if(Type == 'P'):
        for i in lines:
            Temp = i.split(',')
            if (Temp[0] == Add_Id):
                f = open ("Files/Attendance.txt",'a')
                f.write(str(Date)+','+i.strip('\n')+','+Type+'\n')
                f.close()
               
    elif (Type == 'L'):
        Check = Check_Recorded_Leave(Add_Id,Dates)

        if (Check == True):
            for i in Dates:
                for j in lines:
                    Temp = j.split(',')
                    if (Temp[0] == Add_Id):
                        f = open ("Files/Attendance.txt",'a')
                        f.write(i+','+j.strip('\n')+','+Type+'\n')
                        f.close()
            eel.Message("LEAVE HAS BEEN ADDED")
           
               

# File_Checker checks whether the file exists or not by receiving the file path.
def File_Checker(File,x):
    from pathlib import Path
    p = Path(File)
   
    if p.is_file():
        return
    else:
        if (x==1):
            f = open (File,'w')
            f.close()
        else:
            eel.Messgae("THE RECORD FILE WHERE THE DATA NEEDS TO BE STORED DOES NOT EXIST")
            return False

# The Record_check is used to check whether the record already exists in the file.
def Record_check(Id,File):
    lines = Loadrec("Data.txt")
    found = False

    for i in lines:
        Temp = i.split(',')

        if Temp[0] == Id:
            found = True
            break
       
    if (found == True):
        return True
    else:
        return False
    # If found is True then True is returned which means the record exist in the file.


# Add_Image function is used to take picture of while adding record of the first person.
def Add_Image(x):
    Camera = cv2.VideoCapture(0)
    cv2.namedWindow("IMAGE CAPTURE")

    while True:
        if not Camera.isOpened():
            eel.Message("CAMERA IS NOT WORKING !")
            sys.exit('Video source not found...')
            break
   
        ret,frame= Camera.read()
        path= f"Faces"
        cv2.imshow("CAPTURE IMAGE",frame)

        k = cv2.waitKey(1)

        if k%256 == ord('\r'):
            Image_name = "Faces/"+x+".png".format()
            cv2.imwrite(Image_name,frame)
            break

    Camera.release()
    cv2.destroyAllWindows()

# Open_Cam is used to capture a image when adding a storing a record of a student/teacher.
def Open_Cam(Id):

    f=open("Files/Data.txt",'r')
    lines = f.readlines()

    if lines == []:
        Add_Image(Id)
        return True
    else:
        fr = FaceRecognition()
        Match = fr.run_recognition("Add",Id)

        if (Match == "Saved"):
            return True
        elif Match == "NO FACE DETECTION" :
            eel.Message(Match)
            return False
        else:
            eel.Message(Match+"'S FACE WAS DETECTED")
            return False

# Write_Report is used to write on the csv file for attendance that has been created.
def Write_Report(Dates, Faculty, Batch, Start_Date, Ends_Date, UID, Record):
   
        Generate_file(Dates,Faculty,Batch, Start_Date, Ends_Date)
        f = open ("Attendance/"+Batch+'_'+Faculty+'_'+Start_Date+'-'+Ends_Date+".csv",'a')

        for a in UID:
            Leaves = 0
            Present = 0
            Absent = 0
            NA = 0
            Atted_Per = 0

            String = ""
            Leave_Str = a+'L'

            for b in Record:
                if b[0] == 'N/A':
                    String = String + 'N/A,'
                    NA = NA + 1
                elif (a in b):
                    String  = String + 'P,'
                    Present = Present + 1
                elif (Leave_Str in b):
                    String = String + 'L,'
                    Leaves = Leaves +1
                else:
                    String = String + 'A,'
                    Absent = Absent +1

            Name = getName_Attendance(a)
            Total_Days = len(Dates) - NA
            Present_Days = (Total_Days) - Leaves

            if (Total_Days != 0):
                Atted_Per = ((Present_Days - Absent)/ Total_Days)*100

            f.write( Name + ',' + str(a) + ',' + str(Atted_Per) + '%,' + str(Leaves) + ',' + String +'\n')
               
        f.close()
        F_name = "Attendance/" + Batch+'_'+Faculty+'_'+Start_Date+'-'+Ends_Date+".csv"
        F_path = os.path.abspath(F_name)
        Password = getPassword()
        Lock_file(F_path,Password)
        eel.Message("ATTENDANCE HAS BEEN GENERATED")
   

@eel.expose
# The Add_record function is used to add new record in the file which takes ID, Name, Faculty Name and Batch name.

def Add_record(Id,Name,Fac,Batch):
    Flag = False
    File="Files/Data.txt"
    File_Checker(File,1)
   
    checker = Record_check(Id,File)

    # checker() is called to check whether the record exist or not.        

    if checker == False:
      Pic_taken = Open_Cam(Id)
      if (Pic_taken == True):
          f = open (File,'a')
          f.write(Id + ',' + Name + ',' + Fac + ',' + Batch + '\n')
          f.close()
          eel.Message("THE RECORD HAS BEEN RECORDED")
    else:
        eel.Message("THE ID YOU HAVE ENTERED ALREADY EXISTS")

    # If checker returns false then the camera is opened to store a image by the function Open_Cam.

@eel.expose
# The Del_record function deletres the record that has been requested to delete.
def Del_record (Id, Pass):
    Password = getPassword()

    if (Password == Pass):
        File="Files/Data.txt"
        File_check = File_Checker(File,2)

        if (File_check == False):
            return

        checker = Record_check(Id,File)

        f = open (File,'r')
        lines = f.readlines()
        f.close()

        if checker == True:
            Del_Image(Id)
            f = open (File,'w')
            f.truncate(0)

            for i in lines:
                temp = i.split(',')
                if (temp[0] != Id):
                    f.write(i)
            f.close()
            eel.Message("THE RECORD HAS BEEN DELETED")
        else:
            eel.Message("THE RECORD YOU ARE TRYING TO DELETE DOES NOT EXIST")
    else:
        eel.Message("INCORRECT PASSWORD")

@eel.expose        
# Attendance() is used to take the atttendance.  
def Attendance():
    f=open("Files/Data.txt",'r')
    lines = f.readlines()

    if lines == []:
        eel.Message("THE RECORD IS EMPTY")
    else:
        fr = FaceRecognition()
        fr.run_recognition("Atnd","")

@eel.expose
# Add_Leave() is used to take the add Leave for the student.  
def Add_Leave(Id,Dates):
    checker = Record_check(Id, "Data.txt")
    if (checker == True):
        Record_Attendance(Dates,Id,'L')
    else:
        eel.Message("THE ID YOU HAVE ENTEREND DOES NOT EXIST")
       

@eel.expose
# Generate_Attendance generates the attendace for given date, faculty and batch.
def Generate_attendance(Dates,Faculty,Batch):
    lines = Loadrec("Attendance.txt")
    UID = []
    Record = []
    Start_Date = Dates[0]
    Ends_Date = Dates[-1]

    for i in Dates:
        for j in lines:
            m = j.strip('\n')
            Temp = m.split(',')
            if (Temp[3] == Faculty and Temp[4] == Batch):
                if(Temp[1] not in UID):
                    UID.append(Temp[1])
   
    for K in Dates:
        Atnd = []
       
        for L in lines:
            m = L.strip('\n')
            Temp = m.split(',')
           
            if (Temp[0] == K and Temp[1] in UID):

                if (Temp[5] == 'L'):
                    Atnd.append(Temp[1]+'L')
                else:
                    Atnd.append(Temp[1])

        if(Atnd == []):
            Atnd.append('N/A')
               
        Record.append(Atnd)

    if (UID == []):
        eel.Message("THERE ARE NO RECORDS TO ENTER, PLEASE ENTER CORRECT BATCH AND FACULTY NAME")
    else:
        Write_Report(Dates, Faculty, Batch, Start_Date, Ends_Date, UID, Record)

eel.start('AMS2.0.html', size=(1500,1000))
