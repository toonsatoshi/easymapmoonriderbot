/**
 * Cloudflare Worker Dispatcher for Beatsaber Bot
 * 
 * This worker:
 * 1. Validates incoming Telegram webhook requests.
 * 2. Processes audio/document messages to extract file_id.
 * 3. Fetches the file download URL from Telegram.
 * 4. Triggers the GitHub Actions workflow_dispatch.
 */

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    // Basic Telegram Webhook Secret validation (if configured)
    const telegramSecret = request.headers.get("X-Telegram-Bot-Api-Secret-Token");
    if (env.TELEGRAM_WEBHOOK_SECRET && telegramSecret !== env.TELEGRAM_WEBHOOK_SECRET) {
      return new Response("Unauthorized", { status: 401 });
    }

    try {
      const update = await request.json();
      
      if (!update.message) {
        return new Response("OK"); // Not a message update
      }

      const chat_id = update.message.chat.id;
      const message_id = update.message.message_id;
      const text = update.message.text || "";

      // Check if it's a /map command or just an audio file
      const isMapCommand = text.startsWith("/map");
      const audio = update.message.audio || update.message.voice || update.message.document;

      if (!audio && !isMapCommand) {
        return new Response("OK");
      }

      if (isMapCommand && !audio) {
          // Send help message
          await sendTelegramMessage(chat_id, "Send an MP3 or WAV file with the caption `/map` or just send the file to generate a Beat Saber map.", env.TELEGRAM_BOT_TOKEN);
          return new Response("OK");
      }

      // Handle audio file
      let file_id = null;
      let song_title = "Unknown Track";
      let song_artist = "Unknown Artist";

      if (update.message.audio) {
        file_id = update.message.audio.file_id;
        song_title = update.message.audio.title || song_title;
        song_artist = update.message.audio.performer || song_artist;
      } else if (update.message.voice) {
        file_id = update.message.voice.file_id;
      } else if (update.message.document) {
        // Check if it's an audio-like document
        const mime = update.message.document.mime_type || "";
        if (mime.includes("audio") || mime.includes("mpeg") || mime.includes("wav")) {
            file_id = update.message.document.file_id;
            song_title = update.message.document.file_name || song_title;
        }
      }

      if (!file_id) {
        if (isMapCommand) {
            await sendTelegramMessage(chat_id, "Could not find a valid audio file in your message.", env.TELEGRAM_BOT_TOKEN);
        }
        return new Response("OK");
      }

      // Notify user that we are starting
      await sendTelegramMessage(chat_id, "🎵 Audio received! Triggering AI mapping engine... (Est. 5-10 mins)", env.TELEGRAM_BOT_TOKEN);

      // Get file path from Telegram
      const fileResponse = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/getFile?file_id=${file_id}`);
      const fileData = await fileResponse.json();

      if (!fileData.ok) {
        await sendTelegramMessage(chat_id, "❌ Failed to retrieve file from Telegram servers.", env.TELEGRAM_BOT_TOKEN);
        return new Response("OK");
      }

      const audio_url = `https://api.telegram.org/file/bot${env.TELEGRAM_BOT_TOKEN}/${fileData.result.file_path}`;

      // Trigger GitHub Action
      const ghResponse = await triggerGitHubAction(env, {
        telegram_chat_id: chat_id.toString(),
        telegram_message_id: message_id.toString(),
        audio_url: audio_url,
        song_title: song_title,
        song_artist: song_artist,
        difficulty: "5" // Default
      });

      if (!ghResponse.ok) {
        const errorText = await ghResponse.text();
        await sendTelegramMessage(chat_id, `❌ Failed to trigger mapping engine: ${errorText}`, env.TELEGRAM_BOT_TOKEN);
      }

      return new Response("OK");
    } catch (err) {
      console.error(err);
      return new Response("Internal Server Error", { status: 500 });
    }
  }
};

async function sendTelegramMessage(chat_id, text, token) {
  return fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id,
      text,
      parse_mode: "Markdown"
    })
  });
}

async function triggerGitHubAction(env, inputs) {
  const url = `https://api.github.com/repos/${env.GH_OWNER}/${env.GH_REPO}/actions/workflows/${env.GH_WORKFLOW_ID}/dispatches`;
  
  return fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.GH_DISPATCH_TOKEN}`,
      "Accept": "application/vnd.github+json",
      "User-Agent": "Cloudflare-Worker-Dispatcher",
      "X-GitHub-Api-Version": "2022-11-28"
    },
    body: JSON.stringify({
      ref: "main", // or env.GH_REF
      inputs: inputs
    })
  });
}
