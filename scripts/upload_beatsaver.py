"""
Uploads BSMap.zip to BeatSaver via their REST API.
Endpoint: POST https://api.beatsaver.com/upload
Auth:     Authorization: Bearer <token>
Body:     multipart/form-data  field name: "file"
Response: { "id": "3a9f", ... }

IMPORTANT: BeatSaver rate-limits uploads per account.
You must own a BeatSaver account and generate an API key
at: https://beatsaver.com/profile (Account → API keys tab)
"""
import argparse, os, sys
import urllib.request
import json
from urllib.error import HTTPError

parser = argparse.ArgumentParser()
parser.add_argument("--zip")
parser.add_argument("--out")  # file to write map key into
args = parser.parse_args()

# Use Session Cookie instead of Token
session_cookie = os.environ.get("BEATSAVER_SESSION")
if not session_cookie:
    print("Error: BEATSAVER_SESSION environment variable not set.")
    print("Please follow the README to extract your session cookie from beatsaver.com")
    sys.exit(1)

zip_path = args.zip

BOUNDARY = "------BeatsaverUploadBoundary"

with open(zip_path, "rb") as f:
    zip_data = f.read()

body = (
    f"--{BOUNDARY}\r\n"
    f'Content-Disposition: form-data; name="file"; filename="BSMap.zip"\r\n'
    f"Content-Type: application/zip\r\n\r\n"
).encode() + zip_data + f"\r\n--{BOUNDARY}--\r\n".encode()

req = urllib.request.Request(
    "https://api.beatsaver.com/upload",
    data=body,
    headers={
        "Cookie": f"session={session_cookie}",
        "Content-Type": f"multipart/form-data; boundary={BOUNDARY}",
        "User-Agent": "InfernoBot/1.0",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    map_key = result["id"]
    print(f"Uploaded! Map key: {map_key}")
    if args.out:
        with open(args.out, "w") as f:
            f.write(map_key)
except HTTPError as e:
    print(f"Upload failed: {e.code} {e.reason}")
    print(e.read().decode())
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)
