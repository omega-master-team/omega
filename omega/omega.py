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

def login_cooldown(interaction: Interaction):
    level = admin_check(interaction.user.id)
    if (level >= 1):
        return
    return app_commands.Cooldown(3, 3600)

def logout_cooldown(interaction: Interaction):
    level = admin_check(interaction.user.id)
    if (level >= 1):
        return
    return app_commands.Cooldown(1, 3600)

#####################################################################################################################################################

@tree.command(name = "help", description = "Send the bot command list")
async def help(interaction: Interaction):
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='base'").fetchone()[0]
    if maintenance == "on":
        await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
        return
    title = f"Help for Potocole Omega"
    color = random.randint(0, 16777215)
    color = Colour(color) 
    embed = Embed(title = f"{title}", url = "https://profile.intra.42.fr" , color = color)
    embed.add_field(name = "___________", value = f"USERS", inline = False)
    embed.add_field(name = "login", value = f"conectez vous au bot", inline = False)
    embed.add_field(name = "logout", value = f"dé conectez vous du bot", inline = False)
    embed.add_field(name = "___________", value = f"utilities", inline = False)
    embed.add_field(name = "ping", value = f"renvoie le ping du bot", inline = False)
    embed.add_field(name = "issue", value = f"for any issue mp the bot", inline = False)
    embed.add_field(name = "___________", value = f"admin command", inline = False)
    embed.add_field(name = "sync", value = f"set the config parameters on the sever", inline = False)
    embed.add_field(name = "sync_project", value = f"set the project sync parameters on the sever", inline = False)
    embed.add_field(name = "nick", value = f"set the nick parameters on the sever", inline = False)
    embed.add_field(name = "delete", value = f"delete the config parameters on the sever", inline = False)
    embed.add_field(name = "nick_reset", value = f"reset the nick parameters on the sever", inline = False)
    embed.set_footer(text = "The Omega Master : Ngennaro, Oghma, Aartiges")
    await interaction.response.send_message(embed=embed, ephemeral = True)

#####################################################################################################################################################

@tree.command(name = "login", description = "login you with your intra")
@app_commands.checks.dynamic_cooldown(login_cooldown)
async def sign_up(interaction: Interaction):
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='login'").fetchone()[0]
    if maintenance == "on":
        await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
        return
    uid = uuid.uuid4()
    cursor.execute(f"DELETE FROM temp_auth WHERE discord_id={interaction.user.id}")
    cursor.execute(f"INSERT INTO temp_auth (discord_id, code) VALUES ({interaction.user.id},'{uid}')")
    db.commit()
    await interaction.response.send_message(f"Merci de suivre la procedure ci dessous\n{redirect}{uid}", ephemeral = True, delete_after=30)

@sign_up.error
async def on_test_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message("You are on cooldown, please retry later", ephemeral=True, delete_after=2)
#####################################################################################################################################################

@tree.command(name = "logout", description = "remove all your acces and your omega connection")
@app_commands.checks.dynamic_cooldown(logout_cooldown)
async def logout(interaction: Interaction):
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='login'").fetchone()[0]
    if maintenance == "on":
        await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
        return
    cursor.execute(f"DELETE FROM users WHERE discord_id={interaction.user.id}")
    db.commit()
    await interaction.response.send_message(f"You are now logout", ephemeral = True, delete_after=2)
    await disconect(interaction.user.id)

@logout.error
async def on_test_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message("You are on cooldown, please retry later", ephemeral=True, delete_after=3)

#####################################################################################################################################################

@tree.command(name = "ping", description = "send the bot ping")
async def ping(interaction: Interaction):
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='base'").fetchone()[0]
    if maintenance == "on":
        await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
        return
    await interaction.response.send_message(f"{round((client.latency*1000),1)}ms", ephemeral = True, delete_after=5)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "sync", description = "set the config parameters on the sever")
