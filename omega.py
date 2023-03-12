import discord
from discord import *
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

omega_master = [626861778030034945,289850175713837058,403231056003596298]
redirect = f"{os.getenv('DOMAIN')}/api?code="

def omega_cooldown(interaction: Interaction):
    if interaction.user.id in omega_master:
        return None
    return app_commands.Cooldown(3, 3600)

#####################################################################################################################################################

@tree.command(name = "help", description = "Send the bot command list")
async def soon(interaction: Interaction):
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
@app_commands.checks.dynamic_cooldown(omega_cooldown)
async def sign_up(interaction: Interaction, discord_id: str, login: str):
    uid = uuid.uuid4()
    cursor.execute(f"DELETE FROM temp_auth WHERE discord_id={interaction.user.id}")
    cursor.execute(f"INSERT INTO temp_auth (discord_id, code) VALUES ({interaction.user.id},'{uid}')")
    db.commit()
    await interaction.response.send_message(f"Merci de suivre la procedure ci dessous\n{redirect}{uid}", ephemeral = True)


@sign_up.error
async def on_test_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)
#####################################################################################################################################################

@tree.command(name = "logout", description = "remove all your acces and your omega connection")
@app_commands.checks.dynamic_cooldown(omega_cooldown)
async def logout(interaction: Interaction):
    cursor.execute(f"DELETE FROM users WHERE discord_id={interaction.user.id}")
    db.commit()
    await interaction.response.send_message(f"You are now logout", ephemeral = True)
    await disconect(interaction.user.id)

@logout.error
async def on_test_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)

#####################################################################################################################################################

@tree.command(name = "ping", description = "send the bot ping")
async def ping(interaction: Interaction):
    await interaction.response.send_message(f"{round((client.latency*1000),1)}ms", ephemeral = True)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "sync", description = "set the config parameters on the sever")
@app_commands.guild_only()
@app_commands.choices(type=[
    app_commands.Choice(name = 'cursus', value = 1),
    app_commands.Choice(name = 'groups', value = 2),
    app_commands.Choice(name = 'coa', value = 3),
    app_commands.Choice(name = 'years', value = 4),
])
async def sync(interaction: Interaction,type: app_commands.Choice[int], intra_id: int, role_id: str, campus_id: int):
    if (not interaction.user.guild_permissions.administrator and not interaction.user.id in omega_master):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True)
        return
    cursor.execute(f"INSERT INTO {type.name} (campus_id,intra_id, guild_id, discord_id) VALUES ({campus_id},{intra_id},{interaction.guild_id},{int(role_id)})")
    db.commit()
    await interaction.response.send_message(f"configuration successfully update", ephemeral = True)

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
async def sync_project(interaction: Interaction, intra_id: int, in_progress: app_commands.Choice[int], finished: app_commands.Choice[int], validated: app_commands.Choice[int], role_id: str, campus_id: int):
    if (not interaction.user.guild_permissions.administrator and not interaction.user.id in omega_master):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True)
        return
    
    cursor.execute(f"INSERT INTO project (campus_id,intra_id,in_progress,finished,validated,guild_id,discord_id) VALUES ({campus_id},{intra_id},{in_progress.value},{finished.value},{validated.value},{interaction.guild_id},{int(role_id)})")
    db.commit()
    await interaction.response.send_message(f"configuration successfully update", ephemeral = True)
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "nick", description = "set the nick parameters on the sever (&login and &campus works)")
@app_commands.guild_only()
async def nick(interaction: Interaction,namming_pattern: str,campus_id: int):
    if (not interaction.user.guild_permissions.administrator and not interaction.user.id in omega_master):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True)
        return
    cursor.execute(f"INSERT INTO nick (campus_id,format,guild_id) VALUES ({campus_id},'{namming_pattern}',{interaction.guild.id})")
    db.commit()
    if (len(namming_pattern) > 20):
        await interaction.response.send_message(f"configuration successfully update\nWarning, the max len for a nickname is 32 so you can have problem", ephemeral = True)
    else:
        await interaction.response.send_message(f"configuration successfully update", ephemeral = True)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "nick_reset", description = "reset the nick parameters on the sever")
