import os,re

import discord
from discord.ext import commands
from dotenv import load_dotenv
from mm import MortalManager
import json

def getConfig():
    with open ("conf.json","r") as f:
        return json.loads(f.read())
def saveConfig():
    with open ("conf.json","w") as f:
        f.write(json.dumps(config))
def isGod(uid):
    return (str(uid) in config["userapi"]["admins"])

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='/')
config=getConfig()
serverManager = MortalManager.from_save(config)


@bot.command(help="Tworzy nowe konto użytkownika")
async def register(ctx):
    if(not isGod(ctx.author.id)):
        await ctx.send("Nie dla psa!")
        return
    for rank in ctx.message.role_mentions:
        for user in rank.members:
            out = serverManager.create_mortal()
            if(out):
                config["mortals"]=list(serverManager.mortals)
                config["discords"][str(user.id)]=out
                saveConfig()
                await user.send("Pomyślnie utworzono konto na serwerze!\nLogin: "+out)
            else:
                await ctx.send("Nie można utworzyć konta dla: "+user)
    for user in ctx.message.mentions:
        out = serverManager.create_mortal()
        if(out):
            config["mortals"]=list(serverManager.mortals)
            config["discords"][str(user.id)]=out
            saveConfig()
            await user.send("Pomyślnie utworzono konto na serwerze!\nLogin: "+out)
        else:
            await ctx.send("Nie można utworzyć konta dla: "+user)
@bot.command(help="Usuwa konto użytkownika wraz ze wszystkimi danymi")
async def kill(ctx):
    if(not isGod(ctx.author.id)):
        await ctx.send("Nie dla psa!")
        return
    for user in ctx.message.mentions:
        try:
            serverManager.remove_mortal(config["discords"][str(user.id)])
            config["mortals"]=list(serverManager.mortals)
            config["discords"].pop(str(user.id),None)
            saveConfig()
            await ctx.send("Usunięto konto: "+config["discords"][str(user.id)])
        except:
            await ctx.send("Nie można usunąć konta")
    for user in ctx.message.content.split()[1:]:
        try:
            serverManager.remove_mortal(user)
            config["mortals"]=list(serverManager.mortals)
            for i in config["discords"]:
                if(config["discords"][i]==user):
                    config["discords"].pop(i)
                    break
            saveConfig()
            await ctx.send("Usunięto konto: "+user)
        except:
            await ctx.send("Nie można usunąć konta")
@bot.command(help="Zmienia hasło użytkownika")
async def password(ctx):
    try:
        user=config["discords"][str(ctx.author.id)]
        newdata=serverManager.password_reset(user)
        await ctx.author.send("Twoje hasło na serwerze zostało zresetowane!")
        await ctx.author.send("Nowe hasło do przesyłania plików:"+newdata[0])
        await ctx.author.send("Nowe hasło do bazy danych:"+newdata[1])
        await ctx.send("Sprawdź wiadomości prywatne.")
    except:
        await ctx.send("Nie udało się zresetować hasła")
bot.run(TOKEN)