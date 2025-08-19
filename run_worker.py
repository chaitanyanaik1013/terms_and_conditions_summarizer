# run_worker.py (Final Corrected Version with Absolute Paths)
import sys
import subprocess
import json
from pathlib import Path

# Define the jobs directory relative to this script's location
PROJECT_HOME = Path(__file__).parent.resolve()
JOBS_DIR = PROJECT_HOME / "jobs"

def run_job(job_id, url):
    job_file = JOBS_DIR / f"{job_id}.json"

    def update_job_file(status, result=None):
        with open(job_file, 'r+') as f:
            data = json.load(f)
            data['status'] = status
            if result: data['result'] = result
            f.seek(0)
            json.dump(data, f)
            f.truncate()

    update_job_file("running")

    try:
        # --- THIS IS THE CORRECTED PART ---
        # 1. Get the path to the python interpreter that is running THIS script.
        #    This ensures we use the correct one from the virtualenv.
        python_executable = sys.executable
        
        # 2. Build the full, absolute path to the risk_analyzer.py script.
        analyzer_script_path = PROJECT_HOME / "risk_analyzer.py"

        # 3. Use the full paths in the command.
        result = subprocess.check_output(
            [python_executable, str(analyzer_script_path), url],
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        # --- END OF CORRECTION ---

        update_job_file("completed", result)

    except subprocess.CalledProcessError as e:
        error_output = f"The risk_analyzer.py script failed with exit code {e.returncode}.\n"
        error_output += f"--- Error Log ---\n{e.stderr}"
        print(error_output, file=sys.stderr)
        update_job_file("failed", error_output)
    except Exception as e:
        print(f"An unexpected error occurred in run_worker: {e}", file=sys.stderr)
        update_job_file("failed", str(e))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    
    job_id_arg = sys.argv[1]
    url_arg = sys.argv[2]
    run_job(job_id_arg, url_arg)