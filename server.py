from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os, json, uuid

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "uploads"
DATA_FILE  = "photos.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)

photos = json.load(open(DATA_FILE, encoding="utf-8")) \
    if os.path.exists(DATA_FILE) else []

def save():
    json.dump(photos, open(DATA_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

@app.route("/api/upload", methods=["POST"])
def upload():
    if "photo" not in request.files:
        return jsonify({"error": "no photo"}), 400
    file = request.files["photo"]
    ts   = request.form.get("time", datetime.now().strftime("%Y-%m-%d %H:%M"))
    name = f"{uuid.uuid4().hex}.jpg"
    file.save(os.path.join(UPLOAD_DIR, name))
    entry = {"src": f"/uploads/{name}", "time": ts,
             "caption": "", "likes": 0, "comments": 0}
    photos.insert(0, entry)
    save()
    print(f"[上傳] {name} @ {ts}")
    return jsonify({"ok": True, "entry": entry})

@app.route("/api/photos")
def get_photos():
    return jsonify(photos)

@app.route("/uploads/<filename>")
def get_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route("/")
def index():
    return send_from_directory(".", "LETHE.html")

if __name__ == "__main__":
    print("[Server] http://localhost:5000")
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
