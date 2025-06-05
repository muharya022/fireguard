import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import cv2

# Muat model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'optimized_model.h5')
model = load_model(model_path)

# Label kelas
labels = ['fire', 'nofire', 'smoke', 'smokefire']

def predict_fire(img_path):
    input_shape = model.input_shape[1:3]
    print(f"[DEBUG] Membuka gambar: {img_path}")
    img = image.load_img(img_path, target_size=input_shape)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    pred = model.predict(img_array)[0]

    predicted_index = np.argmax(pred)
    predicted_label = labels[predicted_index]
    confidence = pred[predicted_index]

    print(f"[DEBUG] Prediksi: {pred}, Label: {predicted_label}, Confidence: {confidence:.2f}")

    return f"{predicted_label} ({confidence:.2f})"

def predict_fire_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "❌ Gagal membuka video"

    input_shape = model.input_shape[1:3]
    detected_label = "nofire"
    max_confidence = 0.0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_resized = cv2.resize(frame, input_shape)
            frame_array = np.expand_dims(frame_resized, axis=0) / 255.0
            pred = model.predict(frame_array)[0]
            predicted_index = np.argmax(pred)
            confidence = pred[predicted_index]

            if confidence > max_confidence:
                max_confidence = confidence
                detected_label = labels[predicted_index]

            # Break early if fire/smoke detected with high confidence
            if detected_label != "nofire" and confidence > 0.9:
                break
    finally:
        cap.release()

    return f"🎥 Video Deteksi: {detected_label} ({max_confidence:.2f})"
