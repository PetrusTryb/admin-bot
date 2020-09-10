import os,re

import discord
from discord.ext import commands
from dotenv import load_dotenv
from manage import Manager

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='/')
serverManager = Manager()
@bot.command(help="Podstawowe informacje o serwerze")
async def info(ctx):
    for out in serverManager.info():
        await ctx.send(out)
@bot.command(help="Tworzy nowe konto użytkownika")
async def register(ctx,nick=""):
    for out in serverManager.register(nick):
        await ctx.send(out)
@bot.command(help="Usuwa konto użytkownika wraz ze wszystkimi danymi")
async def kill(ctx,nick=""):
    for out in serverManager.kill(nick):
        await ctx.send(out)
@bot.command(help="Czyści folder domowy użytkownika")
async def purge(ctx,nick=""):
    for out in serverManager.purge(nick):
        await ctx.send(out)
@bot.command(help="Zmienia hasło użytkownika")
async def password(ctx,nick="",newpass=""):
    for out in serverManager.reset(nick,newpass):
        await ctx.send(out)
@bot.command(help="Pokazuje status limitu pamięci dyskowej użytkownika")
async def quota(ctx,nick=""):
    for out in serverManager.quota(nick):
        await ctx.send(out)
bot.run(TOKEN)