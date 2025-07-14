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
    "format": "best[ext=mp4]/best",
    "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "merge_output_format": "mp4",
    "retries": 5,
    "geo_bypass": True,
    "geo_bypass_country": "ID",
    "force_ipv4": True,
    "no_check_certificate": True,
    "skip_download": False,
    "socket_timeout": 15,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.youtube.com/",
        "Accept": "*/*",
        "Connection": "keep-alive"
    },
    "concurrent_fragment_downloads": 5,
    "fragment_retries": 5,
}

@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply("Kirim link YouTube, saya akan unduh **tanpa cookies** dan kirim ke kamu. 🚀")

@app.on_message(filters.private & filters.text)
async def handle(_, msg):
    url = msg.text.strip()
    if not url.startswith("http"):
        return await msg.reply("❌ Link tidak valid. Kirim link yang dimulai dengan http atau https.")

    info = await msg.reply("⏬ Mendownload video tanpa cookies...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(data)

        if not os.path.exists(filename):
            return await info.edit("❌ Gagal: file tidak ditemukan setelah download.")

        await info.edit("🚀 Uploading ke Telegram...")
        await app.send_video(
            chat_id=msg.chat.id,
            video=filename,
            caption=data.get("title", "🎬 Video Siap!"),
            supports_streaming=True
        )

        os.remove(filename)
        await info.edit("✅ Selesai! File sudah dihapus dari server.")

    except Exception as e:
        await info.edit(f"⚠️ Gagal download: {e}")

app.run()