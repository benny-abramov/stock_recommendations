"""Auto Git Sync Daemon.

Watches the repository for file changes, automatically stages,
commits, and pushes to GitHub with debounce protection.
"""

import subprocess
import time
from datetime import datetime
import os
import sys

# Directory to watch (project root)
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
CHECK_INTERVAL_SECONDS = 5
DEBOUNCE_SECONDS = 5

def run_cmd(cmd):
    try:
        res = subprocess.run(
            cmd,
            cwd=REPO_DIR,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)

def has_changes():
    code, out, _ = run_cmd("git status --porcelain")
    if code != 0:
        return False, []
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    return len(lines) > 0, lines

def auto_commit_and_push(changed_files):
    # Summarize up to 3 changed files in commit message
    file_names = [f.split()[-1] for f in changed_files[:3]]
    files_summary = ", ".join(file_names)
    if len(changed_files) > 3:
        files_summary += f" and {len(changed_files) - 3} more"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"auto-sync: update {files_summary} ({timestamp})"

    print(f"[{timestamp}] Changes detected: {files_summary}", flush=True)
    print("  -> Staging files...", flush=True)
    run_cmd("git add .")

    print(f"  -> Committing: {commit_msg}", flush=True)
    run_cmd(f'git commit -m "{commit_msg}"')

    print("  -> Pushing to origin main...", flush=True)
    code, out, err = run_cmd("git push origin main")
    if code == 0:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Successfully pushed to GitHub!\n", flush=True)
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Push warning / retry next cycle: {err or out}\n", flush=True)

def main():
    print("=" * 65, flush=True)
    print("  Auto-Git-Sync Daemon Active", flush=True)
    print(f"  Watching: {REPO_DIR}", flush=True)
    print(f"  Check interval: {CHECK_INTERVAL_SECONDS}s | Debounce: {DEBOUNCE_SECONDS}s", flush=True)
    print("=" * 65, flush=True)

    last_change_time = None

    while True:
        try:
            changed, files = has_changes()
            if changed:
                now = time.time()
                if last_change_time is None:
                    last_change_time = now
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Modifications detected, debouncing {DEBOUNCE_SECONDS}s...", flush=True)
                elif now - last_change_time >= DEBOUNCE_SECONDS:
                    auto_commit_and_push(files)
                    last_change_time = None
            else:
                last_change_time = None

            time.sleep(CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            print("\nAuto-Git-Sync stopped.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
