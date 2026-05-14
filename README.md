# Beatsaber Bot: TGRAM → INFERNO → BEATSAVER

Automated Beat Saber map generation using AI, triggered by Telegram and processed via GitHub Actions.

## Components
- **Telegram Bot**: User interface for sending audio files.
- **Cloudflare Worker**: Dispatcher that receives Telegram webhooks and triggers GitHub Actions.
- **GitHub Actions**: Runs [InfernoSaber](https://github.com/fred-brenner/InfernoSaber---BeatSaber-Automapper) to generate maps.
- **BeatSaver API**: Final destination for the generated maps.
- **MoonRider**: Instant play link provider.

## Setup Instructions

### 1. Telegram Bot
1. Create a bot via [@BotFather](https://t.me/BotFather).
2. Save the `TELEGRAM_BOT_TOKEN`.
3. (Optional) Set a `TELEGRAM_WEBHOOK_SECRET` for security.

### 2. GitHub Repository
1. Create a new repository and push this code.
2. Go to **Settings > Secrets and variables > Actions**.
3. Add the following **Secrets**:
   - `TELEGRAM_BOT_TOKEN`: Your bot token.
   - `BEATSAVER_TOKEN`: Your BeatSaver API key (Get it from [beatsaver.com/profile](https://beatsaver.com/profile)).
4. (Optional) Create a **Fine-grained Personal Access Token (PAT)** with `Actions: Read & Write` scope and add it as a secret if you want the worker to trigger it without using your main credentials (though the worker needs this PAT as its own environment variable).

### 3. Cloudflare Worker
1. Install Wrangler: `npm install -g wrangler`.
2. Update `wrangler.jsonc` with your `GH_OWNER` and `GH_REPO`.
3. Deploy the worker: `wrangler deploy`.
4. Set the following **Environment Variables** in the Cloudflare Dashboard for the worker:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_WEBHOOK_SECRET` (if used)
   - `GH_DISPATCH_TOKEN`: A PAT with `workflow` scope.
   - `GH_OWNER`
   - `GH_REPO`
   - `GH_WORKFLOW_ID`: `map.yml`
5. Set the Telegram Webhook:
   `https://api.telegram.org/bot<TOKEN>/setWebhook?url=<WORKER_URL>&secret_token=<OPTIONAL_SECRET>`

### 4. BeatSaver
1. Log in to [beatsaver.com](https://beatsaver.com).
2. Go to **Account > API Keys** and generate a new key.
3. Add this key to your GitHub Secrets as `BEATSAVER_TOKEN`.

## Usage
Send an MP3 or WAV file to your bot. It will automatically:
1. Acknowledge the receipt.
2. Trigger the AI mapping process.
3. Upload the result to BeatSaver.
4. Send you a MoonRider link to play it immediately!
