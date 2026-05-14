import sys
import subprocess
import os

def main():
    if len(sys.argv) < 3:
        print("Usage: python intake.py <input_file> <output_wav>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_wav = sys.argv[2]

    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist.")
        sys.exit(1)

    print(f"Converting {input_file} to {output_wav}...")
    try:
        # -y: overwrite output files
        # -i: input
        # -ar 44100: audio rate 44.1kHz (standard for many AI models)
        # -ac 2: stereo
        subprocess.run(["ffmpeg", "-y", "-i", input_file, "-ar", "44100", "-ac", "2", output_wav], check=True)
        print("Conversion successful.")
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
