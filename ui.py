from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from features import FEATURES


def _button(label):
    return KeyboardButton(label)


def main_menu():
    """Persistent reply keyboard, matching the user's reference screenshot.
    Each button sends a dot-command so existing command handlers can process it.
    """
    rows = []
    items = list(FEATURES.items())
    for i in range(0, len(items), 2):
        row = []
        for feature, (label, _description) in items[i:i + 2]:
            # Dashboard is a menu item, not a command target.
            if feature == "dashboard":
                continue
            row.append(_button(label))
        if row:
            rows.append(row)

    rows.append([_button("⚙️ Settings"), _button("💳 Payment")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


def _command_for_feature(feature):
    mapping = {
        "ban": ".ban", "unban": ".unban", "mute": ".mute", "unmute": ".unmute",
        "autoreply": ".autoreply", "antispam": ".antispam", "translate": ".translate",
        "ai": ".ai", "ocr": ".ocr", "music": ".song", "movie": ".movie",
        "game": ".game", "quiz": ".quiz", "random": ".random", "textgen": ".textgen",
        "texttools": ".texttools", "jashare": ".jashare", "payment": ".pay", "qr": ".qr",
    }
    return mapping.get(feature, f".{feature}")


def category_menu(title, visible_features=None):
    # Kept for compatibility with older callback code.
    from features import CATEGORIES
    features = list(CATEGORIES.get(title, []))
    if visible_features is not None:
        visible = set(visible_features)
        features = [f for f in features if f in visible]
    rows = []
    for i in range(0, len(features), 2):
        rows.append([_button(FEATURES[f][0]) for f in features[i:i + 2]])
    rows.append([_button(".menu")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


def permission_menu():
    rows = []
    items = list(FEATURES.items())
    for i in range(0, len(items), 2):
        row = []
        for feature, (label, _description) in items[i:i + 2]:
            if feature == "dashboard":
                continue
            row.append(_button(f"⚙️ {feature}"))
        if row:
            rows.append(row)
    rows.append([_button(".menu")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


def feature_permission_menu(feature, admin_allowed, member_allowed):
    return ReplyKeyboardMarkup(
        [
            [_button(f"Admin {feature} {'✅' if admin_allowed else '❌'}"),
             _button(f"Member {feature} {'✅' if member_allowed else '❌'}")],
            [_button("⚙️ Settings")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
