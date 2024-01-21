from decouple import config

class Var:
    # Telegram Credentials

    API_ID = config("API_ID", default=6, cast=int)
    API_HASH = config("API_HASH", default="eb06d4abfb49dc3eeb1aeb98ae0f581e")
    BOT_TOKEN = config("BOT_TOKEN", default=None)

    # Database Credentials

    REDIS_URI = config("REDIS_URI", default=None)
    REDIS_PASS = config("REDIS_PASSWORD", default=None)

    # Channels Ids

    BACKUP_CHANNEL = config("BACKUP_CHANNEL", default=0, cast=int)
    MAIN_CHANNEL = config("MAIN_CHANNEL", cast=int)
    LOG_CHANNEL = config("LOG_CHANNEL", default=0, cast=int)
    CLOUD_CHANNEL = config("CLOUD_CHANNEL", cast=int)
    OWNER = config("OWNER", default=0, cast=int)

    # Other Configs

    THUMB = config(
        "THUMBNAIL", default="https://graph.org/file/37d9d0657d51e01a71f26.jpg"
    )
    FFMPEG = config("FFMPEG", default="ffmpeg")
    SEND_SCHEDULE = config("SEND_SCHEDULE", default=False, cast=bool)
    RESTART_EVERDAY = config("RESTART_EVERDAY", default=True, cast=bool)