@app_commands.guild_only()
@app_commands.choices(type=[
    app_commands.Choice(name = 'cursus', value = 1),
    app_commands.Choice(name = 'groups', value = 2),
    app_commands.Choice(name = 'coa', value = 3),
    app_commands.Choice(name = 'years', value = 4),
])
@app_commands.describe(intra_id='the id of this item on intranet', role='the role to give', campus_id='the campus needed')
async def sync(interaction: Interaction,type: app_commands.Choice[int], intra_id: int, role: discord.Role, campus_id: int=0):
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='sync_config'").fetchone()[0]
    if maintenance == "on":
        await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
        return
    level = admin_check(interaction.user.id)
    role_id = role.id
    if (not interaction.user.guild_permissions.administrator and level <= 2):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
        return
    cursor.execute(f"INSERT INTO {type.name} (campus_id,intra_id, guild_id, discord_id) VALUES ({campus_id},{intra_id},{interaction.guild_id},{int(role_id)})")
    db.commit()
    await interaction.response.send_message(f"configuration successfully update", ephemeral = True, delete_after=2)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "sync_project", description = "set the project sync parameters on the sever")
@app_commands.guild_only()
@app_commands.choices(in_progress=[
    app_commands.Choice(name = 'Allow', value = 1),
    app_commands.Choice(name = 'Deny', value = 0),
])
@app_commands.choices(finished=[
    app_commands.Choice(name = 'Allow', value = 1),
    app_commands.Choice(name = 'Deny', value = 0),
])
@app_commands.choices(validated=[
    app_commands.Choice(name = 'Allow', value = 1),
    app_commands.Choice(name = 'Deny', value = 0),
])
@app_commands.describe(intra_id='the id of this item on intranet', role='the role to give', campus_id='the campus needed')
async def sync_project(interaction: Interaction, intra_id: int, in_progress: app_commands.Choice[int], finished: app_commands.Choice[int], validated: app_commands.Choice[int], role: discord.Role, campus_id: int=0):
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='sync_config'").fetchone()[0]
    if maintenance == "on":
        await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
        return
    level = admin_check(interaction.user.id)
    role_id = role.id
    if (not interaction.user.guild_permissions.administrator and level <= 2):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
        return
    
    cursor.execute(f"INSERT INTO project (campus_id,intra_id,in_progress,finished,validated,guild_id,discord_id) VALUES ({campus_id},{intra_id},{in_progress.value},{finished.value},{validated.value},{interaction.guild_id},{int(role_id)})")
    db.commit()
    await interaction.response.send_message(f"configuration successfully update", ephemeral = True, delete_after=2)
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "nick", description = "set the nick parameters on the sever (&login and &campus works)")
@app_commands.guild_only()
@app_commands.describe(namming_pattern='the patern to aply (&login and &campus are a dynamic value)', campus_id='the campus needed')
async def nick(interaction: Interaction,namming_pattern: str, campus_id: int=0):
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='sync_config'").fetchone()[0]
    if maintenance == "on":
        await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
        return
    level = admin_check(interaction.user.id)
    if (not interaction.user.guild_permissions.administrator and level <= 2):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
        return
    cursor.execute(f"INSERT INTO nick (campus_id,format,guild_id) VALUES ({campus_id},'{namming_pattern}',{interaction.guild.id})")
    db.commit()
    if (len(namming_pattern) > 20):
        await interaction.response.send_message(f"configuration successfully update\nWarning, the max len for a nickname is 32 so you can have problem", ephemeral = True, delete_after=3)
    else:
        await interaction.response.send_message(f"configuration successfully update", ephemeral = True, delete_after=2)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "nick_reset", description = "reset the nick parameters on the sever")
@app_commands.guild_only()
async def nick_reset(interaction: Interaction):
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='sync_config'").fetchone()[0]
    if maintenance == "on":
        await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
        return
    level = admin_check(interaction.user.id)
    if (not interaction.user.guild_permissions.administrator and level <= 2):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
        return
    cursor.execute(f"DELETE FROM nick WHERE guild_id={interaction.guild.id}")
    db.commit()
    await interaction.response.send_message(f"configuration successfully update", ephemeral = True, delete_after=2)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "delete", description = "delete the config parameters on the sever")
