from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import json, os, base64, uuid

app = Flask(__name__)
CORS(app)

DATA_FILE  = "photos.json"
MAX_PHOTOS = 10

def load():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save(photos):
    while len(photos) > MAX_PHOTOS:
        photos.pop()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(photos, f, ensure_ascii=False, indent=2)

@app.route("/api/upload", methods=["POST"])
def upload():
    if "photo" not in request.files:
        return jsonify({"error": "no photo"}), 400

    file   = request.files["photo"]
    ts     = request.form.get("time", datetime.now().strftime("%Y-%m-%d %H:%M"))
    ptype  = request.form.get("type", "triggered")   # "auto" 或 "triggered"

    img_data = base64.b64encode(file.read()).decode("utf-8")
    img_src  = f"data:image/jpeg;base64,{img_data}"

    entry = {
        "id":      str(uuid.uuid4()),
        "src":     img_src,
        "time":    ts,
        "type":    ptype,
        "caption": "",
    }

    photos = load()
    photos.insert(0, entry)

    # 超過上限就刪最舊的
    if len(photos) > MAX_PHOTOS:
        photos = photos[:MAX_PHOTOS]

    save(photos)
    print(f"[上傳] type={ptype} @ {ts}")
    return jsonify({"ok": True, "entry": entry})

@app.route("/api/photos")
def get_photos():
    return jsonify(load())

@app.route("/")
def index():
    return send_from_directory(".", "LETHE.html")

@app.route("/api/like/<photo_id>", methods=["POST"])
def like(photo_id):
    photos = load()
    for p in photos:
        if p.get("id") == photo_id:
            p["likes"] = p.get("likes", 0) + 1
            save(photos)
            return jsonify({"likes": p["likes"]})
    return jsonify({"error": "not found"}), 404

@app.route("/api/comment/<photo_id>", methods=["POST"])
def comment(photo_id):
    text = request.json.get("text", "").strip()
    if not text:
        return jsonify({"error": "empty"}), 400
    photos = load()
    for p in photos:
        if p.get("id") == photo_id:
            if "comments" not in p:
                p["comments"] = []
            p["comments"].append(text)
            save(photos)
            return jsonify({"comments": p["comments"]})
    return jsonify({"error": "not found"}), 404
    
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
