#!/usr/bin/env python3

import discord
import textboxer
import json

from pathlib import Path

from discord.ext import commands

config = {}


if __name__ == "__main__":
    config_file = Path("config.json").open()
    config = json.load(config_file)
    config_file.close()
    bot = commands.Bot(command_prefix="a>")
    bot.run(config["token"])
