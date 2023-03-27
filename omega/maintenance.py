import discord
from discord import *
from discord.ext import tasks
import sqlite3
import random
import sys
import datetime
import uuid
from time import strptime
from datetime import datetime
import asyncio

import os

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

import json
from builtins import input

db = sqlite3.connect("omega.db")
cursor = db.cursor()
       
intents = Intents.default()
intents.members = True
client = Client(intents=intents)
tree = app_commands.CommandTree(client)

redirect = f"{os.getenv('DOMAIN')}/api?code="

def admin_check(id):
    guild = client.get_guild(int(1084295027783639080))
    member = guild.get_member(id)
    if member == None:
        return(0)
    owner = guild.get_role(1088563072467210291)
    master = guild.get_role(1084386167501377538)
    hypervisor = guild.get_role(1088563502278512791)
    supervisor = guild.get_role(1088564838072070175)
    moderator =  guild.get_role(1088563364621459627)

    if (owner in member.roles):
        return(5)
    if (master in member.roles):
        return(4)
    if (hypervisor in member.roles):
        return(3)
    if (supervisor in member.roles):
        return(2)
    if (moderator in member.roles):
        return(1)
    return(0)

@tree.command(name = "help", description = "🚧 Bot curently in maintenance 🚧")
async def soon(interaction: Interaction):
    await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral = True, delete_after=5)

#####################################################################################################################################################

@tree.command(name = "login", description = "🚧 Bot curently in maintenance 🚧")
async def sign_up(interaction: Interaction):
    await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral = True, delete_after=5)
    
#####################################################################################################################################################

@tree.command(name = "logout", description = "🚧 Bot curently in maintenance 🚧")
async def logout(interaction: Interaction):
    await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral = True, delete_after=5)

#####################################################################################################################################################

@tree.command(name = "ping", description = "🚧 Bot curently in maintenance 🚧")
async def ping(interaction: Interaction):
    await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral = True, delete_after=5)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "sync", description = "🚧 Bot curently in maintenance 🚧")
@app_commands.guild_only()
async def sync(interaction: Interaction,type: app_commands.Choice[int], intra_id: int, role: discord.Role, campus_id: int=0):
    await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral = True, delete_after=5)
    

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "sync_project", description = "🚧 Bot curently in maintenance 🚧")
@app_commands.guild_only()
async def sync_project(interaction: Interaction, intra_id: int, in_progress: app_commands.Choice[int], finished: app_commands.Choice[int], validated: app_commands.Choice[int], role: discord.Role, campus_id: int=0):
    await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral = True, delete_after=5)
    
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "nick", description = "🚧 Bot curently in maintenance 🚧")
@app_commands.guild_only()
async def nick(interaction: Interaction,namming_pattern: str, campus_id: int=0):
    await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral = True, delete_after=5)


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "nick_reset", description = "🚧 Bot curently in maintenance 🚧")
@app_commands.guild_only()
async def nick_reset(interaction: Interaction):
    await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral = True, delete_after=5)


#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "delete", description = "🚧 Bot curently in maintenance 🚧")
@app_commands.guild_only()
async def delete(interaction: Interaction,type: app_commands.Choice[int], id_from: app_commands.Choice[int], id: str):
    await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral = True, delete_after=5)


#####################################################################################################################################################

@tree.command(name='reaction_role', description='🚧 Bot curently in maintenance 🚧')
@app_commands.guild_only()
async def launch_button(interaction: discord.Interaction,label:str,style: app_commands.Choice[int],role:discord.Role, message: str=""):
    await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral = True, delete_after=5)

#####################################################################################################################################################

@client.event
async def on_interaction(interaction=Interaction):
    if str(interaction.type) == "InteractionType.component":
        data = interaction.data
        type = data['component_type']
        if type == 2:
            await interaction.response.send_message(f"🚧 Bot curently in maintenance 🚧", ephemeral=True, delete_after=3)

#####################################################################################################################################################

async def help(message):
    level = admin_check(message.author.id)
    title = f"Admin help for Potocole Omega"
    color = random.randint(0, 16777215)
    color = Colour(color) 
    embed = Embed(title = f"{title}",color = color)
    embed.add_field(name = "___________", value = f"utilities", inline = False)
    if level >= 5:
        embed.add_field(name = "__ROOT__", value = f"your are the master", inline = False)
    if level >= 4:
        embed.add_field(name = "status", value = f"envoie les status du bot", inline = False)
        embed.add_field(name = "play", value = f"set un status pour le bot", inline = False)
        embed.add_field(name = "pause", value = f"retire un status du bot", inline = False)
        embed.add_field(name = "leave", value = f"quitte un serveur", inline = False)
    if level >= 3:
        embed.add_field(name = "join", value = f"genere une invitation vers le serveur", inline = False)
        embed.add_field(name = "list", value = f"envoie la liste des serveur du bot", inline = False)
    if level >= 2:
        embed.add_field(name = "send", value = f"envoie un mp avec le bot", inline = False)
    if level >= 1:
        embed.add_field(name = "stats", value = f"donne des chifres sur l'utilisation du bot", inline = False)
    await message.channel.send(embed=embed)

