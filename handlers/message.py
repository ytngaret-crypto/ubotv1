from pyrogram import filters
from features import FEATURES
from security import is_allowed


FEATURE_COMMANDS = {
    "ban": ".ban",
    "unban": ".unban",
    "mute": ".mute",
    "unmute": ".unmute",
    "autoreply": ".autoreply",
    "antispam": ".antispam",
    "translate": ".translate",
    "ai": ".ai",
    "ocr": ".ocr",
    "music": ".song",
    "movie": ".movie",
    "game": ".game",
    "quiz": ".quiz",
    "random": ".random",
    "textgen": ".textgen",
    "texttools": ".texttools",
    "jashare": ".jashare",
    "payment": ".pay",
    "qr": ".qr",
}


async def _owner(app, message):
    return bool(
        message.from_user
        and await app.db.get_role(message.from_user.id) == "owner"
    )


def _button_to_feature(text):
    for feature, (label, _description) in FEATURES.items():
        if feature != "dashboard" and text == label:
            return feature
    return None


def register_message_handlers(app):
    @app.on_message(filters.text)
    async def messages(_, message):
        if not message.from_user or not message.text:
            return

        text = message.text.strip()

        # Tombol menu utama. Hanya fitur yang memang diizinkan untuk user
        # yang boleh menghasilkan respons.
        feature = _button_to_feature(text)
        if feature:
            if not await is_allowed(app, message, feature):
                return

            if feature == "payment":
                p = await app.db.get_payment(app.cfg.owner_id)
                if not p:
                    return
                text_out = "💳 <b>PEMBAYARAN</b>\n\n"
                if p["bank"] and p["account_number"]:
                    text_out += f"🏦 <b>Bank:</b> {p['bank']}\n💳 <b>No. Rek:</b> {p['account_number']}\n"
                if p["account_name"]:
                    text_out += f"👤 <b>A/N:</b> {p['account_name']}\n"
                if p["ewallet"] and p["ewallet_number"]:
                    text_out += f"📱 <b>{p['ewallet']}:</b> {p['ewallet_number']}\n"
                if p["description"]:
                    text_out += f"\n📝 {p['description']}"
                if p["qris_file_id"]:
                    await message.reply_photo(p["qris_file_id"], caption=text_out)
                else:
                    await message.reply_text(text_out)
                return

            command = FEATURE_COMMANDS.get(feature)
            if not command:
                return

            # Fitur yang membutuhkan argumen/target diberi petunjuk singkat.
            if feature in ("ban", "unban", "mute", "unmute"):
                await message.reply_text(
                    f"Gunakan <code>{command}</code> dengan reply pesan "
                    "atau @username."
                )
            elif feature in ("autoreply", "antispam", "jashare"):
                await message.reply_text(
                    f"Gunakan <code>{command}</code> sesuai pengaturan fitur."
                )
            elif feature in ("song", "music"):
                await message.reply_text("Contoh: <code>.song Cincin</code>")
            elif feature == "movie":
                await message.reply_text("Contoh: <code>.movie Avengers</code>")
            elif feature == "random":
                await message.reply_text("Contoh: <code>.random merah|biru|hijau</code>")
            elif feature == "quiz":
                await message.reply_text("Contoh: <code>.quiz pengetahuan umum</code>")
            elif feature == "game":
                await message.reply_text("🎮 Gunakan <code>.game</code> untuk memulai Game Center.")
            else:
                await message.reply_text(f"Gunakan <code>{command}</code> untuk fitur ini.")
            return

        # Settings tetap khusus Owner.
        if text == "⚙️ Settings":
            if not await _owner(app, message):
                return
            await message.reply_text(
                "⚙️ <b>Settings</b>\n\n"
                "Gunakan <code>.settings</code> untuk melihat pengaturan.\n"
                "Gunakan <code>.settings nama_fitur</code> untuk melihat setting fitur."
            )
            return

        # Dot commands diproses oleh handler command masing-masing.
        if text.startswith("."):
            return

        # Auto-reply: diam kecuali fitur memang diizinkan.
        if not await is_allowed(app, message, "autoreply"):
            return

        response = await app.db.find_autoreply(message.chat.id, text)
        if response:
            await message.reply_text(response)
