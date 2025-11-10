from flask import Flask, jsonify
from flask_cors import CORS

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
            async function showDetails() {
                const name = document.getElementById('harmonica-select').value;
                const res = await fetch('/api/harmonicas/' + encodeURIComponent(name));
                const details = await res.json();
                document.getElementById('details').textContent = JSON.stringify(details, null, 2);
            }
            window.onload = loadHarmonicas;
        </script>
    </head>
    <body>
        <h1>Select a Harmonica</h1>
        <select id="harmonica-select" onchange="showDetails()"></select>
        <pre id="details"></pre>
    </body>
    </html>
    """

# To run the development server directly from the script
if __name__ == '__main__':
    app.run(debug=True, port=5000) # Flask's default port is 5000

#RUN python app.py