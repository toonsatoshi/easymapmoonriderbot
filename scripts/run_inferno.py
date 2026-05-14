import argparse
import subprocess
import sys
import os
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio", required=True)
    parser.add_argument("--difficulty", default="5")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    # Assuming inferno is in a subdirectory named 'inferno' as per map.yml
    inferno_path = Path("inferno")
    main_script = inferno_path / "main.py"

    if not main_script.exists():
        print(f"Error: {main_script} not found. Make sure InfernoSaber is cloned into 'inferno' directory.")
        sys.exit(1)

    os.makedirs(args.out, exist_ok=True)

    cmd = [
        "python", str(main_script),
        "--audio", args.audio,
        "--diff", args.difficulty,
        "--out", args.out
    ]

    print(f"Running InfernoSaber: {' '.join(cmd)}")
    try:
        # Note: In the workflow, we should be using the venv's python
        # If this script is run within the venv, 'python' will be the right one.
        subprocess.run(cmd, check=True)
        print("InfernoSaber completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running InfernoSaber: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
