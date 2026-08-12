from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from features import FEATURES, CATEGORIES


def main_menu():
    """Main UBot menu. Every category is a real inline button."""
    rows = []
    items = list(CATEGORIES.items())

    # Two category buttons per row, similar to a typical Telegram bot menu.
    for i in range(0, len(items), 2):
        row = []
        for title, _features in items[i:i + 2]:
            row.append(
                InlineKeyboardButton(
                    title,
                    callback_data=f"cat:{list(CATEGORIES).index(title)}",
                )
            )
        rows.append(row)

    rows.append([
        InlineKeyboardButton("⚙️ Permission", callback_data="perm:menu"),
        InlineKeyboardButton("💳 Payment", callback_data="pay:settings"),
    ])
    return InlineKeyboardMarkup(rows)


def category_menu(title, visible_features=None):
    features = list(CATEGORIES.get(title, []))
    if visible_features is not None:
        visible = set(visible_features)
        features = [f for f in features if f in visible]

    rows = []
    for i in range(0, len(features), 2):
        row = [
            InlineKeyboardButton(
                FEATURES[f][0],
                callback_data=f"feat:{f}",
            )
            for f in features[i:i + 2]
        ]
        rows.append(row)

    rows.append([InlineKeyboardButton("⬅️ Kembali", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def permission_menu():
    rows = []
    items = list(FEATURES.items())
    for i in range(0, len(items), 2):
        row = [
            InlineKeyboardButton(
                label[:34],
                callback_data=f"pfeat:{feature}",
            )
            for feature, (label, _description) in items[i:i + 2]
        ]
        rows.append(row)

    rows.append([InlineKeyboardButton("⬅️ Kembali", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def feature_permission_menu(feature, admin_allowed, member_allowed):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                f"Admin {'✅' if admin_allowed else '❌'}",
                callback_data=f"toggle:{feature}:admin",
            ),
            InlineKeyboardButton(
                f"Member {'✅' if member_allowed else '❌'}",
                callback_data=f"toggle:{feature}:member",
            ),
        ],
        [InlineKeyboardButton("⬅️ Permission", callback_data="perm:menu")],
    ])