@app_commands.guild_only()
@app_commands.choices(type=[
    app_commands.Choice(name = 'cursus', value = 1),
    app_commands.Choice(name = 'groups', value = 2),
    app_commands.Choice(name = 'project', value = 3),
    app_commands.Choice(name = 'coa', value = 4),
    app_commands.Choice(name = 'years', value = 5),
])
@app_commands.choices(id_from=[
    app_commands.Choice(name = 'intra_id', value = 1),
    app_commands.Choice(name = 'role_id', value = 2),
])
@app_commands.describe(id_from='the type of id', id='the corresponding id')
async def delete(interaction: Interaction,type: app_commands.Choice[int], id_from: app_commands.Choice[int], id: str):
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='sync_config'").fetchone()[0]
    if maintenance == "on":
        await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
        return
    level = admin_check(interaction.user.id)
    if (not interaction.user.guild_permissions.administrator and level <= 2):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True)
        return
    if (id_from.name == "role_id"):
        cursor.execute(f"DELETE FROM {type.name} WHERE discord_id={int(id)} and guild_id={interaction.guild.id}")
    elif (id_from.name == "intra_id"):
        cursor.execute(f"DELETE FROM {type.name} WHERE intra_id={int(id)} and guild_id={interaction.guild.id}")
    db.commit()
    await interaction.response.send_message(f"configuration successfully update", ephemeral = True)

#####################################################################################################################################################

@client.event
async def on_interaction(interaction=Interaction):
    if str(interaction.type) == "InteractionType.component":
        data = interaction.data
        type = data['component_type']
        custom_id = data['custom_id']
        if type == 2:
            maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='reaction_role'").fetchone()[0]
            if maintenance == "on":
                await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
                return
            guild = client.get_guild(interaction.guild_id)
            role = guild.get_role(int(custom_id))
            try:
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
                    await interaction.response.send_message(f"Remove {role.name}", ephemeral=True, delete_after=1)
                else:
                    await interaction.user.add_roles(role)
                    await interaction.response.send_message(f"Add {role.name}", ephemeral=True, delete_after=1)
            except:
                await interaction.response.send_message(f"someting went wrong", ephemeral=True, delete_after=3)

@tree.command(name='reaction_role', description='create a reaction role button')
@app_commands.guild_only()
@app_commands.choices(style=[
    app_commands.Choice(name = 'blue', value = 1),
    app_commands.Choice(name = 'green', value = 2),
    app_commands.Choice(name = 'red', value =3),
    app_commands.Choice(name = 'grey', value =4),
])
@app_commands.describe(label='the button content', style='the button color', role='the role to give', message='An header message')
async def launch_button(interaction: discord.Interaction,label:str,style: app_commands.Choice[int],role:discord.Role, message: str=""):
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='reaction_role'").fetchone()[0]
    if maintenance == "on":
        await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
        return
    level = admin_check(interaction.user.id)
    if (not interaction.user.guild_permissions.administrator and level <= 2):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
        return
    if (interaction.guild_id == 1084295027783639080 and not interaction.user.id == 626861778030034945):
        await interaction.response.send_message(f"Good try 🤡")
        return
    if style.value==1:
        style = ButtonStyle.blurple
    elif style.value==2:
        style = ButtonStyle.green
    elif style.value==3:
        style = ButtonStyle.red
    elif style.value==4:
        style = ButtonStyle.grey
    view = discord.ui.View(timeout=None)
    button = discord.ui.Button(label=label, custom_id=str(role.id), style=style)
    view.add_item(button)
    await interaction.response.send_message("Success", ephemeral=True, delete_after=1)
    await interaction.channel.send(content=message, view = view)

#####################################################################################################################################################

async def help(message):
    level = admin_check(message.author.id)
    title = f"Admin help for Potocole Omega"
    color = random.randint(0, 16777215)
    color = Colour(color) 
    embed = Embed(title = f"{title}",color = color)
    utils = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='admin_utils'").fetchone()[0]
    sync = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='admin_sync'").fetchone()[0]
    mstatus = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='status'").fetchone()[0]
    if level >= 5:
        embed.add_field(name = "__lock__", value = f"manage maintenance mod", inline = False)
    if level >= 4:
        if sync != "on":
            embed.add_field(name = "sync", value = f"syncronise un utilisateur avec omega", inline = False)
            embed.add_field(name = "logout", value = f"déconecte un utilisateur", inline = False)
        if mstatus != "on":
            embed.add_field(name = "status", value = f"envoie les status du bot", inline = False)
            embed.add_field(name = "play", value = f"set un status pour le bot", inline = False)
            embed.add_field(name = "pause", value = f"retire un status du bot", inline = False)
        if utils != "on":
            embed.add_field(name = "leave", value = f"quitte un serveur", inline = False)
    if level >= 3:
        if utils != "on":
            embed.add_field(name = "join", value = f"genere une invitation vers le serveur", inline = False)
            embed.add_field(name = "list", value = f"envoie la liste des serveur du bot", inline = False)
    if level >= 2:
        if utils != "on":
            embed.add_field(name = "send", value = f"envoie un mp avec le bot", inline = False)
    if level >= 1:
        if utils != "on":
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

