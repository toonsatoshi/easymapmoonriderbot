import argparse, os, urllib.request, json, urllib.parse

parser = argparse.ArgumentParser()
parser.add_argument("--chat-id")
parser.add_argument("--map-key")
args = parser.parse_args()

token = os.environ.get("TELEGRAM_BOT_TOKEN")
if not token:
    print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
    exit(1)

key = args.map_key

msg = (
    f"✅ *Map generated & uploaded!*\n\n"
    f"🗝 BeatSaver Key: `{key}`\n"
    f"🔗 [View on BeatSaver](https://beatsaver.com/maps/{key})\n"
    f"🌕 [Play on MoonRider](https://moonrider.xyz/?id={key})\n\n"
    f"_Auto-mapped by InfernoSaber via GitHub Actions_"
)

payload = json.dumps({
    "chat_id": args.chat_id,
    "text": msg,
    "parse_mode": "Markdown",
    "disable_web_page_preview": False,
}).encode()

req = urllib.request.Request(
    f"https://api.telegram.org/bot{token}/sendMessage",
    data=payload,
    headers={"Content-Type": "application/json"},
)

try:
    with urllib.request.urlopen(req) as resp:
        print(resp.read().decode())
except Exception as e:
    print(f"Failed to send Telegram message: {e}")
    exit(1)
