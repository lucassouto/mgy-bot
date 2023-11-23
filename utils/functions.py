from decouple import config


def build_footer_infos(guild_id: int) -> tuple:
    icon_url = config("BOT_ICON")
    if guild_id in [470710752789921803, 582709300506656792]:
        text = {
            470710752789921803: config("MACRO"),
            582709300506656792: config("MACRO2"),
        }[guild_id]
        return text, icon_url
    return config("BOT_DESCRIPTION", default="MGY"), icon_url
