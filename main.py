import os
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "video_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="downloads",
    workers=16
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_yt_dlp_opts():
    return {
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
        "socket_timeout": 15,
        "force_generic_extractor": True,
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
    await msg.reply("Kirim link Instagram / Facebook / TikTok / Google Drive / Mediafire / Mega / Doodstream, saya akan download dan kirim ke kamu. 🎬")

@app.on_message(filters.private & filters.text)
async def handle(_, msg):
    url = msg.text.strip()
    if not url.startswith("http"):
        return await msg.reply("❌ Link tidak valid.")

    status = await msg.reply("⏬ Mendownload...")

    try:
        # Cek link yang didukung
        supported_sites = ["instagram.com", "facebook.com", "tiktok.com", "drive.google.com", "mediafire.com", "mega.nz", "doodstream.com"]
        if any(site in url for site in supported_sites):
            with YoutubeDL(get_yt_dlp_opts()) as ydl:
                data = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(data)
        else:
            return await status.edit("❌ Situs tidak didukung.")

        if not os.path.exists(filename):
            return await status.edit("❌ File tidak ditemukan setelah download.")

        await status.edit("🚀 Mengirim ke Telegram...")
        await app.send_video(
            chat_id=msg.chat.id,
            video=filename,
            caption="🎬 Video berhasil dikirim",
            supports_streaming=True
        )

        os.remove(filename)
        await status.edit("✅ Selesai! File dihapus dari server.")

    except Exception as e:
        await status.edit(f"⚠️ Gagal: {e}")

app.run()