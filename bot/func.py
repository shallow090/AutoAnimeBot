

import asyncio
import json
import multiprocessing
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from functools import partial, wraps
from pathlib import Path

import aiofiles
import aiohttp

OK = {}


def run_async(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(
            ThreadPoolExecutor(max_workers=multiprocessing.cpu_count() * 5),
            partial(function, *args, **kwargs),
        )

    return wrapper


async def async_searcher(
    url: str,
    post: bool = None,
    headers: dict = None,
    params: dict = None,
    json: dict = None,
    data: dict = None,
    ssl=None,
    re_json: bool = False,
    re_content: bool = False,
    real: bool = False,
    *args,
    **kwargs,
):
    async with aiohttp.ClientSession(headers=headers) as client:
        if post:
            data = await client.post(
                url, json=json, data=data, ssl=ssl, *args, **kwargs
            )
        else:
            data = await client.get(url, params=params, ssl=ssl, *args, **kwargs)
        if re_json:
            return await data.json()
        if re_content:
            return await data.read()
        if real:
            return data
        return await data.text()


async def cover_dl(link):
    try:
        image = await async_searcher(link, re_content=True)
        fn = f"thumbs/{link.split('/')[-1]}"
        if not fn.endswith((".jpg" or ".png")):
            fn += ".jpg"
        async with aiofiles.open(fn, "wb") as file:
            await file.write(image)
        return fn
    except BaseException:
        return None


def code(data):
    OK.update({len(OK): data})
    return str(len(OK) - 1)


def decode(key):
    if OK.get(int(key)):
        return OK[int(key)]
    return


def hbs(size):
    if not size:
        return ""
    power = 2**10
    raised_to_pow = 0
    dict_power_n = {0: "B", 1: "K", 2: "M", 3: "G", 4: "T", 5: "P"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


async def stats(e):
    try:
        wah = e.pattern_match.group(1).decode("UTF-8")
        ah = decode(wah)
        out, dl = ah.split(";")
        ot = hbs(int(Path(out).stat().st_size))
        ov = hbs(int(Path(dl).stat().st_size))
        ans = f"Downloaded:\n{ov}\n\nCompressing:\n{ot}"
        await e.answer(ans, cache_time=0, alert=True)
    except Exception as error:
        await e.answer(f"Someting Went Wrong!\n{error}", cache_time=0, alert=True)


def stdr(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if len(str(minutes)) == 1:
        minutes = "0" + str(minutes)
    if len(str(hours)) == 1:
        hours = "0" + str(hours)
    if len(str(seconds)) == 1:
        seconds = "0" + str(seconds)
    dur = (
        ((str(hours) + ":") if hours else "00:")
        + ((str(minutes) + ":") if minutes else "00:")
        + ((str(seconds)) if seconds else "")
    )
    return dur


async def duration_s(file):
    tsec = await genss(file)
    x = round(tsec / 5)
    y = round(tsec / 5 + 30)
    pin = stdr(x)
    if y < tsec:
        pon = stdr(y)
    else:
        pon = stdr(tsec)
    return pin, pon

