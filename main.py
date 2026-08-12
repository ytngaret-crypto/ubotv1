import asyncio
import logging
import importlib
from pyrogram import idle

# Import instance asli dari config.py bawaan zip Anda
from config import pyro_client, bot_client
from database import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("UBot")

# Exception handler global agar error Telegram tidak mematikan task
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
    # Pasang exception handler
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(global_exception_handler)

    # 1. Inisialisasi Database
    try:
        await init_db()
        logger.info("Database berhasil diinisialisasi.")
    except Exception as e:
        logger.warning(f"Database init warning: {e}")

    # 2. Jalankan Client Pyrogram terlebih dahulu
    logger.info("Starting UBot Clients...")
    await pyro_client.start()

    if bot_client:
        try:
            await bot_client.start()
        except Exception as e:
            logger.warning(f"Bot client start warning: {e}")

    # 3. Import Handlers SETELAH Client Aktif (Mencegah Crash Import & Registration Error)
    try:
        logger.info("Loading handlers...")
        importlib.import_module("handlers")
        logger.info("Seluruh handler (.menu, .mute, .ban) berhasil dimuat!")
    except Exception as e:
        logger.error(f"Gagal memuat handlers: {e}")

    # 4. Jalankan pancingan cache dialog secara background
    asyncio.create_task(safe_cache_dialogs())

    me = await pyro_client.get_me()
    logger.info(f"UBot Aktif sebagai {me.first_name} ({me.id})! Coba ketik .menu di Telegram.")
    
    await idle()

    await pyro_client.stop()
    if bot_client:
        await bot_client.stop()

if __name__ == "__main__":
    asyncio.run(main())
            
