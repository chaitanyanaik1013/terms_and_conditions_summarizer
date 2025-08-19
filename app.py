# app.py (Final Asynchronous Version)

import uuid
import subprocess
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)

JOBS_DIR = Path("jobs")
JOBS_DIR.mkdir(exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-job', methods=['POST'])
# In app.py

@app.route('/start-job', methods=['POST'])
def start_job():
    url = request.get_json().get('link')
    if not url:
        return jsonify({'error': 'No link provided'}), 400

    job_id = str(uuid.uuid4())
    job_file = JOBS_DIR / f"{job_id}.json"

    with open(job_file, 'w') as f:
        json.dump({"status": "pending", "url": url, "result": None}, f)

    log_file_path = JOBS_DIR / f"{job_id}.log"

    # --- THIS IS THE CORRECTED PART ---
    # We build the full, absolute paths so the server never gets lost.

    # 1. Define the full path to your project folder.
    project_home = '/home/chaitanyanaik10/terms_and_conditions_summarizer'

    # 2. Define the full path to the Python interpreter inside your virtualenv.
    # You can find this path on your "Web" tab in the "Virtualenv" section.
    python_executable = '/home/chaitanyanaik10/.virtualenvs/my-app-env/bin/python'

    # 3. Define the full path to the worker script we want to run.
    worker_script_path = f'{project_home}/run_worker.py'

    # Now we run the command using these full paths.
    with open(log_file_path, "w") as log_file:
        subprocess.Popen(
            [python_executable, worker_script_path, job_id, url],
            stdout=log_file,
            stderr=log_file
        )
    # --- END OF CORRECTION ---

    return jsonify({
        "job_id": job_id,
        "status_url": url_for('get_status', job_id=job_id)
    })

@app.route('/status/<job_id>')
def get_status(job_id):
    job_file = JOBS_DIR / f"{job_id}.json"
    if not job_file.exists():
        return jsonify({'error': 'Invalid job ID'}), 404
    with open(job_file, 'r') as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(debug=True)