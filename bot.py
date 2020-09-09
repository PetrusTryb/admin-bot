import os,re,subprocess

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PASSWORD = os.getenv('ROOT_PASSWORD')
bot = commands.Bot(command_prefix='/')
def sudo(command):
    f=subprocess.popen("sudo -S %s"%(command), 'w')
    f.write(PASSWORD)
    f.wait()
@bot.command()
async def test(ctx):
    await ctx.send("Dostępne komendy:\n\
        /help - lista poleceń\n\
        /info - podstawowe informacje o serwerze\n\
        /password - generuje nowe hasło dla użytkownika i wysyła mu je na priv\n\
        /register <nick> - tworzy nowe konto użytkownika o nazwie\n\
        /kill* <nick> - usuwa konto użytkownika wraz ze wszystkimi danymi\n\
        /clear* <nick> - czyści folder domowy użytkownika\n\
        /quota* - pokazuje ranking zapełnienia dysku przez poszczególnych użytkowników\n\
        /reboot* - restartuje serwer\n\n* - oznacza polecenie niedostępne dla zwykłych śmiertelników")
@bot.command(help="podstawowe informacje o serwerze")
async def info(ctx):
    f = os.popen('neofetch --stdout')
    out = f.read()
    await ctx.send(out)
@bot.command(help="tworzy nowe konto użytkownika")
async def register(ctx,nick):
    if(ctx.message.author.top_role.name!="Bogowie"):
        await ctx.send("Nie dla psa")
        return
    nick=re.sub('[^A-Za-z0-9]+', '', nick)
    sudo(f"useradd -m -d /smietnik/{nick} -g smiertelnicy -s /sbin/nologin {nick}")
    sudo("edquota -p samplequota "+nick)
    await ctx.send("Gotowe! Utworzono użytkownika "+nick)
bot.run(TOKEN)