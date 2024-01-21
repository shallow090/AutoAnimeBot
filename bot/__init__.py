import asyncio
import logging
import os
import sys
from logging import INFO, FileHandler, StreamHandler, basicConfig, getLogger
from traceback import format_exc

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from redis import Redis
from telethon import Button, TelegramClient, events
from telethon.errors.rpcerrorlist import FloodWaitError

from .config import Var

basicConfig(
    format="%(asctime)s || %(name)s [%(levelname)s] : %(message)s",
    handlers=[
        FileHandler("AutoAnimeBot.log", mode="w", encoding="utf-8"),
        StreamHandler(),
    ],
    level=INFO,
    datefmt="%m/%d/%Y, %H:%M:%S",
)
LOGS = getLogger("AutoAnimeBot")
TelethonLogger = getLogger("Telethon")
TelethonLogger.setLevel(INFO)

MEM = {}


LOGS.info(
    """
                        Auto Anime Bot

    """
)

if os.cpu_count() < 4:
    LOGS.warning(
        "These Bot Atleast Need 4vcpu and 32GB Ram For Proper Functiong...\nExiting..."
    )
    exit()


def ask_(db: Redis):
    import sys

    if "--newdb" in sys.argv:
        db.flushall()
    elif "--samedb" in sys.argv:
        pass
    else:
        todo = str(input("Want To Flush Database [Y/N]: "))
        if todo.lower() == "y":
            db.flushall()
            LOGS.info("Successfully Flushed The Database!!!")


def loader(mem: dict, db: Redis, logger):
    for key in db.keys():
        mem.update({key: eval(db.get(key) or "[]")})
    logger.info(f"Succesfully Sync Database!!!")


if not os.path.exists("thumb.jpg"):
    os.system(f"wget {Var.THUMB} -O thumb.jpg")
if not os.path.isdir("encode/"):
    os.mkdir("encode/")
if not os.path.isdir("thumbs/"):
    os.mkdir("thumbs/")
if not os.path.isdir("Downloads/"):
    os.mkdir("Downloads/")

try:
    LOGS.info("Trying to Connect With Telegram...")
    bot = TelegramClient(None, Var.API_ID, Var.API_HASH).start(bot_token=Var.BOT_TOKEN)
    pyro = Client(
        name="pekka",
        api_id=Var.API_ID,
        api_hash=Var.API_HASH,
        bot_token=Var.BOT_TOKEN,
        in_memory=True,
    )  # for fast ul , mere marze
    LOGS.info("Succesfully Connected To Telegram...")
except Exception as ee:
    LOGS.critical("Something Went Wrong...\nExiting...")
    LOGS.error(str(ee))
    exit()

try:
    LOGS.info("Trying Connect With Redis database")
    redis_info = Var.REDIS_URI.split(":")
    dB = Redis(
        host=redis_info[0],
        port=redis_info[1],
        password=Var.REDIS_PASS,
        charset="utf-8",
        decode_responses=True,
    )
    LOGS.info("Successfully Connected to Redis database")
    ask_(dB)
    loader(MEM, dB, LOGS)
except Exception as eo:
    LOGS.exception(format_exc())
    LOGS.critical(str(eo))
    exit()


async def notify_about_me():
    try:
        if "--no-notify" in sys.argv:
            return await pyro.start()
        btn = [
            [
                Button.url("Developer 👨‍💻", url="telegram.me/dev_shadow"),
                Button.url(
                    "Ask Source Code 📂", url="https://telegram.me/dev_shadow"
                ),
            ]
        ]
        await bot.send_message(
            Var.MAIN_CHANNEL, "`Hi, Anime Lovers, How Are You?`", buttons=btn
        )
    except BaseException:
        pass
    await pyro.start()


class Reporter:
    def __init__(self, client: TelegramClient, chat_id: int, logger: logging):
        self.client = client
        self.chat = chat_id
        self.logger = logger

    async def report(self, msg, error=False, info=False, log=False):
        if error:
            txt = [f"[ERROR] {msg}", "error"]
        elif info:
            txt = [f"[INFO] {msg}", "info"]
        else:
            txt = [f"{msg}", "info"]
        if log:
            if txt[1] == "error":
                self.logger.error(txt[0])
            else:
                self.logger.info(txt[0])
        try:
            await self.client.send_message(self.chat, f"```{txt[0][:4096]}```")
        except FloodWaitError as fwerr:
            await self.client.disconnect()
            self.logger.info("Sleeping Becoz Of Floodwait...")
            await asyncio.sleep(fwerr.seconds + 10)
            await self.client.connect()
        except ConnectionError:
            await self.client.connect()
        except Exception as err:
            self.logger.error(str(err))


# Reports Logs in telegram
reporter = Reporter(bot, Var.LOG_CHANNEL, LOGS)

# Scheduler For Airtime
sch = AsyncIOScheduler(timezone="Asia/Kolkata")

# Cache Data For Operations
POST_TRACKER = []
REQUEST = []
