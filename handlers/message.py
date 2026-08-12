from pyrogram import filters


async def _owner(app, message):
    return bool(message.from_user and await app.db.get_role(message.from_user.id) == "owner")


def register_message_handlers(app):
    @app.on_message(filters.text)
    async def messages(_, message):
        if not message.from_user or not message.text:
            return

        text = message.text.strip()

        # Feature buttons in the reply keyboard. Clicking a button is
        # equivalent to sending its dot-command.
        feature_commands = {
            "🚫 Ban": ".ban",
            "♻️ Unban": ".unban",
            "🔇 Mute": ".mute",
            "🔊 Unmute": ".unmute",
            "🛡️ Anti Spam": ".antispam",
            "🤖 Auto Reply": ".autoreply",
            "📢 JaShare": ".jashare",
            "🧠 AI Assistant": ".ai",
            "🌐 Translate": ".translate",
            "👁️ OCR": ".ocr",
            "✍️ Text Generator": ".textgen",
            "🔤 Text Tools": ".texttools",
            "🔳 QR Generator": ".qr",
            "🎵 Song Search": ".song",
            "🎬 Movie Search": ".movie",
            "🎮 Game": ".game",
            "🧩 Quiz": ".quiz",
            "🎲 Random": ".random",
            "💳 Payment": ".pay",
        }
        if text in feature_commands:
            # Re-dispatching through a synthetic command is unnecessary and
            # unsafe for user-generated text; show the exact command syntax
            # instead. Payment is handled below.
            if text == "💳 Payment":
                pass
            elif text in ("🚫 Ban", "♻️ Unban", "🔇 Mute", "🔊 Unmute"):
                await message.reply_text(f"Gunakan <code>{feature_commands[text]}</code> dengan reply atau @username.")
                return
            elif text in ("🤖 Auto Reply", "📢 JaShare", "🛡️ Anti Spam"):
                await message.reply_text(f"Gunakan <code>{feature_commands[text]}</code> sesuai pengaturan fitur.")
                return
            else:
                await message.reply_text(f"Gunakan <code>{feature_commands[text]}</code> untuk fitur ini.")
                return

        # Reply-keyboard menu actions. These are intentionally silent for
        # non-owners when they are owner-only settings actions.
        if text == "⚙️ Settings":
            if not await _owner(app, message):
                return
            await message.reply_text(
                "⚙️ <b>Settings</b>\n\n"
                "Gunakan <code>.settings</code> untuk melihat pengaturan.\n"
                "Gunakan <code>.settings nama_fitur</code> untuk melihat setting fitur."
            )
            return

        if text == "💳 Payment":
            # The payment command itself enforces the configured permission.
            p = await app.db.get_payment(app.cfg.owner_id)
            if not p:
                return
            role = await app.db.get_role(message.from_user.id)
            if role != "owner" and not await app.db.permission(message.chat.id, "payment", role):
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

        # Ignore dot commands here; dedicated command handlers process them.
        if text.startswith("."):
            return

        # Auto-reply is silent unless explicitly allowed.
        role = await app.db.get_role(message.from_user.id)
        feature = "autoreply"
        if role == "owner":
            allowed = True
        elif role in ("admin", "member"):
            allowed = await app.db.permission(message.chat.id, feature, role)
        else:
            allowed = False

        if not allowed:
            return

        response = await app.db.find_autoreply(message.chat.id, text)
        if response:
            await message.reply_text(response)
