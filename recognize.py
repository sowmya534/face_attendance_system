import cv2
import sqlite3
from attendance import mark_attendance

print("Starting face recognition...")

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

cam = cv2.VideoCapture(0)

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        user_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

        if confidence < 60:
            cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
            result = cursor.fetchone()

            if result:
                name = result[0]
                mark_attendance(user_id, name)
            else:
                name = "Unknown"
        else:
            name = "Unknown"

        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.putText(img, str(name), (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    cv2.imshow('Face Recognition - Press Enter to Exit', img)

    if cv2.waitKey(1) == 13:
        break

cam.release()
cv2.destroyAllWindows()