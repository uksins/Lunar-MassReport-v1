import time
import os
import asyncio
import toml
import aiohttp
import itertools
import discord
import random
import datetime
import base64
import requests

from typing import Coroutine
from asyncio.tasks import Task
from discord.ext import commands
from pystyle import *


class logging:

    def __init__(self):
        self.theme = "\033[38;5;253m"
        
        self.list = ['\x1b[38;2;255;20;0m', '\x1b[38;2;255;40;0m', '\x1b[38;2;255;60;0m', '\x1b[38;2;255;80;0m', '\x1b[38;2;255;100;0m', '\x1b[38;2;255;120;0m', '\x1b[38;2;255;140;0m', '\x1b[38;2;255;160;0m', '\x1b[38;2;255;180;0m', '\x1b[38;2;255;200;0m', '\x1b[38;2;255;220;0m', '\x1b[38;2;255;240;0m', '\x1b[38;2;220;255;0m', '\x1b[38;2;200;255;0m', '\x1b[38;2;180;255;0m', '\x1b[38;2;160;255;0m', '\x1b[38;2;140;255;0m', '\x1b[38;2;120;255;0m', '\x1b[38;2;100;255;0m', '\x1b[38;2;80;255;0m', '\x1b[38;2;60;255;0m', '\x1b[38;2;40;255;0m', '\x1b[38;2;20;255;0m', '\x1b[38;2;0;255;0m', '\x1b[38;2;0;255;20m', '\x1b[38;2;0;255;40m', '\x1b[38;2;0;255;60m', '\x1b[38;2;0;255;80m', '\x1b[38;2;0;255;100m', '\x1b[38;2;0;255;120m', '\x1b[38;2;0;255;140m', '\x1b[38;2;0;255;160m', '\x1b[38;2;0;255;180m', '\x1b[38;2;0;255;200m', '\x1b[38;2;0;255;220m', '\x1b[38;2;0;255;240m', '\x1b[38;2;0;220;255m', '\x1b[38;2;0;200;255m', '\x1b[38;2;0;180;255m', '\x1b[38;2;0;160;255m', '\x1b[38;2;0;140;255m', '\x1b[38;2;0;120;255m', '\x1b[38;2;0;100;255m', '\x1b[38;2;0;80;255m', '\x1b[38;2;0;60;255m', '\x1b[38;2;0;40;255m', '\x1b[38;2;0;20;255m', '\x1b[38;2;0;0;255m', '\x1b[38;2;20;0;255m', '\x1b[38;2;40;0;255m', '\x1b[38;2;60;0;255m', '\x1b[38;2;80;0;255m', '\x1b[38;2;100;0;255m', '\x1b[38;2;120;0;255m', '\x1b[38;2;140;0;255m', '\x1b[38;2;160;0;255m', '\x1b[38;2;180;0;255m', '\x1b[38;2;200;0;255m', '\x1b[38;2;220;0;255m', '\x1b[38;2;240;0;255m', '\x1b[38;2;255;0;220m', '\x1b[38;2;255;0;200m', '\x1b[38;2;255;0;180m', '\x1b[38;2;255;0;160m', '\x1b[38;2;255;0;140m', '\x1b[38;2;255;0;120m', '\x1b[38;2;255;0;100m', '\x1b[38;2;255;0;80m', '\x1b[38;2;255;0;60m', '\x1b[38;2;255;0;40m', '\x1b[38;2;255;0;20m', '\x1b[38;2;255;0;0m']

        self.list.reverse()
        
        self.mainColors = itertools.cycle(self.list)

    def getTime(self):
        currentTime = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-2]
        return currentTime

    def info(self, text: str, end=None):
        print(
            "{0}[{1}{2}{0}] {0}• {3}".format(
                self.theme, next(self.mainColors), self.getTime(), text
            ),
            end=end
        )

    def error(self, text: str, end=None):
        print(
            "{0}[{1}{2}{0}] {0}• {3}".format(
                self.theme, next(self.mainColors), self.getTime(), text
            ),
            end=end
        )

    def title(self, text: str):
        if os.name == "nt": os.system("title {}".format(text))

class ThreadPool:
    
    def __init__(self, workers) -> None:
        self._semaphore = asyncio.Semaphore(workers)
        self._tasks = set()

    async def submit(self, coro: Coroutine) -> None:
        await self._semaphore.acquire()
        task = asyncio.ensure_future(coro)
        self._tasks.add(task)
        task.add_done_callback(self._on_task_done)

    def _on_task_done(self, task: Task) -> None:
        self._tasks.remove(task)
        self._semaphore.release()

    async def join(self) -> None:
        await asyncio.gather(*self._tasks)

    async def __aenter__(self) -> "ThreadPool":
        return self

    def __aexit__(self, *_) -> None:
        return self.join()

