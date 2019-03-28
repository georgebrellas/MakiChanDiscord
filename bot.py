# MakiChan bot by George Brellas

# General dependencies
import logging
import random
import math
import re
import urllib.request as urllib2
import sqlite3

# Discord.py specific dependencies
import youtube_dl
import discord

# Setting up logging. Courtesy of the discord.py library docs.
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

conn = sqlite3.connect('servers.db')
cursor = conn.cursor()

# Our discord client, aka the bot!
client = discord.Client()

# Our 'video' player global.
global vp
# PyCharm stuffs
# noinspection PyRedeclaration
vp = None


# TODO: Fix redundant commands
# Main youtube_dl player.
class Player:
    def __init__(self, url):
        self.vclient = None
        self.vplayer = None
        self.url = url

    async def start(self, vclient):
        self.vclient = vclient
        lvp = await vclient.create_ytdl_player(self.url)
        self.vplayer = lvp
        lvp.start()

    async def is_playing(self):
        return self.vplayer.is_playing()

    async def stop(self):
        self.vplayer.stop()

    async def play(self):
        self.vplayer.resume()

    async def pause(self):
        self.vplayer.pause()

    async def set_vol(self, vol):
        vol = vol / 100
        self.vplayer.volume = vol

    async def disconnect(self):
        self.vclient.disconnect()

    async def set_url(self, url):
        self.url = url

    async def resume(self):
        self.vplayer.resume()

    async def is_done(self):
        return self.vplayer.is_done()


@client.event
# Initialization
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('--------')
    gameplaying = discord.Game(name="m! help")
    await client.change_presence(game=gameplaying)
    print("Initiating database...")
    db_initiate()


# Helper Functions
def check_int(message):
    try:
        int(message)
        return True
    except ValueError:
        return False


async def delete_message(message):
    await client.delete_message(message)


def safety2(message):
    if db_check_safety(message.server):
        if db_check_safety(message.server) >= 2:
            return True
        else:
            return False
    else:
        return False


def safety3(message):
    if db_check_safety(message.server):
        if db_check_safety(message.server) >= 3:
            return True
        else:
            return False
    else:
        return False


# Checks if a specific URL is supported by the youtube_dl player. Courtesy of stackoverflow!
def supported(url):
    ies = youtube_dl.extractor.gen_extractors()
    for ie in ies:
        if ie.suitable(url) and ie.IE_NAME != 'generic':
            # Site has dedicated extractor
            return True
    return False


