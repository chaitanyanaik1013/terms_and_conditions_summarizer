# app.py

import uuid
import subprocess
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)

# Define the directory where job status files will be stored
JOBS_DIR = Path("jobs")
JOBS_DIR.mkdir(exist_ok=True) # Create the directory if it doesn't exist

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')


@app.route('/start-job', methods=['POST'])
def start_job():
    """
    This is Conversation #1.
    It receives a URL, creates a background job, and immediately returns a job ID.
    This function should be very fast.
    """
    # Get the URL from the request sent by the browser's JavaScript
    url = request.get_json().get('link')
    if not url:
        return jsonify({'error': 'No link provided'}), 400

    # 1. Create a unique ID for this job
    job_id = str(uuid.uuid4())
    job_file = JOBS_DIR / f"{job_id}.json"

    # 2. Create the initial job status file to track its progress
    with open(job_file, 'w') as f:
        json.dump({"status": "pending", "url": url, "result": None}, f)
    
    # 3. Start the background worker script (the "Project Manager").
    #    `subprocess.Popen` is NON-BLOCKING. It starts the script and immediately moves on.
    #    Make sure the python executable path is correct for your system.
    python_executable = "venv/bin/python" # For Linux/macOS
    # python_executable = "venv\\Scripts\\python.exe" # For Windows
    subprocess.Popen([python_executable, "run_worker.py", job_id, url])

    # 4. Immediately return the job ID so the browser knows how to check the status later.
    return jsonify({
        "job_id": job_id,
        "status_url": url_for('get_status', job_id=job_id) # e.g., /status/some-uuid
    })


@app.route('/status/<job_id>')
def get_status(job_id):
    """
    This is Conversation #2.
    The browser's JavaScript will call this URL repeatedly to get status updates.
    This function should also be very fast.
    """
    # Find the job file that corresponds to the provided ID
    job_file = JOBS_DIR / f"{job_id}.json"

    if not job_file.exists():
        return jsonify({'error': 'Invalid job ID'}), 404
    
    # Open the file, read the contents, and return it to the browser
    with open(job_file, 'r') as f:
        return jsonify(json.load(f))


# This part is only for running the app with the `python app.py` command.
# If you use `flask run` or Gunicorn, this is not used.
if __name__ == '__main__':
    app.run(debug=True)