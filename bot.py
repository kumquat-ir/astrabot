#!/usr/bin/env python3
import os

import discord
import json

from pathlib import Path

from discord.ext import commands

from textboxer import textboxer


textboxer.resource_root = Path("tb-resources")
helpdb = {
    "echo": "makes the bot say <text>",
    "tb": textboxer.gen_help()
}
usagedb = {
    "echo": "<text>",
    "tb": "[style] [f:<flag>] <style options...>"
}
briefdb = {
    "echo": "make the bot say something",
    "tb": "create a textbox image"
}


intents = discord.Intents.default()
intents.typing = False
# intents.message_content = True
config_file = Path("config.json").open()
config = json.load(config_file)
config_file.close()
bot = commands.Bot(command_prefix="a> ", intents=intents)


def command_with_help(func):
    fname = func.__name__
    return bot.command(help=helpdb[fname], usage=usagedb[fname], brief=briefdb[fname])(func)


async def require_admin(cxt: commands.Context) -> bool:
    if cxt.message.author.id not in config["admins"]:
        await cxt.send("You do not have permission to do that.")
        return False
    return True


@command_with_help
async def echo(cxt: commands.Context, arg: str):
    await cxt.send(arg)


@bot.command(hidden=True)
async def quit(cxt: commands.Context):
    if await require_admin(cxt):
        await cxt.send("adios.")
        await bot.close()


@bot.command(hidden=True)
async def restart(cxt: commands.Context):
    if await require_admin(cxt):
        await cxt.send("restarting!")
        rsfile = open("bot-restart", "w")
        rsfile.write("if this file exists, the bot will be restarted")
        rsfile.close()
        await bot.close()


@command_with_help
async def tb(cxt: commands.Context, *args: str):
    textboxer.parsestr("", out="tb-tmp.png", presplit=list(args))
    tb_img = open("tb-tmp.png", "rb")
    await cxt.send(file=discord.File(tb_img, "generated textbox.png"))
    tb_img.close()
    os.remove("tb-tmp.png")


bot.run(config["token"])
