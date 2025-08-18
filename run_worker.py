import sys
import subprocess
import json
from pathlib import Path

JOBS_DIR = Path("jobs")

def run_job(job_id, url):
    job_file = JOBS_DIR/f"{job_id}.json"

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
            result = subprocess.check_output(
                ["python", "risk_analyzer.py", url],
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            update_job_file("completed", result)

        except subprocess.CalledProcessError as e:
            error_output = f"Script failed with exit code {e.returncode}.\n---Error Log---\n{e.stderr}"
            update_job_file("failed", error_output)
        except Exception as e:
            update_job_file("failed", str(e))      

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    
    job_id_arg = sys.argv[1]
    url_arg = sys.argv[2]
    run_job(job_id_arg, url_arg)