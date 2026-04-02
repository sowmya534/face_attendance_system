import cv2
import os
import sqlite3

# Create dataset folder if not exists
if not os.path.exists("dataset"):
    os.makedirs("dataset")

# Create database and users table if not exists
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT
)
""")
conn.commit()
conn.close()

# Insert user into database
def insert_user(user_id, name):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    conn.close()

# Take user input
face_id = input("Enter User ID: ")
name = input("Enter Name: ")

insert_user(face_id, name)

print("Look at the camera and wait...")

# Start camera
cam = cv2.VideoCapture(0)
detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

count = 0

while True:
    ret, img = cam.read()
    if not ret:
        print("Camera not working")
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        count += 1

        # Save face image
        file_name = "dataset/User." + str(face_id) + "." + str(count) + ".jpg"
        cv2.imwrite(file_name, gray[y:y+h, x:x+w])

        # Draw rectangle
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Show count
        cv2.putText(img, "Images Captured: " + str(count), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Capturing Faces', img)

    # Press Enter key to stop or capture 50 images
    if cv2.waitKey(1) == 13 or count >= 50:
        break

cam.release()
cv2.destroyAllWindows()

print("Face data captured successfully for ID:", face_id)