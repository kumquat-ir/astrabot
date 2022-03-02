#!/usr/bin/env python3

import os
import subprocess

from pathlib import Path


if __name__ == "__main__":
    subprocess.run("./bot.py")
    while Path("bot-restart").exists():
        print("bot is restarting!")
        os.remove("bot-restart")
        subprocess.run("./bot.py")