async def stats(message):
    wait = await message.channel.send("waiting...")
    student_count = len(cursor.execute(f"SELECT intra_id FROM 'users'").fetchall())
    nick_count = len(cursor.execute(f"SELECT campus_id FROM 'nick'").fetchall())
    cursus_count = len(cursor.execute(f"SELECT campus_id FROM 'cursus'").fetchall())
    coalition_count = len(cursor.execute(f"SELECT campus_id FROM 'coa'").fetchall())
    project_count = len(cursor.execute(f"SELECT campus_id FROM 'project'").fetchall())
    groups_count = len(cursor.execute(f"SELECT campus_id FROM 'groups'").fetchall())
    years_count = len(cursor.execute(f"SELECT campus_id FROM 'years'").fetchall())
    global_count = cursus_count + coalition_count + project_count + groups_count + years_count + nick_count
    server_count = 0
    async for current in client.fetch_guilds():
        server_count += 1
    title = f"Stats tools for Potocole Omega"
    color = random.randint(0, 16777215)
    color = Colour(color) 
    embed = Embed(title = f"{title}",color = color)
    embed.add_field(name = "__Student__", value = f"{student_count}", inline = True)
    embed.add_field(name = "__Server__", value = f"{server_count}", inline = True)
    embed.add_field(name = "__Total synced items__", value = f"{global_count}", inline = False)
    embed.add_field(name = "__Nick__", value = f"{nick_count}", inline = True)
    embed.add_field(name = "__Cursus__", value = f"{cursus_count}", inline = True)
    embed.add_field(name = "__COA__", value = f"{coalition_count}", inline = True)
    embed.add_field(name = "__Project__", value = f"{project_count}", inline = True)
    embed.add_field(name = "__Groups__", value = f"{groups_count}", inline = True)
    embed.add_field(name = "__Years__", value = f"{years_count}", inline = True)
    await message.channel.send(embed=embed)
    await wait.delete()

async def send(command, message):
    command = command.split(" ")
    id = command[0]
    del command[0]
    content = " ".join(command)
    member = await client.fetch_user(id)
    embed = Embed(title = f"Mesage from the Omega Master : {message.author}", description=f"{content}")
    if (str(message.author.avatar) != "None"):
        embed.set_thumbnail(url=message.author.avatar.url)
    try :
        await member.send(embed=embed)
    except:
        await message.channel.send(f"Fail to mp {member}")
        return
    await message.channel.send(f"Succesfully send to {member}")
    channel = client.get_channel(1088582242290368572)
    title = f"Mp from {message.author} to {member}"
    color = random.randint(0, 16777215)
    color = Colour(color) 
    embed = Embed(title = f"{title}",color = color, description=f"{content}")
    embed.set_footer(text = f"recever id : {message.author.id}")
    if (str(message.author.avatar) != "None"):
        embed.set_thumbnail(url=message.author.avatar.url)
    await channel.send(embed=embed)

async def status(command, message):
    i = 0
    msg = ""
    for status in status_list:
        send = False
        i += 1
        msg = f"{msg}\n{status}"
        if (i>=15):
            send = True
            i = 0
            await message.channel.send(msg)
            msg = ""
    if (send == False):
        await message.channel.send(msg)

async def new_status(command, message):
    status_list.append(command)
    await message.channel.send(f"Add : {command}")
    channel = client.get_channel(1088582242290368572)
    title = f"{message.author} set a new status"
    color = random.randint(0, 16777215)
    color = Colour(color) 
    embed = Embed(title = f"{title}",color = color, description=f"{command}")
    if (str(message.author.avatar) != "None"):
        embed.set_thumbnail(url=message.author.avatar.url)
    await channel.send(embed=embed)

async def rm_status(command, message):
    status_list.remove(command)
    await message.channel.send(f"Remove : {command}")
    channel = client.get_channel(1088582242290368572)
    title = f"{message.author} remove a status"
    color = random.randint(0, 16777215)
    color = Colour(color) 
    embed = Embed(title = f"{title}",color = color, description=f"{command}")
    if (str(message.author.avatar) != "None"):
        embed.set_thumbnail(url=message.author.avatar.url)
    await channel.send(embed=embed)

