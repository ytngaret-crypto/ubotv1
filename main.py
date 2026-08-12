import asyncio
import logging

from pyrogram import Client, idle
from pyrogram.enums import ParseMode

from config import Config
from database import Database
from settings_store import SettingsStore

from handlers.commands import register_handlers
from handlers.callbacks import register_callback_handlers
from handlers.message import register_message_handlers
from handlers.settings import register_settings_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("UBot")


async def main():
    cfg = Config.from_env()

    if not cfg.api_id or not cfg.api_hash:
        raise RuntimeError("API_ID/API_HASH belum diisi di Railway Variables.")
    if not cfg.session_string:
        raise RuntimeError("SESSION_STRING belum diisi di Railway Variables.")
    if not cfg.owner_id:
        raise RuntimeError("OWNER_ID belum diisi di Railway Variables.")

    db = Database(cfg.db_path)
    await db.init()
    await db.ensure_owner(cfg.owner_id)

    app = Client(
        "ubot",
        api_id=cfg.api_id,
        api_hash=cfg.api_hash,
        session_string=cfg.session_string,
        parse_mode=ParseMode.HTML,
        workdir=cfg.workdir,
        sleep_threshold=30,
    )

    app.cfg = cfg
    app.db = db
    app.settings = SettingsStore(cfg.db_path)

    # Register every handler BEFORE starting the client.
    register_handlers(app)
    register_callback_handlers(app)
    register_message_handlers(app)
    register_settings_handlers(app)

    log.info("Starting UBot...")
    await app.start()

    try:
        me = await app.get_me()
        log.info("Logged in as %s (%s)", me.first_name, me.id)
        await idle()
    finally:
        await app.stop()
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())
