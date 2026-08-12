import asyncio
import logging
from pyrogram import Client, idle
from pyrogram.errors import PeerIdInvalid, RPCError

# Menggunakan import & variabel sesuai dengan struktur file project Anda
from config import API_ID, API_HASH, SESSION_STRING
from database import init_db
import handlers  # Mengimpor seluruh handler (.menu, .mute, .ban, dll)

# Setup logging agar log Railway tetap informatif
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("UBot")

# Inisialisasi app Pyrogram sesuai konfigurasi ubot Anda
app = Client(
    "ubot_session",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=SESSION_STRING,
    plugins=dict(root="handlers")  # Memastikan seluruh modul handler di-load otomatis
)

# Exception handler agar error Peer ID / KeyError dari Telegram TIDAK membuat bot crash
def global_exception_handler(loop, context):
    msg = context.get("exception", context.get("message"))
    if "Peer id invalid" in str(msg) or "ID not found" in str(msg):
        logger.warning(f"Mengabaikan Peer ID Invalid (Non-fatal): {msg}")
    else:
        logger.error(f"Unhandled Loop Exception: {msg}")

async def safe_load_cache():
    """Memuat cache dialog secara background agar Pyrogram mengenali ID chat."""
    logger.info("Memulai sinkronisasi cache peer...")
    try:
        async for dialog in app.get_dialogs(limit=150):
            _ = dialog.chat.id
        logger.info("Sinkronisasi cache dialog selesai.")
    except (PeerIdInvalid, KeyError, ValueError) as e:
        logger.warning(f"Beberapa peer dilewati saat caching: {e}")
    except Exception as e:
        logger.error(f"Gagal memuat cache dialog: {e}")

async def safe_resolve_log_channels():
    """Mencoba meresolve channel log yang muncul di log error (-1003700496828 & -1003329231332)."""
    target_channels = [-1003700496828, -1003329231332]
    for cid in target_channels:
        try:
            await app.get_chat(cid)
            logger.info(f"Berhasil meresolve channel: {cid}")
        except RPCError as e:
            logger.warning(f"Gagal resolve channel {cid}: {e.MESSAGE}")
        except Exception as e:
            logger.warning(f"Gagal resolve channel {cid}: {e}")

async def main():
    # Set handler error pada asyncio event loop
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(global_exception_handler)

    # Inisialisasi database SQLite/Store internal ubot Anda
    logger.info("Inisialisasi database...")
    if hasattr(init_db, "__call__"):
        await init_db() if asyncio.iscoroutinefunction(init_db) else init_db()

    logger.info("Starting UBot...")
    await app.start()

    me = await app.get_me()
    logger.info(f"Logged in as {me.first_name} ({me.id})")

    # Jalankan caching & pancingan channel log secara async (tanpa mem-blokir bot)
    asyncio.create_task(safe_load_cache())
    asyncio.create_task(safe_resolve_log_channels())

    logger.info("UBot aktif! Seluruh fitur (.menu, .mute, .ban, dll) siap digunakan.")
    await idle()
    await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("UBot dihentikan.")
