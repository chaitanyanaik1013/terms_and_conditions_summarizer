# app.py (Final Version with Robust Path Handling)

import uuid
import subprocess
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, url_for

# =====================================================================
# THIS IS THE KEY FIX:
# We will now dynamically find the correct project folder, just like in the worker.
# This ensures app.py and run_worker.py are always in sync.
# =====================================================================
# Get the directory where this app.py file is located.
PROJECT_HOME = Path(__file__).parent.resolve()

# Define the jobs directory to be INSIDE our project folder.
JOBS_DIR = PROJECT_HOME / "jobs"
JOBS_DIR.mkdir(exist_ok=True) # Create it if it doesn't exist.
# =====================================================================

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start-job', methods=['POST'])
def start_job():
    url = request.get_json().get('link')
    if not url:
        return jsonify({'error': 'No link provided'}), 400

    job_id = str(uuid.uuid4())
    # The job file path is now correctly inside the project folder
    job_file = JOBS_DIR / f"{job_id}.json"

    with open(job_file, 'w') as f:
        json.dump({"status": "pending", "url": url, "result": None}, f)
    
    log_file_path = JOBS_DIR / f"{job_id}.log"

    # Define the absolute path to the Python interpreter in your virtualenv
    python_executable = '/home/chaitanyanaik10/.virtualenvs/my-app-env/bin/python'
    
    # Define the absolute path to the worker script
    worker_script_path = PROJECT_HOME / "run_worker.py"
    
    with open(log_file_path, "w") as log_file:
        subprocess.Popen(
            [python_executable, str(worker_script_path), job_id, url],
            stdout=log_file,
            stderr=log_file
        )

    return jsonify({
        "job_id": job_id,
        "status_url": url_for('get_status', job_id=job_id)
    })

@app.route('/status/<job_id>')
def get_status(job_id):
    # The status check now also correctly looks inside the project folder
    job_file = JOBS_DIR / f"{job_id}.json"
    if not job_file.exists():
        # This will now correctly return a 404 until the worker creates the file
        return jsonify({'status': 'pending', 'result': 'Job file not found yet, worker is starting...'}), 200
    with open(job_file, 'r') as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(debug=True)