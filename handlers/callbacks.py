from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from features import FEATURES, CATEGORIES
from ui import main_menu, category_menu, permission_menu, feature_permission_menu


def _menu_text(app):
    return (
        f"🤖 <b>{getattr(app.cfg, 'bot_name', 'UBot')}</b>\n\n"
        "📋 <b>Semua Fitur</b>\n"
        "Pilih fitur dari tombol di bawah:"
    )


def register_callback_handlers(app):
    @app.on_callback_query()
    async def callbacks(_, q: CallbackQuery):
        try:
            uid = q.from_user.id if q.from_user else 0
            role = await app.db.get_role(uid)
            message = q.message
            chat_id = message.chat.id if message else uid
            data = q.data or ""

            if data == "home":
                await q.answer()
                if message:
                    await message.edit_text(_menu_text(app), reply_markup=main_menu())
                return

            if data == "settings":
                if role != "owner":
                    await q.answer("Settings hanya untuk Owner.", show_alert=True)
                    return
                await q.answer()
                if message:
                    await message.edit_text(
                        "⚙️ <b>Settings</b>\n\n"
                        "Gunakan command berikut:\n"
                        "• <code>.settings</code> — daftar setting\n"
                        "• <code>.settings nama_fitur</code> — detail setting\n"
                        "• <code>.set fitur setting nilai</code> — ubah nilai\n"
                        "• <code>.on fitur</code> / <code>.off fitur</code>",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("⬅️ Kembali", callback_data="home")]
                        ]),
                    )
                return

            if data == "perm:menu":
                if role != "owner":
                    await q.answer("Hanya Owner.", show_alert=True)
                    return
                await q.answer()
                if message:
                    await message.edit_text(
                        "🔐 <b>Permission Manager</b>\n\n"
                        "Pilih fitur untuk mengatur akses Admin/Member.",
                        reply_markup=permission_menu(),
                    )
                return

            if data.startswith("cat:"):
                if role != "owner" and not await app.db.permission(chat_id, "dashboard", role):
                    await q.answer("Menu belum diizinkan.", show_alert=True)
                    return
                try:
                    index = int(data.split(":", 1)[1])
                    title = list(CATEGORIES)[index]
                except (ValueError, IndexError):
                    await q.answer("Kategori tidak ditemukan.", show_alert=True)
                    return

                visible = [
                    f for f in CATEGORIES[title]
                    if f in FEATURES and (
                        role == "owner" or await app.db.permission(chat_id, f, role)
                    )
                ]
                await q.answer()
                if message:
                    await message.edit_text(
                        f"<b>{title}</b>",
                        reply_markup=category_menu(title, visible),
                    )
                return

            if data.startswith("pfeat:"):
                if role != "owner":
                    await q.answer("Hanya Owner.", show_alert=True)
                    return

                feature = data.split(":", 1)[1]
                if feature not in FEATURES or feature == "dashboard":
                    await q.answer("Fitur tidak ditemukan.", show_alert=True)
                    return

                admin_allowed = await app.db.permission(chat_id, feature, "admin")
                member_allowed = await app.db.permission(chat_id, feature, "member")

                await q.answer()
                if message:
                    await message.edit_text(
                        f"⚙️ <b>{FEATURES[feature][0]}</b>\n\n"
                        "Atur akses untuk setiap role:",
                        reply_markup=feature_permission_menu(
                            feature, admin_allowed, member_allowed
                        ),
                    )
                return

            if data.startswith("toggle:"):
                if role != "owner":
                    await q.answer("Hanya Owner.", show_alert=True)
                    return

                parts = data.split(":")
                if len(parts) != 3:
                    await q.answer("Data tombol tidak valid.", show_alert=True)
                    return

                _, feature, target_role = parts
                if feature not in FEATURES or feature == "dashboard":
                    await q.answer("Fitur tidak ditemukan.", show_alert=True)
                    return
                if target_role not in ("admin", "member"):
                    await q.answer("Role tidak valid.", show_alert=True)
                    return

                current = await app.db.permission(chat_id, feature, target_role)
                await app.db.set_permission(
                    chat_id, feature, target_role, not current
                )

                admin_allowed = await app.db.permission(chat_id, feature, "admin")
                member_allowed = await app.db.permission(chat_id, feature, "member")

                await q.answer("Permission diperbarui.")
                if message:
                    await message.edit_reply_markup(
                        feature_permission_menu(
                            feature, admin_allowed, member_allowed
                        )
                    )
                return

            if data.startswith("feat:"):
                feature = data.split(":", 1)[1]
                if feature not in FEATURES or feature == "dashboard":
                    await q.answer("Fitur tidak ditemukan.", show_alert=True)
                    return

                if role != "owner" and not await app.db.permission(
                    chat_id, feature, role
                ):
                    await q.answer("Fitur belum diizinkan untuk akunmu.", show_alert=True)
                    return

                label, description = FEATURES[feature]
                command_map = {
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
                command = command_map.get(feature)

                await q.answer()
                if message:
                    extra = f"\n\nCommand: <code>{command}</code>" if command else ""
                    await message.edit_text(
                        f"{label}\n\n"
                        f"{description}"
                        f"{extra}\n\n"
                        "Gunakan tombol di bawah untuk kembali ke semua fitur.",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("⬅️ Semua Fitur", callback_data="home")]
                        ]),
                    )
                return

            await q.answer("Tombol tidak dikenal.", show_alert=True)

        except Exception as exc:
            # Never let a malformed callback kill the dispatcher.
            try:
                await q.answer("Terjadi kesalahan pada menu.", show_alert=True)
            except Exception:
                pass
