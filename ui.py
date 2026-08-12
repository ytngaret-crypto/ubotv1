from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from features import FEATURES, CATEGORIES


def _btn(text: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=data)


def _rows(items, columns=2):
    return [
        [_btn(text, data) for text, data in items[i:i + columns]]
        for i in range(0, len(items), columns)
    ]


def main_menu():
    """Full UBot menu.

    This is intentionally an INLINE keyboard. Every registered feature is
    displayed here; it is not generated from command handlers.
    """
    items = [
        (label, f"feat:{feature}")
        for feature, (label, _description) in FEATURES.items()
        if feature != "dashboard"
    ]

    rows = _rows(items, 2)
    rows.append([
        _btn("⚙️ Settings", "settings"),
        _btn("🔐 Permissions", "perm:menu"),
    ])
    rows.append([_btn("🔄 Refresh", "home")])
    return InlineKeyboardMarkup(rows)


def menu_for_role(allowed_features=None, include_settings=True):
    """Compatibility helper. None shows every registered feature."""
    allowed = None if allowed_features is None else set(allowed_features)
    items = [
        (label, f"feat:{feature}")
        for feature, (label, _description) in FEATURES.items()
        if feature != "dashboard" and (allowed is None or feature in allowed)
    ]
    rows = _rows(items, 2)
    if include_settings:
        rows.append([_btn("⚙️ Settings", "settings")])
    rows.append([_btn("🔄 Refresh", "home")])
    return InlineKeyboardMarkup(rows)


def category_menu(title, visible_features=None):
    features = list(CATEGORIES.get(title, []))
    if visible_features is not None:
        visible = set(visible_features)
        features = [f for f in features if f in visible]

    items = [(FEATURES[f][0], f"feat:{f}") for f in features if f in FEATURES]
    rows = _rows(items, 2)
    rows.append([_btn("⬅️ Semua fitur", "home")])
    return InlineKeyboardMarkup(rows)


def permission_menu():
    items = [
        (f"⚙️ {label}", f"pfeat:{feature}")
        for feature, (label, _description) in FEATURES.items()
        if feature != "dashboard"
    ]
    rows = _rows(items, 2)
    rows.append([_btn("⬅️ Kembali", "home")])
    return InlineKeyboardMarkup(rows)


def feature_permission_menu(feature, admin_allowed, member_allowed):
    label = FEATURES[feature][0]
    return InlineKeyboardMarkup([
        [_btn(f"Admin {'✅' if admin_allowed else '❌'}", f"toggle:{feature}:admin"),
         _btn(f"Member {'✅' if member_allowed else '❌'}", f"toggle:{feature}:member")],
        [_btn("⬅️ Permissions", "perm:menu"),
         _btn("🏠 Menu", "home")],
    ])
