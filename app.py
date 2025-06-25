from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import re
import os
import qrcode
import blake3
import cv2
import numpy as np
from insightface.app import FaceAnalysis
import time
import traceback
import face_recognition
import shutil

# Flask setup
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULT_FOLDER"] = RESULT_FOLDER
FACE_THRESHOLD = 0.6  # Adjustable threshold for face matching

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Load InsightFace
face_app = FaceAnalysis(name="buffalo_l", providers=['CPUExecutionProvider'])
face_app.prepare(ctx_id=0)

# ---------- Utility Functions ----------

def convert_to_image(file_path):
    try:
        if file_path.endswith(".pdf"):
            images = convert_from_path(file_path, 300)
            if not images:
                raise Exception("PDF conversion failed – no images created")
            image_path = os.path.join(RESULT_FOLDER, "passport_image.png")
            images[0].save(image_path, "PNG")
        else:
            image_path = os.path.join(RESULT_FOLDER, "passport_image.png")
            img = Image.open(file_path)
            img.save(image_path, "PNG")
        print(f"✅ Image saved to {image_path}")
        return image_path
    except Exception as e:
        print(f"❌ Error converting file to image: {e}")
        raise

def extract_passport_number(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    pattern = r'\b[A-Z][0-9]{7}\b'
    match = re.search(pattern, text)
    return match.group(0) if match else None

def generate_blake3_hash(data):
    return blake3.blake3(data.encode()).hexdigest()

def generate_qr_code(data):
    qr_path = os.path.join(RESULT_FOLDER, "passport_qr.png")
    qr = qrcode.make(data)
    qr.save(qr_path)
    return qr_path

def extract_face_with_insight(image_path, save_as="extracted_face.png"):
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Failed to read image at {image_path}")
        return None, None
    faces = face_app.get(img)
    if not faces:
        print(f"❌ No face detected with InsightFace in {image_path}")
        return None, None
    bbox = faces[0].bbox.astype(int)
    x1, y1, x2, y2 = bbox
    face_img = img[y1:y2, x1:x2]
    face_path = os.path.join(RESULT_FOLDER, save_as)
    cv2.imwrite(face_path, face_img)
    return face_path, faces[0].embedding

def extract_face_with_face_recognition(image_path, save_as="face_rec_fallback.png"):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        print(f"❌ No face detected using face_recognition in {image_path}")
        return None, None
    top, right, bottom, left = face_locations[0]
    face_img = image[top:bottom, left:right]
    pil_image = Image.fromarray(face_img)
    save_path = os.path.join(RESULT_FOLDER, save_as)
    pil_image.save(save_path)
    face_encodings = face_recognition.face_encodings(image)
    if not face_encodings:
        return None, None
    return save_path, face_encodings[0]

def capture_real_time_face(save_path): 
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Webcam not accessible")
        return None

    for i in range(0, 11):
        brightness = i / 10.0
        cap.set(cv2.CAP_PROP_BRIGHTNESS, brightness)
        time.sleep(0.3)
        ret, frame = cap.read()
        if ret:
            test_image_path = os.path.join(RESULT_FOLDER, f"test_brightness_{brightness:.1f}.jpg")
            cv2.imwrite(test_image_path, frame)

    cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.6)
    time.sleep(2)

    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None

    cv2.imwrite(save_path, frame)
    return save_path

def verify_real_time_face(doc_face_path):
    real_time_path = os.path.join(RESULT_FOLDER, "real_time_face.png")
    captured = capture_real_time_face(real_time_path)
    if not captured:
        return "Error: Webcam capture failed", None, None, None

    doc_path, doc_embedding = extract_face_with_insight(doc_face_path, "passport_face.png")
    live_path, live_embedding = extract_face_with_insight(real_time_path, "live_face.png")

    fallback_used = False
    if doc_embedding is None or live_embedding is None:
        print("🔁 Fallback to face_recognition")
        doc_path, doc_embedding = extract_face_with_face_recognition(doc_face_path, "passport_face_fallback.png")
        live_path, live_embedding = extract_face_with_face_recognition(real_time_path, "live_face_fallback.png")
        fallback_used = True

    if doc_embedding is None or live_embedding is None:
        return "Face not detected in one or both images", None, None, real_time_path

    distance = np.linalg.norm(doc_embedding - live_embedding)
    confidence = max(0, (1 - distance)) * 100
    confidence = round(confidence, 2)

    result = "Verified ✅" if distance < FACE_THRESHOLD else "Failed to verify ❌"
    if fallback_used:
        result += " (fallback used)"

    print(f"✅ Result: {result} | Distance: {distance:.4f} | Confidence: {confidence}%")
    return result, distance, confidence, real_time_path

# ---------- Main Processing ----------

def process_document(file):
    try:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        print(f"📄 File saved at {file_path}")

        image_path = convert_to_image(file_path)
        print(f"🖼️ Converted image path: {image_path}")

        if not os.path.exists(image_path):
            print("❌ No image was created from the PDF")
            return jsonify({"error": "Failed to convert document to image"}), 500

        passport_number = extract_passport_number(image_path)
        if not passport_number:
            print("❌ Passport number not found")
            return jsonify({"error": "Passport number not found"}), 500

        hash_value = generate_blake3_hash(passport_number)
        print(f"🔐 BLAKE3 Hash of Passport Number: {hash_value}")  # ✅ Added log
        qr_path = generate_qr_code(passport_number)

        extracted_face_path, _ = extract_face_with_insight(image_path, "passport_face.png")
        if not extracted_face_path or not os.path.exists(extracted_face_path):
            print("❌ No face detected in the uploaded document")
            return jsonify({"error": "No face detected in document"}), 500

        verification_result, score, confidence, real_time_face_path = verify_real_time_face(extracted_face_path)

        return jsonify({
            "passport_number": passport_number,
            "hash": hash_value,
            "qr_code": f"http://127.0.0.1:5000/results/{os.path.basename(qr_path)}",
            "face_image": f"http://127.0.0.1:5000/results/passport_face.png",
            "real_time_face": f"http://127.0.0.1:5000/results/live_face.png",
            "verification_result": verification_result,
            "distance_score": score,
            "confidence": f"{confidence}%" if confidence else "N/A"
        })

    except Exception as e:
        print("🔥 Exception occurred:")
        print(traceback.format_exc())
        return jsonify({"error": "Something went wrong during processing"}), 500

# ---------- Flask Routes ----------

@app.route("/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    return process_document(request.files["file"])

@app.route("/results/<filename>")
def get_result_file(filename):
    return send_from_directory(RESULT_FOLDER, filename)

@app.route("/cleanup", methods=["GET"])
def cleanup_folders():
    try:
        shutil.rmtree(UPLOAD_FOLDER)
        shutil.rmtree(RESULT_FOLDER)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(RESULT_FOLDER, exist_ok=True)
        return jsonify({"message": "All uploads and results cleaned up"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------- Run App ----------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
