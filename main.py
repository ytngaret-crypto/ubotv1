import asyncio
import logging
import importlib
from pyrogram import Client, idle
from pyrogram.errors import PeerIdInvalid, RPCError

# Import module internal bawaan project
import config
import database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("UBot")

# Exception handler agar error Peer ID Invalid tidak membuat bot crash
def global_exception_handler(loop, context):
    msg = context.get("exception", context.get("message"))
    if "Peer id invalid" in str(msg) or "ID not found" in str(msg):
        logger.warning(f"Mengabaikan Peer ID Invalid: {msg}")
    else:
        logger.error(f"Loop Exception: {msg}")

# Deteksi otomatis Pyrogram Client dari config.py
clients = []
for attr_name in dir(config):
    attr = getattr(config, attr_name)
    if isinstance(attr, Client):
        clients.append(attr)

if not clients:
    import os
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    SESSION_STRING = os.getenv("SESSION_STRING") or os.getenv("HU_STRING") or os.getenv("SESSION")
    
    app = Client(
        "ubot_session",
        api_id=int(API_ID) if API_ID else None,
        api_hash=API_HASH,
        session_string=SESSION_STRING
    )
    clients.append(app)

primary_client = clients[0]

async def safe_cache_dialogs():
    """Memuat cache peer ID secara background."""
    try:
        async for dialog in primary_client.get_dialogs(limit=100):
            _ = dialog.chat.id
    except Exception as e:
        logger.warning(f"Cache dialog error (dilewati): {e}")

async def main():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(global_exception_handler)

    # Inisialisasi database jika ada fungsi khusus di database.py
    for func_name in ["init_db", "setup_db", "init_database", "create_tables"]:
        if hasattr(database, func_name):
            func = getattr(database, func_name)
            try:
                if asyncio.iscoroutinefunction(func):
                    await func()
                else:
                    func()
                logger.info(f"Database ({func_name}) berhasil dijalankan.")
            except Exception as e:
                logger.warning(f"Database init warning: {e}")
            break

    # Start semua Client Pyrogram
    logger.info("Starting UBot Clients...")
    for c in clients:
        await c.start()

    # Load Handlers (.menu, .mute, .ban, dll) setelah Client aktif
    try:
        logger.info("Loading handlers...")
        importlib.import_module("handlers")
        logger.info("Seluruh handler berhasil dimuat!")
    except Exception as e:
        logger.error(f"Gagal memuat handlers: {e}")

    # Pancing cache dialog di background
    asyncio.create_task(safe_cache_dialogs())

    me = await primary_client.get_me()
    logger.info(f"UBot Aktif sebagai {me.first_name} ({me.id})! Silakan tes .menu di Telegram.")

    await idle()

    for c in clients:
        await c.stop()

if __name__ == "__main__":
    asyncio.run(main())
                    
