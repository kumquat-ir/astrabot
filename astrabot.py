#!/usr/bin/env python3

import os
import subprocess

from pathlib import Path


if __name__ == "__main__":
    print("astrabot is starting!")
    botpath = Path("bot.py").resolve()
    subprocess.run(botpath)
    while Path("bot-restart").exists():
        print("astrabot is restarting!")
        os.remove("bot-restart")
        subprocess.run(botpath)
