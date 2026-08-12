import os
import asyncio
import logging
from pyrogram import Client, idle
from pyrogram.errors import PeerIdInvalid

# Membaca variabel langsung dari Environment Variables Railway Anda
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING") or os.getenv("HU_STRING") or os.getenv("SESSION")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("UBot")

# Inisialisasi Client Pyrogram langsung dari Environment Variables
pyro_client = Client(
    "ubot_session",
    api_id=int(API_ID) if API_ID else None,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    plugins=dict(root="handlers")  # Memuat seluruh fitur di folder handlers otomatis
)

bot_client = None
if BOT_TOKEN:
    bot_client = Client(
        "inline_bot",
        api_id=int(API_ID) if API_ID else None,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

# Exception handler agar error Peer ID Invalid dari Telegram tidak mematikan ubot
def global_exception_handler(loop, context):
    msg = context.get("exception", context.get("message"))
    if "Peer id invalid" in str(msg) or "ID not found" in str(msg):
        logger.warning(f"Mengabaikan Peer ID Invalid: {msg}")
    else:
        logger.error(f"Loop Exception: {msg}")

async def safe_cache_dialogs():
    """Mengisi cache peer ID di SQLite local secara background tanpa mengganggu perintah bot."""
    try:
        async for dialog in pyro_client.get_dialogs(limit=100):
            _ = dialog.chat.id
    except Exception as e:
        logger.warning(f"Cache dialog error (dilewati): {e}")

async def main():
    # Pasang exception handler pada event loop asyncio
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(global_exception_handler)

    # Coba inisialisasi database jika modul database ada
    try:
        from database import init_db
        await init_db()
    except Exception as e:
        logger.warning(f"Database init skipped/warning: {e}")

    logger.info("Starting UBot dari Variables Railway...")
    await pyro_client.start()

    if bot_client:
        try:
            await bot_client.start()
        except Exception as e:
            logger.warning(f"Bot client start warning: {e}")

    # Jalankan pancingan cache dialog secara background
    asyncio.create_task(safe_cache_dialogs())

    logger.info("UBot successfully started! Fitur (.menu, dll) siap digunakan.")
    await idle()

    await pyro_client.stop()
    if bot_client:
        await bot_client.stop()

if __name__ == "__main__":
    asyncio.run(main())
