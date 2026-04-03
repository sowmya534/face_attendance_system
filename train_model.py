import cv2
import os
import numpy as np
from PIL import Image

dataset_path = 'dataset'
recognizer = cv2.face.LBPHFaceRecognizer_create()

faces = []
ids = []

for user_id in os.listdir(dataset_path):
    user_folder = os.path.join(dataset_path, user_id)

    for image_name in os.listdir(user_folder):
        img_path = os.path.join(user_folder, image_name)
        img = Image.open(img_path).convert('L')
        img_numpy = np.array(img, 'uint8')

        faces.append(img_numpy)
        ids.append(int(user_id))

recognizer.train(faces, np.array(ids))
os.makedirs("trainer", exist_ok=True)
recognizer.save('trainer/trainer.yml')

print("Model trained successfully")