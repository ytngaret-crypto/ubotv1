from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from features import FEATURES, CATEGORIES
from ui import main_menu, category_menu, permission_menu, feature_permission_menu


def register_callback_handlers(app):
    @app.on_callback_query()
    async def callbacks(_, q: CallbackQuery):
        try:
            uid = q.from_user.id
            role = await app.db.get_role(uid)
            chat_id = q.message.chat.id if q.message else uid
            data = q.data or ""

            if data == "home":
                if role != "owner" and not await app.db.permission(chat_id, "dashboard", role):
                    await q.answer("Menu belum diizinkan.", show_alert=False)
                    return
                await q.message.edit_text(
                    "🤖 <b>UBot</b>\n\nPilih fitur:",
                    reply_markup=main_menu(),
                )
                await q.answer()
                return

            if data == "perm:menu":
                if role != "owner":
                    await q.answer("Hanya Owner.", show_alert=True)
                    return
                await q.message.edit_text(
                    "⚙️ <b>Permission Manager</b>\n\n"
                    "Default semua fitur adalah <b>Owner Only</b>.\n"
                    "Pilih fitur untuk mengatur akses Admin/Member.",
                    reply_markup=permission_menu(),
                )
                await q.answer()
                return

            if data.startswith("cat:"):
                if role != "owner" and not await app.db.permission(chat_id, "dashboard", role):
                    await q.answer("Menu belum diizinkan.", show_alert=False)
                    return
                try:
                    index = int(data.split(":", 1)[1])
                    title = list(CATEGORIES)[index]
                except (ValueError, IndexError):
                    await q.answer("Menu tidak ditemukan.", show_alert=True)
                    return

                visible = [
                    f for f in CATEGORIES[title]
                    if role == "owner" or await app.db.permission(chat_id, f, role)
                ]
                if not visible:
                    await q.answer("Belum ada fitur yang diizinkan.", show_alert=False)
                    return

                await q.message.edit_text(
                    f"<b>{title}</b>",
                    reply_markup=category_menu(title, visible),
                )
                await q.answer()
                return

            if data.startswith("pfeat:"):
                if role != "owner":
                    await q.answer("Hanya Owner.", show_alert=True)
                    return
                feature = data.split(":", 1)[1]
                if feature not in FEATURES:
                    await q.answer("Fitur tidak ditemukan.", show_alert=True)
                    return

                await q.message.edit_text(
                    f"⚙️ <b>{FEATURES[feature][0]}</b>\n\nPilih akses:",
                    reply_markup=feature_permission_menu(
                        feature,
                        await app.db.permission(chat_id, feature, "admin"),
                        await app.db.permission(chat_id, feature, "member"),
                    ),
                )
                await q.answer()
                return

            if data.startswith("toggle:"):
                if role != "owner":
                    await q.answer("Hanya Owner.", show_alert=True)
                    return

                parts = data.split(":")
                if len(parts) != 3:
                    return
                _, feature, target_role = parts
                if feature not in FEATURES or target_role not in ("admin", "member"):
                    await q.answer("Data permission tidak valid.", show_alert=True)
                    return

                current = await app.db.permission(chat_id, feature, target_role)
                await app.db.set_permission(chat_id, feature, target_role, not current)

                await q.message.edit_reply_markup(
                    feature_permission_menu(
                        feature,
                        await app.db.permission(chat_id, feature, "admin"),
                        await app.db.permission(chat_id, feature, "member"),
                    )
                )
                await q.answer("Permission diperbarui.")
                return

            if data == "pay:settings":
                if role != "owner":
                    await q.answer("Hanya Owner.", show_alert=True)
                    return
                await q.message.edit_text(
                    "💳 <b>Payment Settings</b>\n\n"
                    "Gunakan <code>.setpay</code> untuk mengatur data pembayaran.",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("⬅️ Kembali", callback_data="home")]
                    ]),
                )
                await q.answer()
                return

            if data.startswith("feat:"):
                feature = data.split(":", 1)[1]
                if feature not in FEATURES:
                    await q.answer("Fitur tidak ditemukan.", show_alert=True)
                    return
                if role != "owner" and not await app.db.permission(chat_id, feature, role):
                    await q.answer("Fitur belum diizinkan.", show_alert=True)
                    return
                await q.answer(f"{FEATURES[feature][0]} siap digunakan.")

        except Exception:
            # Never crash the update dispatcher because of one bad callback.
            try:
                await q.answer("Terjadi kesalahan pada menu.", show_alert=True)
            except Exception:
                pass