@app_commands.guild_only()
async def nick_reset(interaction: Interaction):
    if (not interaction.user.guild_permissions.administrator and not interaction.user.id in omega_master):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True)
        return
    cursor.execute(f"DELETE FROM nick WHERE guild_id={interaction.guild.id}")
    db.commit()
    await interaction.response.send_message(f"configuration successfully update", ephemeral = True)

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
async def delete(interaction: Interaction,type: app_commands.Choice[int], id_from: app_commands.Choice[int], id: str):
    if (not interaction.user.guild_permissions.administrator and not interaction.user.id in omega_master):
        await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True)
        return
    if (id_from.name == "role_id"):
        cursor.execute(f"DELETE FROM {type.name} WHERE discord_id={int(id)} and guild_id={interaction.guild.id}")
    elif (id_from.name == "intra_id"):
        cursor.execute(f"DELETE FROM {type.name} WHERE intra_id={int(id)} and guild_id={interaction.guild.id}")
    db.commit()
    await interaction.response.send_message(f"configuration successfully update", ephemeral = True)

#####################################################################################################################################################

async def help(message):
    title = f"Admin help for Potocole Omega"
    color = random.randint(0, 16777215)
    color = Colour(color) 
    embed = Embed(title = f"{title}",color = color)
    embed.add_field(name = "___________", value = f"utilities", inline = False)
    embed.add_field(name = "send", value = f"envoie un mp avec le bot", inline = False)
    embed.add_field(name = "sync", value = f"syncronise un utilisateur avec omega", inline = False)
    embed.add_field(name = "logout", value = f"déconecte un utilisateur", inline = False)
    embed.add_field(name = "play", value = f"set le statut du bot", inline = False)
    await message.channel.send(embed=embed)

async def send(command, message):
    id = command[:18]
    content = command[19:]
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
    if (message.author != ngennaro):
        embed = Embed(title = f"Mesage from: {message.author} to: {member}", description=f"{content}")
        if (str(message.author.avatar) != "None"):
            embed.set_thumbnail(url=message.author.avatar.url)
        embed.set_footer(text = f"id : {message.author.id} , {member.id}")
        await ngennaro.send(embed=embed)

async def status(command, message):
    game = Game(command)
    await client.change_presence(status=Status.online, activity=game)
    await message.channel.send(f"Now playing : {command}")

async def sync_admin(command, message):
    discord_id = command[:18]
    intra_id = command[19:]
    pdt = await message.channel.send("Waiting...")
    await update(intra_id,int(discord_id))
    cursor.execute(f"INSERT INTO users (discord_id,intra_id) VALUES ({discord_id},'{intra_id}')")
    db.commit()
    await message.channel.send("Success")
    await pdt.delete()

async def logout_admin(command, message):
    pdt = await message.channel.send("Waiting...")
    if command[:5] == "login" or command[:5] == "intra":
        command = command[6:]
        dobble_login = cursor.execute(f"SELECT discord_id FROM 'users' WHERE intra_id='{command}'").fetchall()
        cursor.execute(f"DELETE FROM users WHERE intra_id='{command}'")
        db.commit()
        for dobble in dobble_login:
            await disconect(dobble[0])
    else:
        print(command)
        cursor.execute(f"DELETE FROM users WHERE discord_id={command}")
        db.commit()
        await disconect(command)
    
    await message.channel.send("Success")
    await pdt.delete()

