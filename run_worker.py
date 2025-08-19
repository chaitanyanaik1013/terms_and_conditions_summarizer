# run_worker.py (Corrected and Improved Version)
import sys
import subprocess
import json
from pathlib import Path

JOBS_DIR = Path("jobs")

def run_job(job_id, url):
    job_file = JOBS_DIR / f"{job_id}.json"

    def update_job_file(status, result=None):
        # This helper function is the same as before
        with open(job_file, 'r+') as f:
            data = json.load(f)
            data['status'] = status
            if result: data['result'] = result
            f.seek(0)
            json.dump(data, f)
            f.truncate()

    update_job_file("running")

    try:
        # THE FIX IS HERE: We are now using "python3"
        result = subprocess.check_output(
            ["python3", "risk_analyzer.py", url],
            stderr=subprocess.PIPE, # Capture stderr to see errors from the script
            text=True,
            encoding='utf-8'
        )
        update_job_file("completed", result)

    except subprocess.CalledProcessError as e:
        # This error handling is improved to be more visible
        error_output = f"The risk_analyzer.py script failed with exit code {e.returncode}.\n"
        error_output += f"--- Error Log ---\n{e.stderr}"
        print(error_output, file=sys.stderr) # Print to stderr for debugging
        update_job_file("failed", error_output)
    except Exception as e:
        # General error handling
        print(f"An unexpected error occurred in run_worker: {e}", file=sys.stderr)
        update_job_file("failed", str(e))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    
    job_id_arg = sys.argv[1]
    url_arg = sys.argv[2]
    run_job(job_id_arg, url_arg)