# DB manipulation
# I hate this kill me.
def db_initiate():
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='servers'")
        servers_exists = cursor.fetchone()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        users_exists = cursor.fetchone()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assocs'")
        assocs_exists = cursor.fetchone()

        if not servers_exists:
            print("Servers table does not exist.")
            db_create_servers_table()
        else:
            print("Loaded servers table.")

        if not users_exists:
            print("Users table does not exist.")
            db_create_users_table()
        else:
            print("Loaded users table.")

        if not assocs_exists:
            print("Assocs table does not exist.")
            db_create_assocs_table()
        else:
            print("Loaded assocs table.")

    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_sanity_check(message):
    try:
        user = str(message.author)
        server = str(message.server)
        owner = str(message.server.owner)

        if not db_check_user(user):
            db_create_user(user, 100)

        if not db_check_server(server):
            db_create_server(server, 2)

        if not db_check_assoc(server, user):
            if user == owner:
                db_assoc_user(server, user, 2)
            else:
                db_assoc_user(server, user, 0)

    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_create_servers_table():
    try:
        cmd = """CREATE TABLE IF NOT EXISTS servers (
                id INTEGER NOT NULL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                safety INTEGER NOT NULL
                )"""
        print("Creating servers table...")
        cursor.execute(cmd)
        conn.commit()
        print("Committed changes.")
        print("Finalized servers db creation.")
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_create_users_table():
    try:
        cmd = """CREATE TABLE IF NOT EXISTS users (
                 id INTEGER NOT NULL PRIMARY KEY,
                 username VARCHAR(255) NOT NULL,
                 coins integer
              )"""
        print("Creating users table...")
        cursor.execute(cmd)
        conn.commit()
        print("Committed changes.")
        print("Finalized users db creation.")
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_create_assocs_table():
    try:
        cmd = """CREATE TABLE IF NOT EXISTS assocs (
                 id INTEGER NOT NULL PRIMARY KEY,
                 server VARCHAR(255) NOT NULL,
                 user VARCHAR(255) NOT NULL,
                 is_admin INTEGER NOT NULL
              )"""
        print("Creating assocs table...")
        cursor.execute(cmd)
        conn.commit()
        print("Committed changes.")
        print("Finalized assocs db creation.")
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_create_user(username, coins):
    try:
        cmd = f"""INSERT INTO users (username, coins)
                  VALUES ('{username}', '{coins}')"""
        print(f"Inserting user '{username}' to the table...")
        cursor.execute(cmd)
        conn.commit()
        print("Committed changes.")
        print("Finalized user creation.")
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_check_coins(username):
    try:
        cursor.execute(f"SELECT coins FROM users WHERE username='{username}'")
        coins = cursor.fetchone()
        if coins:
            return coins[0]
        else:
            return 0
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_set_coins(username, amount):
    try:
        cmd = f"UPDATE users SET coins = '{amount}' WHERE username = '{username}'"
        print(f"Changing coins of {username} to {amount}")
        cursor.execute(cmd)
        conn.commit()
        print("Committed changes.")
        print("Finalized server coin edit.")
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_check_user(username):
    try:
        cursor.execute(f"SELECT id FROM users WHERE username='{username}'")
        user = cursor.fetchone()
        if user:
            return True
        else:
            return False
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_create_server(server, safety):
    try:
        cmd = f"""INSERT INTO servers (name, safety)
                  VALUES ('{server}', '{safety}');"""
        print(f"Inserting server '{server}' to the table...")
        cursor.execute(cmd)
        conn.commit()
        print("Committed changes.")
        print("Finalized server creation.")
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_check_safety(server):
    try:
        cursor.execute(f"SELECT safety FROM servers WHERE name='{server}'")
        safety = cursor.fetchone()
        if safety:
            return safety[0]
        else:
            return False
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_set_safety(server, safety):
    try:
        cmd = f"UPDATE servers SET safety = '{safety}' WHERE name = '{server}'"
        print(f"Changing safety of {server} to {safety}")
        cursor.execute(cmd)
        conn.commit()
        print("Committed changes.")
        print("Finalized server safety edit.")
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_check_server(server):
    try:
        cursor.execute(f"SELECT id FROM servers WHERE name='{server}'")
        serverid = cursor.fetchone()
        if serverid:
            return True
        else:
            return False
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_assoc_user(server, user, is_admin):
    try:
        cmd = f"""INSERT INTO assocs(server, user, is_admin)
                VALUES ('{server}','{user}','{is_admin}')"""
        print(f"Associating user {user} with the server {server}...")
        cursor.execute(cmd)
        conn.commit()
        print("Committed changes.")
        print("Finalized user-server association.")
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_check_assoc(server, user):
    try:
        cursor.execute(f"SELECT id FROM assocs WHERE server='{server}' AND user='{user}'")
        assoc = cursor.fetchone()
        if assoc:
            return True
        else:
            return False
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_check_admin(server, user):
    try:
        cursor.execute(f"SELECT is_admin FROM assocs WHERE server = '{server}' AND user = '{user}'")
        admin = cursor.fetchone()
        if admin:
            if admin[0] >= 1:
                return True
            else:
                return False
        else:
            return False
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_check_owner(server, user):
    try:
        cursor.execute(f"SELECT is_admin FROM assocs WHERE server = '{server}' AND user = '{user}'")
        admin = cursor.fetchone()
        if admin:
            if admin[0] >= 2:
                return True
            else:
                return False
        else:
            return False
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_check_op(server, user):
    try:
        cursor.execute(f"SELECT is_admin FROM assocs WHERE server = '{server}' AND user = '{user}'")
        admin = cursor.fetchone()
        if admin:
            if admin[0] >= 3:
                return True
            else:
                return False
        else:
            return False
    except sqlite3.Error as e:
        print("SQL Error:", e)


