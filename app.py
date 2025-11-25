import os
import re
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Uploads folder configuration
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# SONGS folder (each song gets its own folder with metadata + files)
SONGS_FOLDER = os.path.join(os.getcwd(), 'songs')
os.makedirs(SONGS_FOLDER, exist_ok=True)


def _slug_name(name: str) -> str:
    """Return a filesystem-safe slug for a song name."""
    s = str(name or '').lower()
    s = re.sub(r'[^a-z0-9_\-]+', '_', s)
    s = s.strip('_')
    return s or 'untitled'

def _song_folder(slug: str) -> str:
    return os.path.join(SONGS_FOLDER, slug)

def _meta_path(slug: str) -> str:
    return os.path.join(_song_folder(slug), 'song.json')

def _load_meta(slug: str):
    path = _meta_path(slug)
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as fh:
        return json.load(fh)

def _save_meta(slug: str, meta: dict):
    folder = _song_folder(slug)
    os.makedirs(folder, exist_ok=True)
    with open(_meta_path(slug), 'w', encoding='utf-8') as fh:
        json.dump(meta, fh, indent=2)


# You still import your logic and database just like before
from logic import get_all_harmonica_names, get_harmonica_dict_by_name, process_song_for_harmonicas
from data import all_harmonicas

# Create the Flask app instance
app = Flask(__name__)

# --- IMPORTANT: Configure CORS ---
# This is the Flask way to allow your frontend to make requests.
CORS(app)

# --- Define your API Endpoints ---
# gets all harmonica names
@app.route("/api/harmonicas", methods=['GET'])
def list_harmonicas():
    """Returns a JSON array of all harmonica names."""
    names = get_all_harmonica_names()
    # In Flask, you use the `jsonify` function to properly format the response
    return jsonify(names)

# get details of a specific harmonica
@app.route("/api/harmonicas/<harmonica_name>", methods=['GET'])
def get_harmonica_details(harmonica_name):
    """Returns details of a specific harmonica by name."""
    details = get_harmonica_dict_by_name(harmonica_name)
    if details:
        return jsonify(details)
    else:
        return jsonify({"error": "Harmonica not found"}), 404

# simple in-memory store for the last submitted notes
LAST_SUBMITTED_NOTES = None

# Endpoint to submit notes manually
@app.route("/api/submit-notes", methods=['POST'])
def submit_notes():
    """Accepts JSON { notes: 'A4 C5 ...' } or { notes: ['A4','C5'] } from manual input and stores them."""
    global LAST_SUBMITTED_NOTES
    data = request.get_json(silent=True) or {}
    notes = data.get('notes')
    if isinstance(notes, str):
        # split on whitespace or commas
        notes = re.split(r'[\s,]+', notes.strip())
    if not isinstance(notes, list):
        return jsonify({"error": "invalid notes format"}), 400

    LAST_SUBMITTED_NOTES = notes
    return jsonify({"received_notes": notes, "stored": True})

# Endpoint to upload a file
@app.route("/api/upload", methods=['POST'])
def upload_file():
    """Accepts a file upload (form field 'file') and saves it to ./uploads."""

    uploaded = request.files.get('file')
    if not uploaded:
        return jsonify({"error": "no file uploaded"}), 400

    filename = secure_filename(uploaded.filename) or 'uploaded_file'
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    # avoid overwriting existing files by adding a numeric suffix
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(save_path):
        filename = f"{base}_{counter}{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        counter += 1

    uploaded.save(save_path)
    return jsonify({"saved": True, "filename": filename, "path": save_path})

@app.route("/api/transcribe", methods=['GET', 'POST'])
def transcribe_to_harmonica():
    """
    Transcribe notes to harmonica tabs.
    - POST with JSON { notes: 'A4 C5' } or { notes: ['A4','C5'] } -> transcribe those notes
    - GET -> transcribe the last notes submitted via /api/submit-notes
    Optional query params:
        ?song_name=NameOfSong
        ?easy=true    (use easy_to_play harmonicas)
    """
    easy = request.args.get('easy', 'false').lower() == 'true'
    song_name = request.args.get('song_name', 'uploaded_song')

    # choose notes: POST body overrides; otherwise use last submitted
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        notes = data.get('notes')
        if isinstance(notes, str):
            notes = re.split(r'[\s,]+', notes.strip())
        if not isinstance(notes, list):
            return jsonify({"error": "invalid notes format"}), 400
    else:
        # GET -> use stored notes
        global LAST_SUBMITTED_NOTES
        notes = LAST_SUBMITTED_NOTES
        if not notes:
            return jsonify({"error": "no notes submitted yet (use /api/submit-notes)"}), 400

    # call existing logic to process notes for all harmonicas
    results = process_song_for_harmonicas(song_name, notes, all_harmonicas, easy_to_play=easy)
    return jsonify({"song": song_name, "notes": notes, "results": results})

@app.route("/")
def index():
    with open("index.html", "r") as f:
        return f.read()

# To run the development server directly from the script
if __name__ == '__main__':
    app.run(debug=True, port=5000) # Flask's default port is 5000

#RUN python app.py