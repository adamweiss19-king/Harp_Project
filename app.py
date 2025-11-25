import os
import re
import json
import uuid
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, abort, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import your existing logic helpers
from logic import (
    get_all_harmonica_names,
    get_harmonica_dict_by_name,
    convert_midi_to_tabs_for_a_set_of_harmonicas,
    convert_midi_to_easy_to_play_tabs_for_a_set_of_harmonicas,
)
# The harmonica data (dictionary of all harmonicas) is provided by your data.py module
try:
    from data import all_harmonicas
except Exception:
    all_harmonicas = {}  # fallback if data.py missing during tests

# -----------------------
# Configuration & helpers
# ---------------------
app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)  # Allow the frontend (even if served from a different host) to make requests.


# Directory where songs (folders + metadata + uploaded files) will be stored.
BASE_DIR = Path(__file__).parent
SONGS_DIR = BASE_DIR / "songs"
SONGS_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "txt", "pdf"}

def slugify(name: str) -> str:
    """
    Create a filesystem-friendly slug from a song name.
    Lowercase, replace spaces with -, remove unwanted chars.
    """
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9\-_\s]", "", s)
    s = re.sub(r"\s+", "-", s)
    if not s:
        s = uuid.uuid4().hex[:8]
    return s

def song_meta_path(slug: str) -> Path:
    return SONGS_DIR / slug / "meta.json"

def load_song_meta(slug: str) -> dict:
    """
    Load song metadata (name, slug, files, notes).
    If missing meta, return an error-like dict with 'error' key.
    """
    p = song_meta_path(slug)
    if not p.exists():
        return {"error": "Song not found"}
    try:
        return json.loads(p.read_text(encoding="utf8"))
    except Exception as e:
        return {"error": f"Failed to read meta: {e}"}

def save_song_meta(meta: dict):
    """
    Persist meta.json for a song. Ensures directory exists.
    """
    slug = meta.get("slug") or slugify(meta.get("name", "untitled"))
    d = SONGS_DIR / slug
    d.mkdir(parents=True, exist_ok=True)
    p = d / "meta.json"
    p.write_text(json.dumps(meta, indent=2), encoding="utf8")

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# -----------------------
# Frontend: index page
# -----------------------
@app.route("/")
def index():
# Flask looks for this file in the 'templates' folder
    return render_template("index.html")
   
# -----------------------
# API: Song management
# -----------------------

@app.route("/api/songs", methods=["GET"])
def api_list_songs():
    """
    Returns a list of songs with {name, slug}.
    Scans the songs directory and reads meta.json from each folder.
    """
    out = []
    for d in SONGS_DIR.iterdir():
        if d.is_dir():
            meta_file = d / "meta.json"
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf8"))
                    out.append({"name": meta.get("name", d.name), "slug": meta.get("slug", d.name)})
                except Exception:
                    out.append({"name": d.name, "slug": d.name})
    return jsonify(out)