def db_set_admin(server, user, rank):
    try:
        cmd = f"UPDATE assocs SET is_admin = '{rank}' WHERE server = '{server}' AND user = '{user}'"
        print(f"Changing admin level of {user} to {rank}")
        cursor.execute(cmd)
        conn.commit()
        print("Committed changes.")
        print("Finalized admin rank edit.")
    except sqlite3.Error as e:
        print("SQL Error:", e)


# Usable commands
# Admin
# noinspection PyUnresolvedReferences
async def set_safety(message, msg):
    user = message.author
    server = message.server
    msg = re.sub('safety', "", msg, count=1)
    if check_int(msg):
        msg = int(msg)
        if msg == "":
            await client.send_message(message.channel, "Please enter a number from 1 to 3!")
        else:
            if 4 > msg > 0:
                if db_check_admin(server, user):
                    db_set_safety(server, msg)
                    await client.send_message(message.channel, f"Set the server's safety level to {str(msg)}.")
                else:
                    # noinspection PyUnresolvedReferences
                    await client.send_message(message.channel, "You are not authorized to use this command!")
            else:
                await client.send_message(message.channel, "Please enter a number from 1 to 3!")
    else:
        await client.send_message(message.channel, "Please enter a number from 1 to 3!")


# noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
async def set_admin(message, msg):
    user = message.author
    msg = re.sub('admin', "", msg, count=1)
    server = message.server
    member = server.get_member(msg)
    if len(message.mentions) > 1:
        return client.send_message(message.channel, "You must tag only one person!")
    else:
        if member is None:
            if not message.mentions:
                adminusr = message.author
            else:
                adminusr = server.get_member(message.mentions[0].id)
        else:
            adminusr = member
    if db_check_owner(server, user):
        if db_check_admin(server, adminusr):
            db_set_admin(server, adminusr, 0)
            await client.send_message(message.channel, f"Admin authorization striped from {str(msg)}.")
        else:
            db_set_admin(server, adminusr, 1)
            await client.send_message(message.channel, f"Admin authorization given to {str(msg)}.")
    else:
        await client.send_message(message.channel, "You are not authorized to use this command!")


# Currency
# noinspection PyUnresolvedReferences
async def give_coins(message, msg):
    msg = re.sub("give ", '', msg, count=1)
    user = message.author
    user_coins = db_check_coins(user)
    if message.mentions:
        if len(message.mentions) > 1:
            await client.send_message(message.channel, "Please only tag one person!")
        else:
            mention = message.server.get_member(message.mentions[0].id)
            name = message.mentions[0].name
            mr = str(message.mentions[0].mention)
            if mention == message.author:
                await client.send_message(message.channel, "You can't send yourself coins...")
            else:
                coin_check = re.sub(mr, '', msg, count=1)
                if not check_int(coin_check):
                    await client.send_message(message.channel, "Please enter a number only!")
                else:
                    coin_amount = abs(int(coin_check))
                    if coin_amount == 0:
                        await client.send_message(message.channel, "You can't send air you dummy!")
                    else:
                        if user_coins > 0:
                            if user_coins < coin_amount:
                                await client.send_message(message.channel, "You do not have that many coins!")
                            else:
                                recipient_coins = db_check_coins(mention)
                                db_set_coins(mention, recipient_coins + coin_amount)
                                db_set_coins(user, user_coins - coin_amount)
                                await client.send_message(message.channel, f"Sent {coin_amount} to {name}")
                        else:
                            await client.send_message(message.channel, "You have no coins to give!")
    else:
        await client.send_message(message.channel, "Please tag someone!")


# noinspection PyUnresolvedReferences
async def view_coins(message):
    if message.mentions:
        mention = message.server.get_member(message.mentions[0].id)
        mentionname = message.mentions[0].name
        coins = str(db_check_coins(mention))
        await client.send_message(message.channel, f"{mentionname} has {coins} coins.")
    else:
        coins = str(db_check_coins(message.author))
        await client.send_message(message.channel, f"You have {coins} coins.")