logging = logging()
clear = lambda: os.system("cls; clear")

with open('data/settings.toml') as settings:
    data = toml.load(settings)

    threads = data["System"]["Threads"]
    delay = data["System"]["Delay"]

    token = data["Client"]["Token"]

api = itertools.cycle(["6", "7"])

lock = asyncio.Lock()

client = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None, case_insensitive=True)

headers = {"Authorization": "{}".format(token)}

class Functions(object):
    async def SendReports(channel: str, guild: str, message: str, reason: str):
        try:
            while True:
                async with aiohttp.ClientSession(headers=headers) as client:
                    async with client.post("https://discord.com/api/v9/report", json={'channel_id': channel, 'guild_id': guild, 'message_id': message, 'reason': reason}) as response:
                        if(response.status in range(200, 299)):
                            logging.info("Report Sent To Guild [{}], Channel [{}]".format(guild, channel))
                            break
                        elif (response == 429):
                            json = await response.json()
                            logging.info("Got Ratelimited For {} Seconds".format(json["retry_after"]))
                            return await functions.SendReports(channel, guild, message, reason)
                        else:
                            text = await response.text()
                            logging.info(text)
                            break
        except Exception as error:
            logging.info("CAUGHT EXCEPTION : {}".format(error))
    
    async def test():
        logging.info("Sent A Report")

async def menu():
    clear()
    lime = "\x1b[38;2;52;235;58m"
    reset = "\x1b[0m"
    print(Colorate.Horizontal(Colors.rainbow, logo, 1))
    print()
    logging.info("Loading [Lunar] Functions")
    await asyncio.sleep(1.999)
    clear()
    print(Colorate.Horizontal(Colors.rainbow, logo, 1))
    print()
    logging.info("Threads > {}".format(threads))
    print()
    logging.info("Loaded [Lunar] Function > \"mass-report\"")
    logging.info("Loaded [Lunar] Function > \"log-out\"")
    print()
    logging.info("{}[@Lunar]~Command $ {}".format(reset, lime), end="")
    try:
        command = str(input())
    except:
        return (await menu())
    
    if command.lower() == "mass-report":
        clear()
        print(Colorate.Horizontal(Colors.rainbow, logo, 1))
        print()
        logging.info("{}[@Lunar]~Channel $ {}".format(reset, lime), end="")
        try:
            c = str(input())
        except:
            return await menu()

        logging.info("{}[@Lunar]~Guild $ {}".format(reset, lime), end="")
        try:
            g = str(input())
        except:
            return await menu()
        
        logging.info("{}[@Lunar]~Message-ID $ {}".format(reset, lime), end="")
        try:
            l = str(input())
        except:
            return await menu()
        
        logging.info("Report Content For:")
        print()
        logging.info("1 > \"Illegal Content\"")
        logging.info("2 > \"Harrassment\"")
        logging.info("3 > \"Spam/Phishing Links\"")
        logging.info("4 > \"Self-Harm\"")
        logging.info("5 > \"NSFW Content\"")
        print()
        logging.info("{}[@Lunar]~Reason $ {}".format(reset, lime), end="")
        try:
            r = str(input())
        except:
            return await menu()

        async with ThreadPool(threads) as executor:
            for i in range(999999):
                await executor.submit(Functions.SendReports(c, g, l, r))
                if delay != 0: await asyncio.sleep(delay)
            else:
                pass
        await asyncio.sleep(2500)
        return await menu()

#channel: str, guild: str, message: str, reason: str)
logo = """
 /$$                                              
| $$                                              
| $$       /$$   /$$ /$$$$$$$   /$$$$$$   /$$$$$$ 
| $$      | $$  | $$| $$__  $$ |____  $$ /$$__  $$
| $$      | $$  | $$| $$  \ $$  /$$$$$$$| $$  \__/
| $$      | $$  | $$| $$  | $$ /$$__  $$| $$      
| $$$$$$$$|  $$$$$$/| $$  | $$|  $$$$$$$| $$      
|________/ \______/ |__/  |__/ \_______/|__/  Mass Report - sins                                         
"""

if __name__ == "__main__":
    Anime.Fade(Center.Center(logo), Colors.rainbow, Colorate.Vertical, enter=True)
    clear()
    print(Colorate.Horizontal(Colors.rainbow, logo, 1))
    print()
    asyncio.run(menu())