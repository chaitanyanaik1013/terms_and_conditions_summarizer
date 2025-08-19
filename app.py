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
    
    # Create a unique log file path for this specific job's output
    log_file_path = JOBS_DIR / f"{job_id}.log"

    # Open the log file in write mode
    with open(log_file_path, "w") as log_file:
        # --- THIS IS THE IMPORTANT PART ---
        # We now use the simple "python3" command that we proved works,
        # instead of the full path to the venv.
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