@app.route("/api/songs", methods=["POST"])
def api_create_song():
    """
    Create a new song folder and meta.json.
    Body: { "name": "My Song" }
    Returns: { created: true, slug: "my-song" } on success.
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "untitled")
    slug = slugify(name)
    folder = SONGS_DIR / slug
    if folder.exists():
        return jsonify({"created": False, "error": "Song already exists", "slug": slug})
    folder.mkdir(parents=True, exist_ok=True)
    meta = {"name": name, "slug": slug, "files": [], "notes": []}
    save_song_meta(meta)
    return jsonify({"created": True, "slug": slug})

@app.route("/api/songs/<slug>", methods=["GET"])
def api_get_song(slug):
    """
    Return metadata for a song, including files list and notes array.
    """
    meta = load_song_meta(slug)
    if meta.get("error"):
        return jsonify(meta)
    # ensure files list matches folder contents (simple sync)
    folder = SONGS_DIR / slug
    files = []
    if folder.exists():
        for f in folder.iterdir():
            if f.is_file() and f.name != "meta.json":
                files.append(f.name)
    meta["files"] = sorted(list(set(meta.get("files", [])) | set(files)))
    # persist any adjustments
    save_song_meta(meta)
    return jsonify(meta)

@app.route("/api/songs/<slug>/upload", methods=["POST"])
def api_upload_file(slug):
    """
    Save an uploaded file into the song folder.
    Form-data: file=<file>
    Returns { saved: true, filename: "..." } on success.
    """
    meta = load_song_meta(slug)
    if meta.get("error"):
        return jsonify(meta)
    if "file" not in request.files:
        return jsonify({"saved": False, "error": "No file part"})
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"saved": False, "error": "No selected file"})
    filename = secure_filename(f.filename)
    if not allowed_file(filename):
        return jsonify({"saved": False, "error": "File type not allowed"})
    folder = SONGS_DIR / slug
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / filename
    f.save(dest)
    # update meta
    meta_files = meta.get("files", [])
    if filename not in meta_files:
        meta_files.append(filename)
        meta["files"] = meta_files
        save_song_meta(meta)
    return jsonify({"saved": True, "filename": filename})

@app.route("/api/songs/<slug>/files/<path:filename>", methods=["GET"])
def api_get_file(slug, filename):
    """
    Serve file from song folder. Used to preview uploaded images or download files.
    """
    folder = SONGS_DIR / slug
    if not folder.exists():
        abort(404)
    # Security: ensure filename won't escape folder
    safe = secure_filename(filename)
    p = folder / safe
    if not p.exists():
        abort(404)
    return send_from_directory(folder, safe)

@app.route("/api/songs/<slug>/add-notes", methods=["POST"])
def api_add_notes(slug):
    """
    Append manual notes (space/comma separated) to the song.
    Body: { notes: "A4 C5 Bb4" }
    Returns { added: true, notes: [...] }
    """
    meta = load_song_meta(slug)
    if meta.get("error"):
        return jsonify(meta)
    data = request.get_json(silent=True) or {}
    raw = data.get("notes", "")
    if not raw:
        return jsonify({"added": False, "error": "No notes provided"})
    # split by whitespace or comma
    parts = re.split(r"[,\s]+", raw.strip())
    parts = [p for p in parts if p]
    # Append to existing notes
    meta_notes = meta.get("notes", [])
    meta_notes.extend(parts)
    meta["notes"] = meta_notes
    save_song_meta(meta)
    return jsonify({"added": True, "notes": meta_notes})

@app.route("/api/songs/<slug>/generate-notes", methods=["POST"])
def api_generate_notes_with_model(slug):
    """
    Placeholder: generate notes from an uploaded photo using an external model (e.g., Gemini).
    This is intentionally a stub. To integrate:
      - Accept the uploaded image file
      - Send it to your ML API or OCR/ML pipeline
      - Parse returned text to notes and append to song meta
    For now this endpoint returns an explanatory message.
    """
    # Example usage:
    # file = request.files.get('file')
    # if file: save it temporarily, call external API, parse response
    return jsonify({"generated": False, "error": "Model integration not configured. Implement call to Gemini or OCR here."})

@app.route("/api/songs/<slug>/transcribe", methods=["GET"])
def api_transcribe(slug):
    """
    Transcribe the stored notes for a song across all harmonica keys.
    Uses the logic functions convert_midi_to_tabs_for_a_set_of_harmonicas and
    convert_midi_to_easy_to_play_tabs_for_a_set_of_harmonicas.

    Returns JSON:
      { results: [...], easy_results: [...] }
    where each result contains harmonica, tabs, percent, notes, octave_shift.
    """
    meta = load_song_meta(slug)
    if meta.get("error"):
        return jsonify(meta)
    notes = meta.get("notes", [])
    if not notes:
        return jsonify({"error": "Song has no notes to transcribe", "results": [], "easy_results": []})
    # Build a "song" dict compatible with logic functions
    song = {"name": meta.get("name"), "notes": notes}
    # Call the full-coverage conversion across all harmonicas
    try:
        results = convert_midi_to_tabs_for_a_set_of_harmonicas(song, all_harmonicas)
    except Exception as e:
        results = []
    # Call the easy-to-play conversion
    try:
        easy_results = convert_midi_to_easy_to_play_tabs_for_a_set_of_harmonicas(song, all_harmonicas)
    except Exception as e:
        easy_results = []
    # Return both result lists; frontend will sort/display them
    return jsonify({"results": results, "easy_results": easy_results})

# -----------------------
# Run server (dev)
# -----------------------
if __name__ == "__main__":
    # Development server: debug on port 5000
    app.run(debug=True, port=5000)