# noinspection PyUnresolvedReferences
async def coin_toss(message):
    user = message.author
    rand = random.randrange(0, 2)
    if db_check_coins(user):
        coins = int(db_check_coins(user))
        if coins > 0:
            await client.send_message(message.channel, "Pick, heads or tails? You've got 10 seconds!")
            wmsg = await client.wait_for_message(timeout=10, author=message.author)
            if wmsg:
                if wmsg.content.lower().startswith("heads"):
                    if rand == 1:
                        await client.send_message(message.channel, "It was heads! You win 2 coins!")
                        coins = int(db_check_coins(user)) + 2
                        db_set_coins(user, coins)
                    else:
                        await client.send_message(message.channel, "It was tails! You lose 1 coin!")
                        coins = int(db_check_coins(user)) - 1
                        db_set_coins(user, coins)
                elif wmsg.content.lower().startswith("tails"):
                    if rand == 1:
                        await client.send_message(message.channel, "It was heads! You lose 1 coin!")
                        coins = int(db_check_coins(user)) - 1
                        db_set_coins(user, coins)
                    else:
                        await client.send_message(message.channel, "It was tails! You win 2 coins!")
                        coins = int(db_check_coins(user)) + 2
                        db_set_coins(user, coins)
                else:
                    await client.send_message(message.channel, "You have to answer either heads or tails! Jee!")
            else:
                await client.send_message(message.channel, "Be faster! Baaaka!")
        else:
            await client.send_message(message.channel, "You have no coins to flip!")
    else:
        await client.send_message(message.channel, "You have no coins to flip!")


# noinspection PyUnresolvedReferences
async def set_coins(message, msg):
    msg = re.sub('setcoins', "", msg, count=1)
    server = message.server
    user = message.author
    gg = db_check_op(server, user)
    if gg:
        if msg.startswith("of"):
            msg = re.sub('', "", msg, count=1)
            lucky = server.get_member(message.mentions[0])
            msg = re.sub(str(lucky), "", msg, count=1)
            coins = int(db_check_coins(lucky)) + int(msg)
            db_set_coins(lucky, coins)
        elif msg.startswith("mine"):
            unlucky = server.get_member(message.mentions[0].id)
            coins = 0
            db_set_coins(unlucky, coins)
        elif msg.startswith("none"):
            db_set_coins(user, 0)
        else:
            coins = int(db_check_coins(message.author)) + int(msg)
            db_set_coins(message.author, coins)
    else:
        await client.send_message(message.channel, 'You have to choose a valid command dummy! '
                                                   '(Type m! list for a list of all available commands!)')


# Player
# noinspection PyUnresolvedReferences
async def player_start(message, msg):
    global vp
    # Not sure why I have to remove the play twice. But it works so ¯\_(ツ)_/¯
    amsg = re.sub('play ', "", msg, count=1)
    amsg = re.sub('play', "", amsg, count=1)
    if not amsg:
        if vp is None:
            return client.send_message(message.channel, "Please enter a URL!")
        elif await vp.is_playing() or vp.vplayer.is_done():
            return client.send_message(message.channel, "There's already something playing! "
                                                        "(Enter an URL to change it!)")
        else:
            await vp.resume()
            return client.send_message(message.channel, "Resuming playback of '" + vp.vplayer.title + "'")
    else:
        if supported(amsg):
            if message.author.voice_channel:
                if vp is not None:
                    if vp.vplayer is None:
                        vp.vplayer.disconnect()
                        uvc = message.author.voice_channel
                        vc = await client.join_voice_channel(uvc)
                        vp = Player(amsg)
                        await vp.start(vc)
                        return client.send_message(message.channel, "Started playing '" + vp.vplayer.title + "'")

                    elif await vp.is_playing() or vp.vplayer.is_done():
                        await vp.stop()
                        vp.vclient.disconnect()
                        uvc = message.author.voice_channel
                        vc = await client.join_voice_channel(uvc)
                        vp = Player(amsg)
                        await vp.start(vc)
                        return client.send_message(message.channel, "Started playing '" + vp.vplayer.title + "'")
                else:
                    uvc = message.author.voice_channel
                    vc = await client.join_voice_channel(uvc)
                    vp = Player(amsg)
                    await vp.start(vc)
                    print(vp, vp.vplayer)
                    return client.send_message(message.channel, "Started playing '" + vp.vplayer.title + "'")
            else:
                return client.send_message(message.channel, "Please join a channel!")
        else:
            return client.send_message(message.channel, "Please enter a valid URL!")


