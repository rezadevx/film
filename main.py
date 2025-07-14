import os
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "yt_nocookie_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="downloads",
    workers=16
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

ydl_opts = {
    "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s",
    "format": "best",  # Satu file langsung
    "noplaylist": True,
    "quiet": True,
    "noprogress": True,
    "retries": 5,
    "geo_bypass": True,
    "force_ipv4": True,
    "no_check_certificate": True,
    "skip_download": False,
    "merge_output_format": "mp4",
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://www.youtube.com/"
    }
    # Optional: Pakai proxy publik kalau YouTube diblokir ISP
    # "proxy": "http://your-proxy:port"
}

@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply("Kirim link YouTube/vidio lainnya, saya akan unduh tanpa cookies 😈.")

@app.on_message(filters.private & filters.text)
async def handle(_, msg):
    url = msg.text.strip()
    if not url.startswith("http"):
        return await msg.reply("Link tidak valid!")

    info = await msg.reply("⏬ Downloading video (tanpa cookies)...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(data)

        await info.edit("🚀 Uploading ke Telegram...")
        await app.send_video(
            chat_id=msg.chat.id,
            video=filename,
            caption=data.get("title", "🎬 Video Siap!"),
            supports_streaming=True
        )

        os.remove(filename)
        await info.edit("✅ Selesai tanpa cookies.")

    except Exception as e:
        await info.edit(f"⚠️ Gagal: {e}")

app.run()