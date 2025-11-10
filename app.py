import os
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

# ensure uploads folder exists
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# You still import your logic and database just like before
from logic import get_all_harmonica_names, get_harmonica_dict_by_name

# Create the Flask app instance
app = Flask(__name__)

# --- IMPORTANT: Configure CORS ---
# This is the Flask way to allow your frontend to make requests.
CORS(app)

# --- Define your API Endpoints ---
# This is equivalent to FastAPI's @app.get("/api/harmonicas")

@app.route("/api/harmonicas", methods=['GET'])
def list_harmonicas():
    """Returns a JSON array of all harmonica names."""
    names = get_all_harmonica_names()
    # In Flask, you use the `jsonify` function to properly format the response
    return jsonify(names)

# This is equivalent to FastAPI's @app.get("/api/harmonicas/{harmonica_name}")
# Notice the <variable_name> syntax for path parameters.

@app.route("/api/harmonicas/<harmonica_name>", methods=['GET'])
def get_harmonica_details(harmonica_name):
    """Returns details of a specific harmonica by name."""
    details = get_harmonica_dict_by_name(harmonica_name)
    if details:
        return jsonify(details)
    else:
        return jsonify({"error": "Harmonica not found"}), 404

@app.route("/api/submit-notes", methods=['POST'])
def submit_notes():
    """Accepts JSON { notes: 'A4 C5 ...' } or { notes: ['A4','C5'] } from manual input."""
    data = request.get_json(silent=True) or {}
    notes = data.get('notes')
    if isinstance(notes, str):
        # split on whitespace or commas
        notes = re.split(r'[\s,]+', notes.strip())
    if not isinstance(notes, list):
        return jsonify({"error": "invalid notes format"}), 400
    return jsonify({"received_notes": notes})

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

@app.route("/")
def index():
    return """
    <html>
    <head>
        <title>Harmonica Selector</title>
        <script>
            async function loadHarmonicas() {
                const res = await fetch('/api/harmonicas');
                const names = await res.json();
                const select = document.getElementById('harmonica-select');
                select.innerHTML = '';
                names.forEach(name => {
                    const option = document.createElement('option');
                    option.value = name;
                    option.text = name;
                    select.appendChild(option);
                });
            }

            function toggleInput(kind) {
                document.getElementById('manual-area').style.display = kind === 'manual' ? 'block' : 'none';
                document.getElementById('file-area').style.display = kind === 'file' ? 'block' : 'none';
            }

            async function submitManual() {
                const raw = document.getElementById('manual-notes').value;
                const res = await fetch('/api/submit-notes', {
                    method: 'POST',
                    headers: {'Content-Type':'application/json'},
                    body: JSON.stringify({notes: raw})
                });
                const j = await res.json();
                document.getElementById('input-result').textContent = JSON.stringify(j, null, 2);
            }

            async function submitFile() {
                const f = document.getElementById('note-file').files[0];
                if (!f) return alert('Choose a file first');
                const fd = new FormData();
                fd.append('file', f);
                const res = await fetch('/api/upload', { method: 'POST', body: fd });
                const j = await res.json();
                document.getElementById('input-result').textContent = JSON.stringify(j, null, 2);
            }

            async function showDetails() {
                const name = document.getElementById('harmonica-select').value;
                const res = await fetch('/api/harmonicas/' + encodeURIComponent(name));
                const details = await res.json();
                document.getElementById('details').textContent = JSON.stringify(details, null, 2);
            }

            window.onload = function() {
                loadHarmonicas();
                toggleInput('manual');
            }
        </script>
    </head>
    <body>
        <h1>Select a Harmonica</h1>
        <select id="harmonica-select" onchange="showDetails()"></select>
        <pre id="details"></pre>

        <h2>Input Choices</h2>
        <label><input type="radio" name="input-kind" checked onchange="toggleInput('manual')"> Manual notes</label>
        <label><input type="radio" name="input-kind" onchange="toggleInput('file')"> Upload file</label>

        <div id="manual-area" style="margin-top:10px;">
            <textarea id="manual-notes" rows="4" cols="50" placeholder="Type notes, e.g. A4 C5 Bb4"></textarea><br/>
            <button onclick="submitManual()">Submit Manual Notes</button>
        </div>

        <div id="file-area" style="display:none; margin-top:10px;">
            <input id="note-file" type="file" accept=".txt"/><br/>
            <button onclick="submitFile()">Upload File</button>
        </div>

        <h3>Result</h3>
        <pre id="input-result"></pre>
    </body>
    </html>
    """

# To run the development server directly from the script
if __name__ == '__main__':
    app.run(debug=True, port=5000) # Flask's default port is 5000

#RUN python app.py