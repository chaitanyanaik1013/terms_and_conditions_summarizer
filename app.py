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
def start_job():
    url = request.get_json().get('link')
    if not url:
        return jsonify({'error': 'No link provided'}), 400

    job_id = str(uuid.uuid4())
    job_file = JOBS_DIR / f"{job_id}.json"

    with open(job_file, 'w') as f:
        json.dump({"status": "pending", "url": url, "result": None}, f)
    
    log_file_path = JOBS_DIR / f"{job_id}.log"

    with open(log_file_path, "w") as log_file:
        python_executable = "python3"
        subprocess.Popen(
            [python_executable, "run_worker.py", job_id, url],
            stdout=log_file,
            stderr=log_file
        )

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