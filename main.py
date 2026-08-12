import asyncio
import logging
from pyrogram import idle

# Memanggil pyro_client & bot_client dari config.py asli Anda 
# (config.py Anda sudah membaca Variabel Railway & mereset handler secara benar)
from config import pyro_client, bot_client
from database import init_db
import handlers  # Memastikan seluruh handler (.menu, .mute, dll) terdaftar ke pyro_client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("UBot")

# Mencegah error 'Peer id invalid' mematikan dispatcher Pyrogram
def global_exception_handler(loop, context):
    msg = context.get("exception", context.get("message"))
    if "Peer id invalid" in str(msg) or "ID not found" in str(msg):
        logger.warning(f"Abaikan Peer ID Invalid: {msg}")
    else:
        logger.error(f"Loop Exception: {msg}")

async def safe_cache_dialogs():
    """Mengisi cache peer ID di SQLite local secara background."""
    try:
        async for dialog in pyro_client.get_dialogs(limit=100):
            _ = dialog.chat.id
    except Exception as e:
        logger.warning(f"Cache dialog error (dilewati): {e}")

async def main():
    # Pasang exception handler agar error Telegram tidak menghentikan bot
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(global_exception_handler)

    # Inisialisasi Database bawaan Anda
    await init_db()

    logger.info("Starting UBot...")
    await pyro_client.start()

    if bot_client:
        try:
            await bot_client.start()
        except Exception as e:
            logger.warning(f"Bot client start warning: {e}")

    # Jalankan pancingan cache secara background agar tidak menghalangi perintah masuk
    asyncio.create_task(safe_cache_dialogs())

    logger.info("UBot successfully started! Coba ketik .menu di Telegram.")
    await idle()

    await pyro_client.stop()
    if bot_client:
        await bot_client.stop()

if __name__ == "__main__":
    asyncio.run(main())
    