@client.event
async def on_message(message):
    if (message.author == client.user):
        return
    if (str(message.channel.type) == "private"):
        if (message.author.id in omega_master):
            mp = message.content
            if mp[:4] == "send":
                await send(mp[5:], message)
            elif mp[:4] == "play":
                await status(mp[5:], message)
            elif mp[:4] == "sync":
                await sync_admin(mp[5:], message)
            elif mp[:6] == "logout":
                await logout_admin(mp[7:], message)
            else:
                await help(message)
        else:
            embed = Embed(title = f"Mp from : {message.author}", description=f"{message.content}")
            embed.set_footer(text = f"id : {message.author.id}")
            if (str(message.author.avatar) != "None"):
                embed.set_thumbnail(url=message.author.avatar.url)
            await ngennaro.send(embed=embed)
            await message.channel.send(f"Succesfully send to the administrator")

#####################################################################################################################################################

@client.event
async def on_member_join(member):
    user = cursor.execute(f"SELECT omega_id FROM 'users' WHERE discord_id='{member.id}'").fetchone()
    if (not user):
        uid = uuid.uuid4()
        cursor.execute(f"DELETE FROM temp_auth WHERE discord_id={member.id}")
        cursor.execute(f"INSERT INTO temp_auth (discord_id, code) VALUES ({member.id},'{uid}')")
        db.commit()
        try :
            await member.send(f"Hello and welcome to the {member.guild.name} server!\n\nThis server is powered by the Omega Protocol bot and therefore has automatic permissions based on your account on the 42 intranet.\n\n**Please authenticate via this link**\n{redirect}{uid}\n\nFor any problem with this step, I invite you to PM the bot with your request\n\nThe Omega master, Ngennaro")
        except :
            print(f"____________________\nfail to send a message to {member}")

#####################################################################################################################################################

def init_api():
    global api
    client_id = os.getenv('INTRA_ID')
    client_secret = os.getenv('INTRA_SECRET')
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
                        await member.edit(nick=name)
                except:
                    if (len(name) > 32):
                        print(f"max len for nick : {login}, on {guild.name}")
                    else:
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
                    await disconect(dobble[0])
                cursor.execute(f"DELETE FROM users WHERE intra_id='{login}'")
                cursor.execute(f"DELETE FROM new_users WHERE discord_id={id} and intra_id='{login}'")
                db.commit()
                await update(login,id)
                cursor.execute(f"INSERT INTO 'users' (discord_id, intra_id) VALUES ({id},'{login}')")
                db.commit()
    while (i <= number):
        new = cursor.execute(f"SELECT discord_id,intra_id FROM 'new_users'").fetchall()
        if (not new):
            try :
                login = cursor.execute(f"SELECT intra_id FROM 'users' WHERE omega_id='{i}'").fetchone()[0]
                id = int(cursor.execute(f"SELECT discord_id FROM 'users' WHERE omega_id='{i}'").fetchone()[0])
                print(f"____________________\n{login}")
                await update(login, id)
                print("update done")
                await asyncio.sleep(0.5)

            except :
                await asyncio.sleep(0.5)
            i = i + 1
        else :
            for current in new:
                id = current[0]
                login = current[1]

                print(f"____________________\nWe have now add : {id} {login}")
                cursor.execute(f"DELETE FROM users WHERE discord_id={id}")
                db.commit()
                dobble_login = cursor.execute(f"SELECT discord_id FROM 'users' WHERE intra_id='{login}'").fetchall()
                for dobble in dobble_login:
                    await disconect(dobble[0])
                cursor.execute(f"DELETE FROM users WHERE intra_id='{login}'")
                cursor.execute(f"DELETE FROM new_users WHERE discord_id={id} and intra_id='{login}'")
                db.commit()
                await update(login,id)
                cursor.execute(f"INSERT INTO 'users' (discord_id, intra_id) VALUES ({id},'{login}')")
                db.commit()


##################################################setup discord and call token##################################################################

@client.event
async def on_ready():
    await tree.sync()
    game = Game(name=f"someone else broke it")
    await client.change_presence(status=Status.online, activity=game)
    global ngennaro
    ngennaro = await client.fetch_user(626861778030034945)
    print(f"We have logged in as {client.user}.")
    while (1):
        await main()

client.run(os.getenv('BOT_TOKEN'))
