import cv2
import sqlite3
from attendance import mark_attendance

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load users from database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
conn.close()

names = {user[0]: user[1] for user in users}

cam = cv2.VideoCapture(0)
attendance_marked = False

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.2, 5)

    for (x, y, w, h) in faces:
        id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

        if confidence < 70:
            name = names[id]
            mark_attendance(id, name)
            text = f"{name} - Attendance Marked"
            attendance_marked = True
        else:
            text = "Unknown"

        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.putText(img, text, (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    cv2.imshow("Face Attendance", img)

    if attendance_marked:
        cv2.waitKey(2000)
        break

    if cv2.waitKey(1) == 27:
        break

cam.release()
cv2.destroyAllWindows()