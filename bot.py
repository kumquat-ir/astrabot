#!/usr/bin/env python3

import os
import discord
import json
import logging

from pathlib import Path

from discord.ext import commands

from textboxer import textboxer


textboxer.resource_root = Path("tb-resources")
helpdb = {
    "echo": "makes the bot say <text>",
    "tb": textboxer.gen_help(),
    "tb_alias": """Searches the textbox image alias database to find what image names you can use for a given style.
See "a> help tb" for a list of styles"""
}
usagedb = {
    "echo": "<text>",
    "tb": "[style] [f:<flag>] <style options...>",
    "tb_alias": "<style> <search term>"
}
briefdb = {
    "echo": "make the bot say something",
    "tb": "create a textbox image",
    "tb_alias": "what images you can use for textboxes"
}


logging.basicConfig(level=logging.INFO)
intents = discord.Intents.default()
intents.typing = False
# intents.message_content = True
initialized_status = False
config_file = Path("config.json").open()
config = json.load(config_file)
config_file.close()
bot = commands.Bot(command_prefix="a> ", intents=intents)


def command_with_help(_bot, *args, **kwargs):

    def decorator(func):
        fname = func.__name__
        return _bot.command(*args, **kwargs, help=helpdb[fname], usage=usagedb[fname], brief=briefdb[fname])(func)

    return decorator


def group_with_help(_bot, *args, **kwargs):

    def decorator(func):
        fname = func.__name__
        return _bot.group(*args, **kwargs, help=helpdb[fname], usage=usagedb[fname], brief=briefdb[fname])(func)

    return decorator


async def require_admin(cxt: commands.Context) -> bool:
    if cxt.message.author.id not in config["admins"]:
        await cxt.send("You do not have permission to do that.")
        return False
    return True


@command_with_help(bot)
async def echo(cxt: commands.Context, *, arg: str):
    await cxt.send(arg)


@bot.command(hidden=True, name="quit")
async def _quit(cxt: commands.Context):
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


@bot.command(hidden=True)
async def setstatus(cxt: commands.Context, *, text: str):
    if await require_admin(cxt):
        await _setstatus(text)


async def _setstatus(text: str):
    game = discord.Game(text)
    await bot.change_presence(status=discord.Status.idle, activity=game)


@command_with_help(bot, aliases=["textbox"])
async def tb(cxt: commands.Context, *args: str):
    textboxer.parsestr("", out="tb-tmp.png", presplit=list(args))
    tb_img = open("tb-tmp.png", "rb")
    await cxt.send(file=discord.File(tb_img, "generated textbox.png"))
    tb_img.close()
    os.remove("tb-tmp.png")


@command_with_help(bot, name="tb-images", aliases=["tb-alias"])
async def tb_alias(cxt: commands.Context, style: str, search: str):
    alias_tmp = open("alias-tmp", "w+")
    print(textboxer.find_aliases(style, search), file=alias_tmp)
    alias_tmp.seek(0)
    await cxt.send("alias search results for \"" + search + "\" in style " + style,
                   file=discord.File(alias_tmp, "search-" + search + ".txt"))
    alias_tmp.close()
    os.remove("alias-tmp")


@bot.event
async def on_ready():
    global initialized_status
    if not initialized_status:
        initialized_status = True
        await bot.change_presence(status=discord.Status.idle)


bot.run(config["token"])