# noinspection PyUnresolvedReferences
async def player_stop(message):
    global vp
    if vp is None:
        await client.send_message(message.channel, "There's nothing playing to stop.")
    elif vp.vplayer is None:
        await client.send_message(message.channel, "Stopped playback.")
        await vp.vclient.disconnect()
        vp = None

    elif await vp.is_playing():
        await vp.stop()
        await client.send_message(message.channel, "Stopped playback.")
        await vp.vclient.disconnect()
        vp = None

    else:
        await client.send_message(message.channel, "Stopped playback.")
        await vp.vclient.disconnect()
        vp = None


# noinspection PyUnresolvedReferences
async def player_pause(message):
    if await vp.is_playing():
        await vp.pause()
        await client.send_message(message.channel, "Paused playback.")
    else:
        await client.send_message(message.channel, "There isn't anything to pause!")


# noinspection PyUnresolvedReferences
async def player_resume(message):
    if vp is None:
        await client.send_message(message.channel, "There's nothing playing to resume it's playback!")
    if await vp.is_playing() or vp.vplayer.is_done():
        await client.send_message(message.channel, "There's already something playing!")
    else:
        await vp.resume()
        await client.send_message(message.channel, "Resuming playback of '" + vp.vplayer.title + "'")


# noinspection PyUnresolvedReferences
async def player_vol(message, msg):
    amsg = re.sub('vol ', "", msg, count=1)
    if vp is None:
        await client.send_message(message.channel, "There's nothing playing to set it's volume.")
    else:
        if math.isnan(int(amsg)):
            await client.send_message(message.channel, "Please enter a number!")
        else:
            amsg = int(amsg)
            if amsg > 200 or amsg < 0:
                await client.send_message(message.channel, "Please enter a valid volume number! (0-200)")
            else:
                if amsg <= 100:
                    await vp.set_vol(amsg)
                    await client.send_message(message.channel, "Set volume to " + str(amsg) + "%.")
                else:
                    await client.send_message(message.channel,
                                              "WARNING! Setting the volume above 100%"
                                              " will cause audio distortion!")
                    await vp.set_vol(amsg)
                    await client.send_message(message.channel, "Set volume to " + str(amsg) + "%.")


# noinspection PyUnresolvedReferences
async def player_nowplaying(message):
    if vp is None:
        await client.send_message(message.channel, "There's nothing playing!")
    elif not await vp.is_playing():
        await client.send_message(message.channel, "There's nothing playing!")
    else:
        await client.send_message(message.channel, "Currently playing: '" + vp.vplayer.title + "'.")


# Misc
def greethello(message):
    return client.send_message(message.channel, 'Hi ' + str(message.author.mention) + ' <3 !')


def greetbye(message):
    return client.send_message(message.channel, 'Bye ' + str(message.author.mention) + ' <3 !')


def avatar(message):
    msg = message.content
    amsg = re.sub('avatar', "", msg, count=1)
    server = message.server
    member = server.get_member_named(amsg)
    if len(message.mentions) > 1:
        return client.send_message(message.channel, "You must tag only one person!")
    else:
        if member is None:
            if not message.mentions:
                return client.send_message(message.channel, "https://cdn.discordapp.com/avatars/" + message.author.id
                                           + "/" + message.author.avatar + ".jpg")
            else:
                member = server.get_member(message.mentions[0].id)
                return client.send_message(message.channel, "https://cdn.discordapp.com/avatars/" + member.id + "/"
                                                            + member.avatar + ".jpg")
        else:
            return client.send_message(message.channel, "https://cdn.discordapp.com/avatars/" + member.id + "/"
                                                        + member.avatar + ".jpg")


