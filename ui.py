from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton
from features import FEATURES


def _button(label: str) -> KeyboardButton:
    return KeyboardButton(label)


# Semua fitur yang tampil di menu utama.
# Key harus sama dengan FEATURES agar menu selalu mengikuti daftar fitur UBot.
FEATURE_BUTTONS = [
    (feature, label)
    for feature, (label, _description) in FEATURES.items()
    if feature != "dashboard"
]


def main_menu():
    """Menu utama UBot berupa tombol permanen seperti menu bot pada contoh pengguna.

    Owner melihat seluruh fitur. Untuk Admin/Member, penyaringan dilakukan oleh
    caller berdasarkan permission sebelum menu dikirim.
    """
    rows = []
    for i in range(0, len(FEATURE_BUTTONS), 2):
        rows.append([
            _button(FEATURE_BUTTONS[j][1])
            for j in range(i, min(i + 2, len(FEATURE_BUTTONS)))
        ])

    # Pengaturan adalah menu tambahan, bukan fitur yang perlu permission member.
    rows.append([_button("⚙️ Settings")])
    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False,
        selective=False,
    )


def menu_for_role(allowed_features=None, include_settings=True):
    """Buat menu dengan hanya fitur yang diizinkan untuk role tertentu.

    allowed_features=None berarti semua fitur (dipakai Owner).
    """
    allowed = None if allowed_features is None else set(allowed_features)
    items = [
        (feature, label)
        for feature, label in FEATURE_BUTTONS
        if allowed is None or feature in allowed
    ]

    rows = []
    for i in range(0, len(items), 2):
        rows.append([_button(items[j][1]) for j in range(i, min(i + 2, len(items)))])

    if include_settings:
        rows.append([_button("⚙️ Settings")])

    return ReplyKeyboardMarkup(
        rows,
        resize_keyboard=True,
        is_persistent=True,
        one_time_keyboard=False,
        selective=False,
    )


def category_menu(title, visible_features=None):
    # Compatibility helper.
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
    items = [(f, label) for f, (label, _desc) in FEATURES.items() if f != "dashboard"]
    for i in range(0, len(items), 2):
        rows.append([_button(f"⚙️ {items[j][0]}") for j in range(i, min(i + 2, len(items)))])
    rows.append([_button(".menu")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, is_persistent=True)


def feature_permission_menu(feature, admin_allowed, member_allowed):
    return ReplyKeyboardMarkup(
        [
            [
                _button(f"Admin {feature} {'✅' if admin_allowed else '❌'}"),
                _button(f"Member {feature} {'✅' if member_allowed else '❌'}"),
            ],
            [_button("⚙️ Settings")],
        ],
        resize_keyboard=True,
        is_persistent=True,
    )