async def sync_admin(command, message):
    command = command.split(" ")
    discord_id = command[0]
    intra_id = command[1]
    pdt = await message.channel.send("Waiting...")
    await update(intra_id,int(discord_id))
    cursor.execute(f"INSERT INTO new_users (discord_id,intra_id) VALUES ({discord_id},'{intra_id}')")
    db.commit()
    await message.channel.send("Success")
    await pdt.delete()
    channel = client.get_channel(1088582242290368572)
    member = client.get_user(int(discord_id))
    title = f"{message.author} force sync"
    color = random.randint(0, 16777215)
    color = Colour(color) 
    embed = Embed(title = f"{title}",color = color, description=f"discord : {member} ({member.id}) \n login : {intra_id}")
    if (str(message.author.avatar) != "None"):
        embed.set_thumbnail(url=message.author.avatar.url)
    await channel.send(embed=embed)

async def logout_admin(command, message):
    pdt = await message.channel.send("Waiting...")
    if command[:5] == "login" or command[:5] == "intra":
        command = command[6:]
        dobble_login = cursor.execute(f"SELECT discord_id FROM 'users' WHERE intra_id='{command}'").fetchall()
        cursor.execute(f"DELETE FROM users WHERE intra_id='{command}'")
        db.commit()
        for dobble in dobble_login:
            await disconect(dobble[0])
        channel = client.get_channel(1088582242290368572)
        title = f"{message.author} logout"
        color = random.randint(0, 16777215)
        color = Colour(color) 
        embed = Embed(title = f"{title}",color = color, description=f"login : {command}")
        if (str(message.author.avatar) != "None"):
            embed.set_thumbnail(url=message.author.avatar.url)
        await channel.send(embed=embed)
    else:
        print(command)
        cursor.execute(f"DELETE FROM users WHERE discord_id={command}")
        db.commit()
        await disconect(command)
        channel = client.get_channel(1088582242290368572)
        member = client.get_user(int(command))
        title = f"{message.author} logout"
        color = random.randint(0, 16777215)
        color = Colour(color) 
        embed = Embed(title = f"{title}",color = color, description=f"discord : {member} ({member.id})")
        if (str(message.author.avatar) != "None"):
            embed.set_thumbnail(url=message.author.avatar.url)
        await channel.send(embed=embed)
    await message.channel.send("Success")
    await pdt.delete()

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

async def adm_maintenance(command, message):
    command = command.split(" ")
    sub = command[0]
    module_list = cursor.execute(f"SELECT part,status FROM 'maintenance'").fetchall()
    if sub == "list":
        title = f"Admin help for Potocole Omega"
        color = random.randint(0, 16777215)
        color = Colour(color) 
        embed = Embed(title = f"{title}",color = color)
        for module in module_list:
            embed.add_field(name = f"__{module[0]}__", value = module[1], inline = True)
        await message.channel.send(embed=embed)
        return
    if sub == "all":
        for module in module_list:
            try :
                mode = command[1]
                if mode != "on" and mode != "off":
                    await message.channel.send("mode invalid...")
                    return
            except:
                await message.channel.send("mode missing...")
                return
            cursor.execute(f"UPDATE 'maintenance' SET status='{command[1]}' WHERE part='{module[0]}'")
            db.commit()
        await message.channel.send("Success...")
        return
    for module in module_list:
        if sub == module[0]:
            try :
                mode = command[1]
                if mode != "on" and mode != "off":
                    await message.channel.send("mode invalid...")
                    return
            except:
                await message.channel.send("mode missing...")
                return
            cursor.execute(f"UPDATE 'maintenance' SET status='{command[1]}' WHERE part='{module[0]}'")
            db.commit()
            await message.channel.send("Success...")
            return
    await message.channel.send("invalid module")