def say(message, msg):
    amsg = re.sub('say', "", msg, count=1)
    if amsg == "":
        return client.send_message(message.channel, "Please enter something for me to say!")
    else:
        return client.send_message(message.channel, amsg)


def love(message, msg):
    amsg = re.sub('love ', "", msg, count=1)
    amount = random.randrange(1, 101)
    server = message.server
    member = server.get_member_named(amsg)
    if len(message.mentions) > 1:
        return client.send_message(message.channel, "You must tag only one person!")
    else:
        if member is None:
            if not message.mentions:
                luvusr = message.author.name
            else:
                luvusr = server.get_member(message.mentions[0].id).name
        else:
            luvusr = member.name
        if 0 >= amount <= 19:
            return client.send_message(message.channel, "" + str(amount)
                                       + "% love... :broken_heart:  \n Pff, you're a pest " + luvusr
                                       + "!\n Stop wasting oxygen!")
        elif 20 >= amount <= 39:
            return client.send_message(message.channel, "" + str(amount) + "% love... :broken_heart:  "
                                                        "\n Ahaha, you believe I would like YOU "
                                                        + luvusr + "? \n get over yourself.")
        elif 40 >= amount <= 59:

            return client.send_message(message.channel, "" + str(amount) + "% love. :neutral_face:  "
                                                        "\n I suppose you're tolerable " + luvusr + ".")
        elif 60 >= amount <= 79:
            return client.send_message(message.channel, "" + str(amount) + "% love! :heart: \n You are a great friend "
                                                        + luvusr + "!")
        elif 80 >= amount <= 99:
            return client.send_message(message.channel, "" + str(amount)
                                       + "% love! :heart::heart:  \n You're one of my best friends " + luvusr + "!")
        elif amount == 100:
            return client.send_message(message.channel, "TRUE LOVE! (100%) :heart_eyes: \n"
                                                        " I-It's not like I like you or anything! Baka " + luvusr
                                                        + " ! \n O-Okay maybe just a bit.")


def hot(message, msg):
    amsg = re.sub('hot ', "", msg, count=1)
    amount = random.randrange(1, 101)
    server = message.server
    member = server.get_member_named(amsg)
    if len(message.mentions) > 1:
        return client.send_message(message.channel, "You must tag only one person!")
    else:
        if member is None:
            if not message.mentions:
                hotusr = message.author.name
            else:
                hotusr = server.get_member(message.mentions[0].id).name
        else:
            hotusr = member.name
        if 0 >= amount <= 19:
            return client.send_message(message.channel, hotusr + " is " + str(amount)
                                       + "% hot! :nauseated_face: :nauseated_face: ")
        elif 20 >= amount <= 39:
            return client.send_message(message.channel, hotusr + " is " + str(amount) + "% hot! :nauseated_face: ")
        elif 40 >= amount <= 59:
            return client.send_message(message.channel, hotusr + " is " + str(amount) + "% hot! :unamused: :unamused: ")
        elif 60 >= amount <= 79:
            return client.send_message(message.channel, hotusr + " is " + str(amount) + "% hot! :fire: ")
        elif 80 >= amount <= 99:
            return client.send_message(message.channel, hotusr + " is " + str(amount) + "% hot! :fire: :fire: ")
        elif amount == 100:
            return client.send_message(message.channel, ":fire: :fire: THE HOTTEST (100%) :boom: :fire: :fire: ")


def creds(message):
    return client.send_message(message.channel, "Creator: KawaiiMeowz \n"
                                                "Made in Python using the discord.py API wrapper made by Rapptz")


def dev(message):
    return client.send_message(message.channel, "Something broke? Join the MakiChanDev server and ask for help from the"
                                                "creator himself!\nhttps://discord.gg/2wteP7T")


