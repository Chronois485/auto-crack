import subprocess
import sys

from colored import cprint


def run_command(command):
    try:
        return subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        cprint(f"[-] Command failed: {' '.join(command)}", "red")
        cprint(f"[-] Error output: {e.stderr.strip()}", "red")
        # sys.exit("1")
