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
See "a> help tb" for a list of styles""",
    "tb_imageget": "Attempts to get an image from its name.\nSee \"a> help tb\" for a list of styles"
}
usagedb = {
    "echo": "<text>",
    "tb": "[style] [f:<flag>] <style options...>",
    "tb_alias": "<style> <search term>",
    "tb_imageget": "<style> <image name>"
}
briefdb = {
    "echo": "make the bot say something",
    "tb": "create a textbox image",
    "tb_alias": "search for images you can use for textboxes",
    "tb_imageget": "get an image from its name"
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


@tb.error
async def tb_error(cxt: commands.Context, error):
    await cxt.send("something went wrong! check that all images exist and you have not skipped any style options")


@bot.group(name="tb-images", aliases=["tb-alias"], brief="stuff for images used in textboxes")
async def tb_images(cxt: commands.Context):
    if cxt.invoked_subcommand is None:
        await cxt.send("subcommand " + str(cxt.subcommand_passed) + " does not exist")


@command_with_help(tb_images, name="search")
async def tb_alias(cxt: commands.Context, style: str, search: str):
    alias_tmp = open("alias-tmp", "w+")
    print(textboxer.find_aliases(style, search), file=alias_tmp)
    alias_tmp.seek(0)
    await cxt.send("alias search results for \"" + search + "\" in style " + style,
                   file=discord.File(alias_tmp, "search-" + search + ".txt"))
    alias_tmp.close()
    os.remove("alias-tmp")


@command_with_help(tb_images, name="get")
async def tb_imageget(cxt: commands.Context, style: str, image: str):
    imagepath = textboxer.get_image(style, image)
    imagefile = imagepath.open("rb")
    await cxt.send(image, file=discord.File(imagefile, filename=image + imagepath.suffix))
    imagefile.close()


@tb_imageget.error
async def imageget_error(cxt: commands.Context, error):
    if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, AttributeError):
        await cxt.send("could not get image!")


@bot.event
async def on_ready():
    global initialized_status
    if not initialized_status:
        initialized_status = True
        await bot.change_presence(status=discord.Status.idle)


@bot.event
async def on_command_error(cxt: commands.Context, error):
    if isinstance(error, commands.UserInputError):
        await cxt.send("i only got the first part of that")
    elif isinstance(error, commands.CommandNotFound):
        await cxt.send("what does any of that even mean???")
    raise error


bot.run(config["token"])