async def list(message):
    i = 0
    msg = ""
    async for current in client.fetch_guilds():
        send = False
        i += 1
        current = await client.fetch_guild(int(current.id))
        owner = await client.fetch_user(int(current.owner_id))
        msg = f"{msg}\n{current.name} | {current.id} | {owner} | {current.approximate_member_count} membres"
        if (i>=15):
            send = True
            i = 0
            await message.channel.send(msg)
            msg = ""
    if (send == False):
        await message.channel.send(msg)

async def admin_join(command, message):
    guild = await client.fetch_guild(int(command))
    channel = await guild.fetch_channels()
    for current in channel:
        try:
            invite = await current.create_invite(max_uses = 1, reason = "Omega master request", max_age=3600)
            await message.channel.send(invite)
            channel = client.get_channel(1088582242290368572)
            title = f"{message.author} join {guild.name}"
            color = random.randint(0, 16777215)
            color = Colour(color) 
            embed = Embed(title = f"{title}",color = color)
            if (str(message.author.avatar) != "None"):
                embed.set_thumbnail(url=message.author.avatar.url)
            await channel.send(embed=embed)
            return
        except:
            useless = 1
    await message.channel.send("Someting went wrong")

async def srv_leave(command, message):
    guild = await client.fetch_guild(int(command))
    try:
        await guild.leave()
        await message.channel.send(f"Successfully leave {guild.name}")
        channel = client.get_channel(1088582242290368572)
        title = f"{message.author} leave {guild.name}"
        color = random.randint(0, 16777215)
        color = Colour(color) 
        embed = Embed(title = f"{title}",color = color)
        if (str(message.author.avatar) != "None"):
            embed.set_thumbnail(url=message.author.avatar.url)
        await channel.send(embed=embed)
    except:
        await message.channel.send("Someting went wrong")

@client.event
async def on_message(message):
    if (message.author == client.user):
        return
    if (str(message.channel.type) == "private"):
        level = admin_check(message.author.id)
        if (level >= 1):
            mp = message.content
            if mp[:5] == "stats" and level >= 1:
                await stats(message)
            elif mp[:4] == "send" and level >= 2:
                await send(mp[5:], message)
            elif mp[:4] == "list" and level >= 3:
                await list(message)
            elif mp[:4] == "join" and level >= 3:
                await admin_join(mp[5:], message)
            elif mp[:5] == "leave" and level >= 4:
                await srv_leave(mp[6:], message)
            elif mp[:6] == "status" and level >= 4:
                await status(mp[7:], message)
            elif mp[:4] == "play" and level >= 4:
                await new_status(mp[5:], message)
            elif mp[:5] == "pause" and level >= 4:
                await rm_status(mp[6:], message)
            elif mp[:4] == "help" and level >= 1:
                await help(message)
        else:
            channel = await client.fetch_channel(1088582109343514664)
            embed = Embed(title = f"Ticket from : {message.author}", description=f"{message.content}")
            embed.set_footer(text = f"id : {message.author.id}")
            if (str(message.author.avatar) != "None"):
                embed.set_thumbnail(url=message.author.avatar.url)
            await channel.send(embed=embed)
            await message.channel.send(f"Succesfully send to the administrator")

#####################################################################################################################################################

@client.event
async def on_member_join(member):
    user = cursor.execute(f"SELECT omega_id FROM 'users' WHERE discord_id='{member.id}'").fetchone()
    if (not user):
        try :
            await member.send(f"Hello and welcome to the {member.guild.name} server!\n\nThis server is powered by the Omega Protocol bot and therefore has automatic permissions based on your account on the 42 intranet.\n\n**Please authenticate via the command /login\n\nFor any problem with this step, I invite you to PM the bot with your request\n\nThe Omega master, Ngennaro")
        except :
            print(f"____________________\nfail to send a message to {member}")

#####################################################################################################################################################

@tasks.loop(seconds=20)
async def presence():
    for status in status_list:
        game = Game(name=status)
        await client.change_presence(status=Status.do_not_disturb, activity=game)
        await asyncio.sleep(20)

status_list = ["🚧 Maintenance 🚧"]

@client.event
async def on_ready():
    await tree.sync()
    presence.start()

client.run("MTA0MjgwMjE0ODM4OTQ0MTYzNw.GOiKQC.njVntL6pbOaXtSHoDzNP1qko3nwOGRQk4AX-ek") #(os.getenv('BOT_TOKEN'))