@client.event
async def on_message(message):
    if (message.author == client.user):
        return
    if (str(message.channel.type) == "private"):
        level = admin_check(message.author.id)
        if (level >= 1):
            utils = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='admin_utils'").fetchone()[0]
            sync = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='admin_sync'").fetchone()[0]
            mstatus = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='status'").fetchone()[0]
            mp = message.content
            if mp[:5] == "stats" and level >= 1:
                if utils == "on":
                    await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                    return
                await stats(message)
            elif mp[:4] == "send" and level >= 2:
                if utils == "on":
                    await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                    return
                await send(mp[5:], message)
            elif mp[:4] == "list" and level >= 3:
                if utils == "on":
                    await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                    return
                await list(message)
            elif mp[:4] == "join" and level >= 3:
                if utils == "on":
                    await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                    return
                await admin_join(mp[5:], message)
            elif mp[:5] == "leave" and level >= 4:
                if utils == "on":
                    await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                    return
                await srv_leave(mp[6:], message)
            elif mp[:6] == "status" and level >= 4:
                if mstatus == "on":
                    await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                    return
                await status(mp[7:], message)
            elif mp[:4] == "play" and level >= 4:
                if mstatus == "on":
                    await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                    return
                await new_status(mp[5:], message)
            elif mp[:5] == "pause" and level >= 4:
                if mstatus == "on":
                    await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                    return
                await rm_status(mp[6:], message)
            elif mp[:4] == "sync" and level >= 4:
                if sync == "on":
                    await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                    return
                await sync_admin(mp[5:], message)
            elif mp[:6] == "logout" and level >= 4:
                if sync == "on":
                    await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                    return
                await logout_admin(mp[7:], message)
            elif mp[:4] == "help" and level >= 1:
                await help(message)
            elif mp[:4] == "lock" and level >= 5:
                await adm_maintenance(mp[5:], message)
        else:
            maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='ticket'").fetchone()[0]
            if maintenance == "on":
                await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
                return
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
            maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='login'").fetchone()[0]
            if maintenance == "on":
                await member.send(f"Hello and welcome to the {member.guild.name} server!\n\nThis server is powered by the Omega Protocol bot and therefore has automatic permissions based on your account on the 42 intranet.\n\n**Please authenticate via the /login command\n\nFor any problem with this step, I invite you to PM the bot with your request\n\nThe Omega master, Ngennaro")
                return
            uid = uuid.uuid4()
            cursor.execute(f"DELETE FROM temp_auth WHERE discord_id={member.id}")
            cursor.execute(f"INSERT INTO temp_auth (discord_id, code) VALUES ({member.id},'{uid}')")
            db.commit()
            await member.send(f"Hello and welcome to the {member.guild.name} server!\n\nThis server is powered by the Omega Protocol bot and therefore has automatic permissions based on your account on the 42 intranet.\n\n**Please authenticate via this link**\n{redirect}{uid}\n\nFor any problem with this step, I invite you to PM the bot with your request\n\nThe Omega master, Ngennaro")
        except :
            print(f"____________________\nfail to send a message to {member}")

#####################################################################################################################################################

def init_api():
    global api
    client_id = os.getenv('API_UID')
    client_secret = os.getenv('API_SECRET')
    client = BackendApplicationClient(client_id=client_id)
    api = OAuth2Session(client=client)
    token = api.fetch_token(token_url='https://api.intra.42.fr/oauth/token', client_id=client_id, client_secret=client_secret)
    return(api)


async def request(url) :
    try :
        raw = api.get(f'https://api.intra.42.fr/v2/{url}')
    except :
        init_api()
        raw = api.get(f'https://api.intra.42.fr/v2/{url}')
    finally :
        if str(raw) == "<Response [200]>" or str(raw) == "<Response [404]>":
            return raw.json()
        else:
            await print(f"bad request with : {url}")
            return raw.json()

#####################################################################################################################################################

