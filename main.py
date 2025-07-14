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
        "format": "bestvideo+bestaudio/best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title).80s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "merge_output_format": "mp4",
        "retries": 5,
        "geo_bypass": True,
        "geo_bypass_country": "ID",
        "cookiefile": "cookies.txt",  # ← gunakan cookies jika ada
        "http_headers": {
            "User-Agent": "Mozilla/5.0"
        },
        "concurrent_fragment_downloads": 5,
        "fragment_retries": 5,
    }

@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply(
        "Kirim link dari Instagram / Facebook / TikTok / Google Drive / Mediafire / Mega / Doodstream / YouTube,\n"
        "saya akan download dan kirim ke kamu. 🎬\n\n"
        "Jika kamu ingin akses video YouTube terbatas, silakan kirim file cookies.txt ke bot ini."
    )

@app.on_message(filters.document)
async def save_cookies(_, msg):
    if msg.document.file_name.lower() == "cookies.txt":
        await msg.download(file_name="cookies.txt")
        await msg.reply("✅ File `cookies.txt` berhasil disimpan dan akan digunakan untuk download selanjutnya.")

@app.on_message(filters.private & filters.text)
async def handle(_, msg):
    url = msg.text.strip()
    if not url.startswith("http"):
        return await msg.reply("❌ Link tidak valid.")

    status = await msg.reply("⏬ Mendownload...")

    try:
        with YoutubeDL(get_yt_dlp_opts()) as ydl:
            data = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(data)

        if not os.path.exists(filename):
            return await status.edit("❌ File tidak ditemukan setelah download.")

        await status.edit("🚀 Mengirim ke Telegram...")

        ext = os.path.splitext(filename)[1].lower()
        if ext in (".jpg", ".jpeg", ".png", ".webp"):
            await app.send_photo(
                chat_id=msg.chat.id,
                photo=filename,
                caption="🖼️ Gambar berhasil dikirim"
            )
        elif ext in (".mp4", ".mkv", ".mov", ".avi", ".webm"):
            await app.send_video(
                chat_id=msg.chat.id,
                video=filename,
                caption="🎬 Video berhasil dikirim",
                supports_streaming=True
            )
        else:
            await app.send_document(
                chat_id=msg.chat.id,
                document=filename,
                caption="📎 File berhasil dikirim"
            )

        os.remove(filename)
        await status.edit("✅ Selesai! File dihapus dari server.")

    except Exception as e:
        await status.edit(f"⚠️ Gagal: {e}")

app.run()