def func_help(message):
    desc = "**Party Stuff** \n\n:bust_in_silhouette: **avatar:** *Links yours or someone else's avatar!*\n" \
        ":wave: **hi | bye:** *Greets you* \n" \
        ":speech_left: **say | sayd:** *Repeats after you(latter one also deletes your message)*\n" \
        ":anger: **roast:** *Roasts you (or someone else)*\n" \
        ":heart: **love:** *Tells you how much I love you!*\n" \
        ":fire: **hot:** *How hot are you?*\n" \
        ":smirk: **perv:** *Ofc you know what this is, you perv!* \n" \
        "\n\n**Coins**\n\n" \
        ":moneybag: **coins:** Shows you your coins or someone else's\n"\
        ":money_with_wings: **flip:** Flip a coin!\n" \
        ":gift: **give:** Give someone coins\n"\
        "\n\n**Player Controls**\n\n" \
        ":arrow_forward: **play:** Starts/resumes playback.\n" \
        ":pause_button: **pause:** *Pauses playback.*\n" \
        ":play_pause: **resume:** *Resumes playback. (I know, redundant)*\n" \
        ":information_source: **nowplaying:** *Shows info on what's playing right now!*\n" \
        ":speaker: **vol:** *Sets the volume (0%-200%)*" \
        "\n\n**Utilities**\n\n" \
        ":cowboy: **admin:** *Give/take bot admin authorization to someone*\n"\
        ":baby: **safety:** *Sets the server's safety tier (1-3)*\n"\
        ":page_with_curl: **list | help:** *Lists all available commands(aka this.. duh.)*\n" \
        ":information_source: **creds:** *Developer and library credits.*"
    em = discord.Embed(colour=0xe91e63, description=desc)
    return client.send_message(message.channel, "Here's what I can do!", embed=em)


def sayd(message, msg):
    amsg = re.sub('sayd', "", msg, count=1)
    try:
        return client.send_message(message.channel, amsg)
    except discord.errors.HTTPException:
        return client.send_message(message.channel, "Stop trying to break me, BAKA!")


def rand_insult(message, msg):
    amsg = re.sub('roast', "", msg, count=1)
    server = message.server
    member = server.get_member_named(amsg)
    if len(message.mentions) > 1:
        return client.send_message(message.channel, "You must tag only one person!")
    else:
        if member is None:
            if not message.mentions:
                insult = str(urllib2.urlopen("https://insult.mattbas.org/api/en/insult.txt").read())
                insult = insult.strip(insult[0])
                insult = insult.strip("'")
                return client.send_message(message.channel, insult + "!")
            else:
                member = server.get_member(message.mentions[0].id).name
                insult = str(
                    urllib2.urlopen('https://insult.mattbas.org/api/en/insult.txt?who=' + member).read())
                insult = insult.strip(insult[0])
                insult = insult.strip("'")
                return client.send_message(message.channel, insult + "!")
        else:
            insult = str(urllib2.urlopen('https://insult.mattbas.org/api/en/insult.txt?who=' + member).read())
            insult = insult.strip(insult[0])
            insult = insult.strip("'")
            return client.send_message(message.channel, insult + "!")


def perv(message, msg):
    amsg = re.sub('perv ', "", msg, count=1)
    amount = random.randrange(1, 101)
    server = message.server
    member = server.get_member_named(amsg)
    if len(message.mentions) > 1:
        return client.send_message(message.channel, "You must tag only one person!")
    else:
        if member is None:
            if not message.mentions:
                pervusr = message.author.name
            else:
                pervusr = server.get_member(message.mentions[0].id).name
        else:
            pervusr = member.name
        if 0 >= amount <= 19:
            return client.send_message(message.channel, pervusr + " is " + str(amount)
                                       + "% perverted! :no_mouth: :no_mouth: ")
        elif 20 >= amount <= 39:
            return client.send_message(message.channel, pervusr + " is " + str(amount) + "% perverted! :no_mouth: ")
        elif 40 >= amount <= 59:
            return client.send_message(message.channel, pervusr + " is " + str(amount)
                                       + "% perverted! :thumbsdown: :thumbsdown: ")
        elif 60 >= amount <= 79:
            return client.send_message(message.channel, pervusr + " is " + str(amount)
                                       + "% perverted! :weary: :punch: :sweat_drops: ")
        elif 80 >= amount <= 99:
            return client.send_message(message.channel, pervusr + " is " + str(amount)
                                       + "% perverted! :weary: :punch: :sweat_drops: :weary: :punch: :sweat_drops: ")
        elif amount == 100:
            return client.send_message(message.channel, ":smirk: :weary: :punch: :sweat_drops: MEGA PERVERT (100%) "
                                                        ":weary: :punch: :sweat_drops: :smirk: ")


