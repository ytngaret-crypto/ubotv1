from features import COMMAND_FEATURES


async def is_allowed(app, message, feature):
    uid = message.from_user.id if message.from_user else 0
    role = await app.db.get_role(uid)

    # Owner bypasses all feature permissions.
    if role == "owner":
        return True

    if role not in ("admin", "member"):
        return False

    # In groups, permissions are scoped to the group. In private chat,
    # use the private chat id so nothing is accidentally enabled globally.
    scope = message.chat.id if message.chat else uid
    return await app.db.permission(scope, feature, role)


async def command_allowed(app, message, command):
    feature = COMMAND_FEATURES.get(command.lower())
    if not feature:
        return False
    return await is_allowed(app, message, feature)


# Backward-compatible alias used by older handlers.
command_is_allowed = command_allowed
