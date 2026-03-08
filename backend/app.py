
from flask import Flask, request, jsonify, send_from_directory
import os, uuid
from werkzeug.utils import secure_filename
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import sys

print("Imports loaded successfully", file=sys.stderr)

API_TOKEN = os.getenv("API_TOKEN")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
FRONTEND_FOLDER = os.path.join(os.path.dirname(__file__), "..", "caption_generator")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Enable CORS for localhost
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, x-api-key"
    return response

ALLOWED_EXT = {"png","jpg","jpeg","gif"}

# Load BLIP model once at startup
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device available: {device}", file=sys.stderr)

try:
    print("Loading processor...", file=sys.stderr, flush=True)
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    print("✓ Processor loaded", file=sys.stderr, flush=True)
    
    print("Loading model...", file=sys.stderr, flush=True)
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)
    print(f"✓ Model loaded on device: {device}", file=sys.stderr, flush=True)
except Exception as e:
    print(f"✗ Error loading model: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)
    processor = None
    model = None

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXT

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return "", 200

@app.before_request
def check_token():
    if request.endpoint in ("index","serve_static","static_file","upload_image","generate_caption"):
        return
    token = request.headers.get("x-api-key") or request.args.get("api_key")
    if token != API_TOKEN:
        return jsonify({"error":"invalid or missing api token"}), 401

@app.route("/", methods=["GET"])
def index():
    return send_from_directory(FRONTEND_FOLDER, "index.html")

@app.route("/<path:filename>", methods=["GET"])
def serve_static(filename):
    if filename and '.' in filename:
        return send_from_directory(FRONTEND_FOLDER, filename)
    return send_from_directory(FRONTEND_FOLDER, "index.html")

@app.route("/upload", methods=["POST", "OPTIONS"])
def upload_image():
    if request.method == "OPTIONS":
        return "", 200
    if "image" not in request.files:
        return jsonify({"error":"no image part"}), 400
    f = request.files["image"]
    if f.filename == "":
        return jsonify({"error":"no selected file"}), 400
    if not allowed_file(f.filename):
        return jsonify({"error":"file type not allowed"}), 400
    filename = secure_filename(f.filename)
    uid = str(uuid.uuid4())[:8]
    saved = f"{uid}_{filename}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], saved)
    f.save(path)
    return jsonify({"filename": saved, "url": f"/uploads/{saved}"}), 201

@app.route("/uploads/<path:filename>", methods=["GET"])
def static_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/generate_caption", methods=["POST", "OPTIONS"])
def generate_caption():
    if request.method == "OPTIONS":
        return "", 200
    if model is None:
        return jsonify({"error":"model not loaded"}), 500
    data = request.get_json() or {}
    text = data.get("text")
    image = data.get("image")
    if text:
        caption = f"Echo caption: {text[:200]}"
    elif image:
        img_path = os.path.join(app.config["UPLOAD_FOLDER"], image)
        if not os.path.exists(img_path):
            return jsonify({"error":"image not found"}), 404
        raw_image = Image.open(img_path).convert("RGB")
        inputs = processor(raw_image, return_tensors="pt").to(device)
        out = model.generate(**inputs, max_length=30)
        caption = processor.decode(out[0], skip_special_tokens=True)
    else:
        return jsonify({"error":"no input provided; include 'text' or 'image'"}), 400
    return jsonify({"caption": caption})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)