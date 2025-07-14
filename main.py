import os
from pyrogram import Client, filters
from yt_dlp import YoutubeDL
from config import API_ID, API_HASH, BOT_TOKEN

app = Client(
    "fast_upload_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="downloads",
    workers=32  # upload & download paralel lebih cepat
)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

ydl_opts = {
    "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s",  # max judul 80 karakter
    "format": "bestvideo+bestaudio/best",               # pilih kualitas tertinggi
    "noplaylist": True,
    "quiet": True,
    "merge_output_format": "mp4",
    "noprogress": True,
    "retries": 3
}

@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply("Kirim link video apa saja (YouTube, Google Drive, Mega, dll). Saya akan download dan kirim secepat kilat 🚀.")

@app.on_message(filters.private & filters.text)
async def handle_link(_, msg):
    url = msg.text.strip()

    if not url.startswith("http"):
        return await msg.reply("❌ Link tidak valid. Harap kirim link video langsung.")

    status = await msg.reply("⏬ Mendownload video...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if not os.path.exists(filename):
            return await status.edit("❌ Gagal: file tidak ditemukan setelah download.")

        caption = info.get("title", "🎬 Video Siap!")
        await status.edit("🚀 Mengirim video ke Telegram...")

        await app.send_video(
            chat_id=msg.chat.id,
            video=filename,
            caption=caption,
            supports_streaming=True
        )

        os.remove(filename)
        await status.edit("✅ Selesai! File sudah dihapus dari server.")

    except Exception as e:
        await status.edit(f"⚠️ Gagal: {e}")

app.run()