async def update(login, id):
    user = await client.fetch_user(id)
    guild_list = user.mutual_guilds
    #campus init#
    student = await request(f'users/{login}')
    campus_list = student['campus']
    campus_list_id = []
    campus_list_name = []
    for campus in campus_list:
        campus_list_id.append(campus['id'])
        campus_list_name.append(campus['name'])
    
    #cursus init#
    student_cursus = student['cursus_users']
    student_cursus_id = []
    student_cursus_data = []
    for current in student_cursus:
        cursus = current['cursus']
        student_cursus_id.append(cursus['id'])
        new = []
        new.append(cursus['id'])
        now = datetime.now()
        begin = datetime.strptime(current['begin_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        if (current['end_at'] == None):
            end = now
        else:
            end = datetime.strptime(current['end_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        if (now > begin and now <= end):
            new.append("in")
        else:
            new.append("out")
        student_cursus_data.append(new)
    
    #goups init#
    student_groups = student['groups']
    student_groups_id = []
    for current in student_groups:
        student_groups_id.append(current['id'])
    
    #project init#
    student_project = student['projects_users']
    student_project_id = []
    student_project_data = []
    for current in student_project:
        project = current['project']
        student_project_id.append(project['id'])
        new = []
        new.append(project['id'])
        if (current['validated?'] == True):
            new.append(3)
        elif (current['status'] == "in_progress" or current['status'] == "waiting_for_correction"):
            new.append(1)
        elif (current['status'] == "finished"):
            new.append(2)
        else:
            new.append(0)
        student_project_data.append(new)
    
    #coa init#
    student_coa = await request(f'users/{login}/coalitions_users')
    student_coa_id = []
    for current in student_coa:
        student_coa_id.append(current['coalition_id'])
    
    #years init#
    student_years = student['pool_year']

    for guild in guild_list:
        #nick sync#
        data_list = cursor.execute(f"SELECT campus_id,format FROM 'nick' WHERE guild_id='{guild.id}'").fetchall()
        member =  guild.get_member(id)
        for data in data_list:
            campus_id = data[0]
            name = data[1]
            name = name.replace("&login", login)
            name = name.replace("&campus", ','.join(campus_list_name))
            if (campus_id in campus_list_id or campus_id == 0):
                try:
                    if (member.nick != name):
                        if (len(name) > 32):
                            print(f"max len for nick : {login}, on {guild.name}")
                            name = name[:32]
                        await member.edit(nick=name)
                except:
                        print(f"403 for nick : {login}, on {guild.name}")
        
        #cursus sync#
        data_list = cursor.execute(f"SELECT campus_id,intra_id,discord_id FROM 'cursus' WHERE guild_id='{guild.id}'").fetchall()
        for data in data_list:
            try:
                campus_id = data[0]
                groups = data[1]
                discord_id = data[2]
                role = guild.get_role(discord_id)
                
                if (campus_id in campus_list_id or campus_id == 0):
                    if (groups in student_cursus_id):
                        for current in student_cursus_data:
                            if (current[0] == groups and current[1] == "in"  and role not in member.roles):
                                await member.add_roles(role)
                            elif (current[0] == groups and current[1] == "out" and role in member.roles):
                                await member.remove_roles(role)
                    elif (groups not in student_cursus_id and role in member.roles):
                        await member.remove_roles(role)
            except:
                print(f"error with role intra: {groups}, discord:{discord_id} on {guild.name}")
        
        #groups sync#
        data_list = cursor.execute(f"SELECT campus_id,intra_id,discord_id FROM 'groups' WHERE guild_id='{guild.id}'").fetchall()
        for data in data_list:
            try:
                campus_id = data[0]
                groups = data[1]
                discord_id = data[2]
                role = guild.get_role(discord_id)
                if (campus_id in campus_list_id or campus_id == 0):
                    if (groups in student_groups_id and role not in member.roles):
                        await member.add_roles(role)
                    elif (groups not in student_groups_id and role in member.roles):
                        await member.remove_roles(role)
            except:
                print(f"error with role intra: {groups}, discord:{discord_id} on {guild.name}")
        
        #project sync#
        data_list = cursor.execute(f"SELECT campus_id,intra_id,discord_id,in_progress,finished,validated FROM 'project' WHERE guild_id='{guild.id}'").fetchall()
        for data in data_list:
            try:
                campus_id = data[0]
                groups = data[1]
                discord_id = data[2]
                in_progress = data[3]
                finished = data[4]
                validated = data[5]
                role = guild.get_role(discord_id)
                if (campus_id in campus_list_id or campus_id == 0):
                    if (groups in student_project_id):
                        for current in student_project_data:
                            if (current[0] == groups and role not in member.roles):
                                if (current[1] == 1 and in_progress == 1):
                                    await member.add_roles(role)
                                elif (current[1] == 2 and finished == 1):
                                    await member.add_roles(role)
                                elif (current[1] == 3 and validated == 1):
                                    await member.add_roles(role)
                            if (current[0] == groups and role in member.roles):
                                if (current[1] == 1 and in_progress == 0):
                                    await member.remove_roles(role)
                                elif (current[1] == 2 and finished == 0):
                                    await member.remove_roles(role)
                                elif (current[1] == 3 and validated == 0):
                                    await member.remove_roles(role)
                    elif (groups not in student_project_id and role in member.roles):
                        await member.remove_roles(role)

            except:
                print(f"error with role intra: {groups}, discord:{discord_id} on {guild.name}")
        
        #coa sync#
        data_list = cursor.execute(f"SELECT campus_id,intra_id,discord_id FROM 'coa' WHERE guild_id='{guild.id}'").fetchall()
        for data in data_list:
            try:
                campus_id = data[0]
                coa = data[1]
                discord_id = data[2]
                role = guild.get_role(discord_id)
                if (campus_id in campus_list_id or campus_id == 0):
                    if (coa in student_coa_id and role not in member.roles):
                        await member.add_roles(role)
                    elif (coa not in student_coa_id and role in member.roles):
                        await member.remove_roles(role)
            except:
                print(f"error with role intra: {coa}, discord:{discord_id} on {guild.name}")
        
        #years sync#
        data_list = cursor.execute(f"SELECT campus_id,intra_id,discord_id FROM 'years' WHERE guild_id='{guild.id}'").fetchall()
        for data in data_list:
            try:
                campus_id = data[0]
                years = data[1]
                discord_id = data[2]
                role = guild.get_role(discord_id)
                years = int(years)
                student_years = int(student_years)
                if (campus_id in campus_list_id or campus_id == 0):
                    if (years == student_years and role not in member.roles):
                        await member.add_roles(role)
                    elif (years != student_years and role in member.roles):
                        await member.remove_roles(role)
            except:
                print(f"error with role intra: {years}, discord:{discord_id} on {guild.name}")

async def disconect(id):
    user = await client.fetch_user(id)
    guild_list = user.mutual_guilds
    for guild in guild_list:
        member =  guild.get_member(int(id))
        #cursus sync#    
        data_list = cursor.execute(f"SELECT discord_id FROM 'cursus' WHERE guild_id='{guild.id}'").fetchall()
        for data in data_list:
            try:
                data = data[0]
                role = guild.get_role(data)
                if (role in member.roles):
                    await member.remove_roles(role)
            except:
                print(f"error to remove: {role}, discord:{data} on {guild.name}")
        
        #groups sync#
        data_list = cursor.execute(f"SELECT discord_id FROM 'groups' WHERE guild_id='{guild.id}'").fetchall()
        for data in data_list:
            try:
                data = data[0]
                role = guild.get_role(data)
                if (role in member.roles):
                    await member.remove_roles(role)
            except:
                print(f"error to remove: {role}, discord:{data} on {guild.name}")
        
        #project sync#
        data_list = cursor.execute(f"SELECT discord_id FROM 'project' WHERE guild_id='{guild.id}'").fetchall()
        for data in data_list:
            try:
                data = data[0]
                role = guild.get_role(data)
                if (role in member.roles):
                    await member.remove_roles(role)
            except:
                print(f"error to remove: {role}, discord:{data} on {guild.name}")
        #coa sync#
        data_list = cursor.execute(f"SELECT discord_id FROM 'coa' WHERE guild_id='{guild.id}'").fetchall()
        for data in data_list:
            try:
                data = data[0]
                role = guild.get_role(data)
                if (role in member.roles):
                    await member.remove_roles(role)
            except:
                print(f"error to remove: {role}, discord:{data} on {guild.name}")
        
        #years sync#
        data_list = cursor.execute(f"SELECT discord_id FROM 'years' WHERE guild_id='{guild.id}'").fetchall()
        for data in data_list:
            try:
                data = data[0]
                role = guild.get_role(data)
                if (role in member.roles):
                    await member.remove_roles(role)
            except:
                print(f"error to remove: {role}, discord:{data} on {guild.name}")

async def main():
    i = 1
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='sync_task'").fetchone()[0]
    if maintenance == "on":
        return
    number = int(cursor.execute(f"SELECT seq FROM 'sqlite_sequence' WHERE name='users'").fetchone()[0])
    if (not number):
        await asyncio.sleep(5)
        new = cursor.execute(f"SELECT discord_id,intra_id FROM 'new_users'").fetchall()
        for current in new:
                id = current[0]
                login = current[1]

                print(f"____________________\nWe have now add : {id} {login}")
                cursor.execute(f"DELETE FROM users WHERE discord_id={id}")
                db.commit()
                dobble_login = cursor.execute(f"SELECT discord_id FROM 'users' WHERE intra_id='{login}'").fetchall()
                for dobble in dobble_login:
                    if (dobble[0] != id):
                        await disconect(dobble[0])
                cursor.execute(f"DELETE FROM users WHERE intra_id='{login}'")
                cursor.execute(f"DELETE FROM new_users WHERE discord_id={id} and intra_id='{login}'")
                db.commit()
                await update(login,id)
                cursor.execute(f"INSERT INTO 'users' (discord_id, intra_id) VALUES ({id},'{login}')")
                db.commit()
    while (i <= number and maintenance == "off"):
        maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='sync_task'").fetchone()[0]
        new = cursor.execute(f"SELECT discord_id,intra_id FROM 'new_users'").fetchall()
        if (not new):
            try :
                login = cursor.execute(f"SELECT intra_id FROM 'users' WHERE omega_id='{i}'").fetchone()[0]
                id = int(cursor.execute(f"SELECT discord_id FROM 'users' WHERE omega_id='{i}'").fetchone()[0])
                await update(login, id)
                await asyncio.sleep(0.5)

            except :
                await asyncio.sleep(0.15)
            i = i + 1
        else :
            for current in new:
                id = current[0]
                login = current[1]

                cursor.execute(f"DELETE FROM users WHERE discord_id={id}")
                db.commit()
                dobble_login = cursor.execute(f"SELECT discord_id FROM 'users' WHERE intra_id='{login}'").fetchall()
                for dobble in dobble_login:
                    if (dobble[0] != id):
                        await disconect(dobble[0])
                cursor.execute(f"DELETE FROM users WHERE intra_id='{login}'")
                cursor.execute(f"DELETE FROM new_users WHERE discord_id={id} and intra_id='{login}'")
                db.commit()
                await update(login,id)
                cursor.execute(f"INSERT INTO 'users' (discord_id, intra_id) VALUES ({id},'{login}')")
                db.commit()

##################################################setup discord and call token##################################################################

@tasks.loop(seconds=20)
async def presence():
    maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='status'").fetchone()[0]
    if maintenance == "on":
        game = Game(name="🚧 maintenance 🚧")
        await client.change_presence(status=Status.do_not_disturb, activity=game)
        return
    for status in status_list:
        maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='status'").fetchone()[0]
        if maintenance == "on":
            game = Game(name="🚧 maintenance 🚧")
            await client.change_presence(status=Status.do_not_disturb, activity=game)
            return
        game = Game(name=status)
        await client.change_presence(status=Status.do_not_disturb, activity=game)
        await asyncio.sleep(20)

status_list = ["Someone else broke it"]

@client.event
async def on_ready():
    await tree.sync()
    presence.start()
    while (client.get_guild(int(1084295027783639080)) != None):
        await main()
        maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='sync_task'").fetchone()[0]
        while maintenance == "on":
            await asyncio.sleep(2)
            maintenance = cursor.execute(f"SELECT status FROM 'maintenance' WHERE part='sync_task'").fetchone()[0]
    print("Unautorized bot version, please contact ngennaro (Gennaron#7378)")
    ngennaro = client.get_user(626861778030034945)
    if ngennaro != None:
        await ngennaro.send(f"Unautorized version of omega is runing as {client.user}")
    module_list = cursor.execute(f"SELECT part,status FROM 'maintenance'").fetchall()
    for module in module_list:
        cursor.execute(f"UPDATE 'maintenance' SET status='on' WHERE part='{module[0]}'")
        db.commit()

client.run(os.getenv('BOT_TOKEN'))
