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
def recovery(discord_id):
    user=config["discords"][str(discord_id)]
    return serverManager.password_reset(user)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='/')
config=getConfig()
serverManager = MortalManager.from_save(config)
@commands.cooldown(1,10)
@bot.command(help="Tworzy nowe konto użytkownika")
async def register(ctx):
    if(not isGod(ctx.author.id)):
        await ctx.send("Nie dla psa!")
        return
    for rank in ctx.message.role_mentions:
        for user in rank.members:
            if(str(user.id) in config["discords"]):
                await ctx.send("Ten użytkownik ma już konto: "+config["discords"][str(user.id)])
                return
            out = serverManager.create_mortal()
            if(out):
                config["mortals"]=list(serverManager.mortals)
                config["discords"][str(user.id)]=out
                saveConfig()
                await ctx.send("Utworzono użytkownika: "+out)
                newdata=recovery(user.id)
                await user.send("Utworzono dla Ciebie konto na serwerze szkolnym!\nWięcej informacji: http://153.19.168.9/\nLogin: `"+out+"`\nHasło do przesyłania plików: `"+newdata[0]+"`\n"+"Hasło do bazy danych: `"+newdata[1]+"`")
            else:
                await ctx.send("Nie można utworzyć konta dla: "+user)
    for user in ctx.message.mentions:
        if(str(user.id) in config["discords"]):
                await ctx.send("Ten użytkownik ma już konto: "+config["discords"][str(user.id)])
                return
        out = serverManager.create_mortal()
        if(out):
            config["mortals"]=list(serverManager.mortals)
            config["discords"][str(user.id)]=out
            saveConfig()
            await ctx.send("Utworzono użytkownika: "+out)
            newdata=recovery(user.id)
            await user.send("Utworzono dla Ciebie konto na serwerze szkolnym!\nWięcej informacji: http://153.19.168.9/\nLogin: `"+out+"`\nHasło do przesyłania plików: `"+newdata[0]+"`\n"+"Hasło do bazy danych: `"+newdata[1]+"`")
        else:
            await ctx.send("Nie można utworzyć konta dla: "+user)
@commands.cooldown(1,10)
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
            if(user[0]!="@"):
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
@commands.cooldown(1,10)
@bot.command(help="Zmienia hasło użytkownika")
async def password(ctx):
    try:
        newdata=recovery(ctx.author.id)
        await ctx.send("Pomyślnie ustawiono nowe hasła.")
        await ctx.author.send("Nowe hasło do przesyłania plików: `"+newdata[0]+"`\n"+"Nowe hasło do bazy danych: `"+newdata[1]+"`")
    except:
        await ctx.send("Nie udało się zresetować hasła")
@commands.cooldown(1,10)
@bot.command(help="Sprawdza, które konta są powiązane z danymi użytkownikami")
async def whois(ctx):
    if(not isGod(ctx.author.id)):
        await ctx.send("Nie dla psa!")
        return
    for user in ctx.message.mentions:
        try:
            nick=config["discords"][str(user.id)]
            await ctx.send(nick)
        except:
            await ctx.send("Ten użytkownik nie posiada konta na serwerze.")
    for user in ctx.message.content.split()[1:]:
        if(user[0]!="@"):
            found=False
            for i in config["discords"]:
                if(config["discords"][i]==user):
                    res=await bot.fetch_user(i)
                    await ctx.send(res.nick)
                    found=True
                    break
            if(not found):
                await ctx.send("Ten użytkownik nie istnieje.")

bot.run(TOKEN)