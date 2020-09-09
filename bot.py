import os,re

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PASSWORD = os.getenv('ROOT_PASSWORD')
bot = commands.Bot(command_prefix='/')
def sudo(command):
    f=os.popen("sudo -S %s"%(command), 'w')
    f.write(PASSWORD)
    out=f.read()
    return out
@bot.command()
async def test(ctx):
    await ctx.send("Dostępne komendy:\n\
        /help - lista poleceń\n\
        /info - podstawowe informacje o serwerze\n\
        /password - generuje nowe hasło dla użytkownika i wysyła mu je na priv\n\
        /register - tworzy nowe konto użytkownika i wysyła hasło na priv\n\
        /kill* <nick> - usuwa konto użytkownika wraz ze wszystkimi danymi\n\
        /clear* <nick> - czyści folder domowy użytkownika\n\
        /quota* - pokazuje ranking zapełnienia dysku przez poszczególnych użytkowników\n\
        /reboot* - restartuje serwer\n\n* - oznacza polecenie niedostępne dla zwykłych śmiertelników")
@bot.command(help="podstawowe informacje o serwerze")
async def info(ctx):
    f = os.popen('neofetch --stdout')
    out = f.read()
    await ctx.send(out)
@bot.command(help="tworzy nowe konto użytkownika i wysyła hasło na priv")
async def register(ctx):
    sender = ctx.message.author.id
    print(sender)
    await ctx.send(sudo("useradd -m -d /smietnik/${username} -g smiertelnicy -s /sbin/nologin ${username}"))
    await ctx.send(sudo("edquota -p samplequota user"))
bot.run(TOKEN)
#client.run(TOKEN)