import sys
import os
import discord
sys.path.append('./lib')
import OWparser
import OWGetter
import OWUpdater
import threading
import asyncio
import sched
import time

#update the database
def update():
    s = sched.scheduler(time.time, time.sleep)
    #update immediately on startup
    updater.update_all()
    while True:
        #then update every 24 hours
        s.enter(60*60*24, 1, updater.update_all)
        s.run()

#define discord client
def client(discordToken): 
    asyncio.set_event_loop(asyncio.new_event_loop())

    client = discord.Client()

    @client.event
    async def on_message(message):
        if message.content.startswith(">help"):
            response = '''>>> __**Overbot commands:**__ 
            \n\n**Battle tags format: name-12345**
            \n\n**Overwatch profiles that you add must be public** 
            \n\n>addplayer **battle tag**: Adds a player without associating your username 
            \n>addme **battle tag**: Adds your account and links your discord account for easy searching. 
            \n>myranks: Returns your ranks if your username is associated with your Battle Tag.
            \n>ranks **Battle tag**: Returns ranks of the given user.
            \n>qptimes **battle tag**: Shows your times played for each hero in quickplay.
            \n>removeplayer **battle tag**: Delete all data associated to the battle tag.
            \n>removeme: Removes your data if you associated a battle tag with your discord using the >addme command.
            \n>comptimes **battle tag**: Shows your times played for each hero in competitive.
            \n>qpstats **battle tag**: Shows your stats for quickplay (Overall stats, not specific heros yet).
            \n>whatsmybattletag: Returns your Battle.net battletag if you have linked your discord to me.
            \n>findbattletag **username**: returns the battle tag of someone in my database. (use username, not nickname!)'''
            await message.channel.send(response)

        if message.content.startswith(">addplayer"):
            try:
                name = message.content[10:]
                add_result = updater.add_user(name)
                if add_result is not None:
                    await message.channel.send(add_result)
                else:
                    await message.channel.send("{} added to database.".format(name))
            except:
                await message.channel.send("Player not found. Please make sure your profile is public.")

        elif message.content.startswith(">addme"):
            try:
                name = message.content[6:]
                add_result = updater.bind_author_to_user(name.strip(), message.author.name)
                if add_result is not None:
                    await message.channel.send(add_result)
                else:
                    await message.channel.send("{} added to database.".format(name))
            except:
                await message.channel.send("Player not found. Check your Btag formatting.")

        elif message.content.startswith(">removeplayer"):
            name = message.content[13:]
            result = updater.remove_user(name.strip())
            await message.channel.send(result)

        elif message.content.startswith(">qptimes"):
            name = message.content[8:]
            await message.channel.send(getter.get_quickplay_times(name.strip()))

        elif message.content.startswith(">comptimes"):
            name = message.content[10:]
            await message.channel.send(getter.get_competitive_times(name.strip()))

        elif message.content.startswith(">qpstats"):
            name = message.content[8:]
            await message.channel.send(getter.get_quickplay_stats(name.strip()))

        elif message.content.startswith(">whatsmybattletag"):
            await message.channel.send(getter.get_battle_tag(message.author.name))

        elif message.content.startswith(">findbattletag"):
            username = message.content[15:]
            await message.channel.send(getter.get_battle_tag(username.strip()))

        elif message.content.startswith(">removeme"):
            await message.channel.send(updater.remove_user(None, message.author.name))

        elif message.content.startswith(">myranks"):
            await message.channel.send(getter.get_ranks(None, message.author.name))

        elif message.content.startswith(">ranks"):
            await message.channel.send(getter.get_ranks(message.content[6:].strip()))




    @client.event
    async def on_ready():
        client.display_name = "OverBot"
        print("logged in as " + str(client.user.name))
        game = discord.Game("the drums in Busan | >help")
        await client.change_presence(activity = game)

    client.run(discordToken)

def main():
    global getter, parser, updater

    with open("token.json") as file:
        data = file.read()

    discordToken = os.environ["discord-token"]
    dbname = os.environ["database-name"]
    dbuser = os.environ["database-user"]
    dbpass = os.environ["database-pass"]

    parser = OWparser.OWParser(dbname, dbuser, dbpass)
    getter = OWGetter.OWGetter(dbname, dbuser, dbpass)
    updater = OWUpdater.OWUpdater(parser, getter)
    #update database and run discord client asynchronously
    threads = []
    bot = threading.Thread(target = client, args = (discordToken,))
    up = threading.Thread(target = update)

    bot.start()
    up.start()

main()