# noinspection PyUnresolvedReferences
@client.event
# Function responsible for the bot's ability to actually recognize commands.
async def on_message(message):
    global vp
    if message.content.lower().startswith('m! '):
        msg = message.content
        msg = re.sub('m! ', "", msg, count=1)

        if msg.lower().startswith('hello') or msg.lower().startswith('hi'):
            db_sanity_check(message)
            await greethello(message)

        elif msg.lower().startswith('bye') or msg.lower().startswith('bai'):
            db_sanity_check(message)
            await greetbye(message)

        elif msg.startswith('avatar') or msg.startswith('AVATAR'):
            db_sanity_check(message)
            await avatar(message)

        elif msg.startswith('sayd') or msg.startswith('SAYD'):
            db_sanity_check(message)
            if safety2(message):
                amsg = re.sub('sayd', "", msg, count=1)
                if not amsg:
                    await client.send_message(message.channel, "Please enter something for me to say!")
                elif amsg == "":
                    await client.send_message(message.channel, "Please enter something for me to say!")
                else:
                    await sayd(message, msg)
                    await delete_message(message)
            else:
                await client.send_message(message.channel, "This command is blocked in your server!")

        elif msg.startswith('say') or msg.startswith('SAY'):
            db_sanity_check(message)
            await say(message, msg)

        elif msg.startswith('roast') or msg.startswith('ROAST'):
            db_sanity_check(message)
            if safety2(message):
                await rand_insult(message, msg)
            else:
                await client.send_message(message.channel, "This command is blocked in your server!")

        elif msg.startswith('love') or msg.startswith('LOVE'):
            db_sanity_check(message)
            await love(message, msg)

        elif msg.startswith('hot') or msg.startswith('HOT'):
            db_sanity_check(message)
            await hot(message, msg)

        elif msg.startswith('perv') or msg.startswith('PERV'):
            db_sanity_check(message)
            if safety2(message):
                await perv(message, msg)
            else:
                await client.send_message(message.channel, "This command is blocked in your server!")
        # Coins
        elif msg.lower().startswith('coins'):
            db_sanity_check(message)
            await view_coins(message)

        elif msg.lower().startswith('flip'):
            db_sanity_check(message)
            await coin_toss(message)

        elif msg.lower().startswith('give'):
            db_sanity_check(message)
            await give_coins(message, msg)
        # YT player commands
        elif msg.startswith('play') or msg.startswith('PLAY'):
            await player_start(message, msg)

        elif msg.startswith('stop') or msg.startswith('STOP'):
            await player_stop(message)

        elif msg.startswith('pause') or msg.startswith('PAUSE'):
            await player_pause(message)

        elif msg.startswith('resume') or msg.startswith('RESUME'):
            await player_pause(message)

        elif msg.startswith('vol') or msg.startswith('VOL'):
            await player_vol(message, msg)

        elif msg.startswith('nowplaying') or msg.startswith('NOWPLAYING'):
            await player_nowplaying(message)

        # Utilities
        elif msg.lower().startswith('dev'):
            db_sanity_check(message)
            await dev(message)

        elif msg.lower().startswith('list') or msg.lower().startswith('help'):
            db_sanity_check(message)
            await func_help(message)

        elif msg.lower().startswith('creds'):
            await creds(message)
        # Administration
        elif msg.lower().startswith('safety'):
            db_sanity_check(message)
            await set_safety(message, msg)

        elif msg.startswith('admin') or msg.startswith('ADMIN'):
            db_sanity_check(message)
            await set_admin(message, msg)

        elif msg.startswith('setcoins'):
            db_sanity_check(message)
            await set_coins(message, msg)

        else:
            await client.send_message(message.channel, 'You have to choose a valid command dummy! '
                                      '(Type m! list for a list of all available commands!)')

# Authorization token. Obviously opened from a file, don't want that public!
client.run(open('auth').read())
