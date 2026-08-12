from features import COMMAND_FEATURES

async def is_allowed(app, message, feature):
    if not message.from_user:
        return False

    uid = message.from_user.id
    role = await app.db.get_role(uid)

    if role == "owner":
        return True

    if role not in ("admin", "member"):
        return False

    scope = message.chat.id if message.chat else uid
    return await app.db.permission(scope, feature, role)


async def command_allowed(app, message, command):
    feature = COMMAND_FEATURES.get(command.lower().lstrip("."))
    if not feature:
        return False
    return await is_allowed(app, message, feature)


async def command_is_allowed(app, message, command):
    return await command_allowed(app, message, command)
