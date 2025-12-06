import calendar
import discord
from discord import *
from discord.ext import tasks
import random
import datetime
import uuid
import time
from time import strptime
from datetime import datetime
import asyncio

import os

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

import json
from builtins import input

import mysql.connector

MASTER_GUILD_ID = 1084295027783639080
LOGS_CHANNEL_ID = 1088582242290368572

connected = False
while (connected != True):
	try:
		db = mysql.connector.connect(
		  host=os.getenv('MYSQL_HOST'),
		  user=os.getenv('MYSQL_USER'),
		  password=os.getenv('MYSQL_PASSWORD'),
		  database=os.getenv('MYSQL_DATABASE')
		)
		connected = True
	except:
		print("Db connection failed, retry in 5 seconds...")
		time.sleep(5)
cursor = db.cursor(buffered=True)

intents = Intents.default()
intents.members = True
client = Client(intents=intents)
tree = app_commands.CommandTree(client)

redirect = f"{os.getenv('DOMAIN')}/api?code="

def admin_check(id):
	guild = client.get_guild(int(MASTER_GUILD_ID))
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
	cursor.execute(f"SELECT status FROM maintenance WHERE part='base'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
		return
	title = f"Help for Potocole Omega"
	color = random.randint(0, 16777215)
	color = Colour(color) 
	embed = Embed(title = f"{title}", url = "https://profile.intra.42.fr" , color = color)
	embed.add_field(name = "___________", value = f"USERS", inline = False)
	embed.add_field(name = "login", value = f"conectez vous au bot", inline = False)
	embed.add_field(name = "logout", value = f"déconnectez vous du bot", inline = False)
	embed.add_field(name = "___________", value = f"utilities", inline = False)
	embed.add_field(name = "ping", value = f"renvoie le ping du bot", inline = False)
	embed.add_field(name = "issue", value = f"for any issue mp the bot", inline = False)
	embed.add_field(name = "___________", value = f"admin command", inline = False)
	embed.add_field(name = "sync", value = f"set the config parameters on the sever", inline = False)
	embed.add_field(name = "sync_piscine", value = f"set the piscine sync parameters on the sever", inline = False)
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
	cursor.execute(f"SELECT status FROM maintenance WHERE part='login'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
		return
	uid = uuid.uuid4()
	cursor.execute(f"DELETE FROM temp_auth WHERE discord_id={interaction.user.id}")
	cursor.execute(f"INSERT INTO temp_auth (discord_id, code) VALUES ({interaction.user.id},'{uid}')")
	db.commit()
	await interaction.response.send_message(f"Please follow the procedure below\n{redirect}{uid}", ephemeral = True, delete_after=30)

@sign_up.error
async def on_test_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
	if isinstance(error, app_commands.CommandOnCooldown):
		await interaction.response.send_message("You are on cooldown, please retry later", ephemeral=True, delete_after=2)
#####################################################################################################################################################

@tree.command(name = "logout", description = "remove all your acces and your omega connection")
@app_commands.checks.dynamic_cooldown(logout_cooldown)
async def logout(interaction: Interaction):
	cursor.execute(f"SELECT status FROM maintenance WHERE part='login'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
		return
	cursor.execute(f"DELETE FROM users WHERE discord_id={interaction.user.id}")
	db.commit()
	await interaction.response.send_message(f"You are now logout", ephemeral = True, delete_after=2)
	await disconnect(interaction.user.id)

@logout.error
async def on_test_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
	if isinstance(error, app_commands.CommandOnCooldown):
		await interaction.response.send_message("You are on cooldown, please retry later", ephemeral=True, delete_after=3)

#####################################################################################################################################################

@tree.command(name = "ping", description = "send the bot ping")
async def ping(interaction: Interaction):
	cursor.execute("SELECT status FROM maintenance WHERE part='base'")
	maintenance = cursor.fetchone()[0]
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
	cursor.execute(f"SELECT status FROM maintenance WHERE part='sync_config'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
		return
	level = admin_check(interaction.user.id)
	role_id = role.id
	if (not interaction.user.guild_permissions.administrator and level <= 2):
		await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
		return
	cursor.execute(f"INSERT INTO {type.name} (campus_id, intra_id, guild_id, discord_id) VALUES (%s, %s, %s, %s)" , (campus_id, intra_id, interaction.guild_id, role_id))
	db.commit()
	await interaction.response.send_message(f"configuration successfully update", ephemeral = True, delete_after=2)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "sync_piscine", description = "set the piscine sync parameters on the sever")
@app_commands.guild_only()
@app_commands.choices(pool_month=[
	app_commands.Choice(name = 'January', value = 1),
	app_commands.Choice(name = 'Febuary', value = 2),
	app_commands.Choice(name = 'March', value = 3),
	app_commands.Choice(name = 'April', value = 4),
	app_commands.Choice(name = 'May', value = 5),
	app_commands.Choice(name = 'June', value = 6),
	app_commands.Choice(name = 'July', value = 7),
	app_commands.Choice(name = 'August', value = 8),
	app_commands.Choice(name = 'September', value = 9),
	app_commands.Choice(name = 'October', value = 10),
	app_commands.Choice(name = 'November', value = 11),
	app_commands.Choice(name = 'December', value = 12),
])
@app_commands.describe(pool_month='the pool_month to sync with role', pool_year='the pool_year to sync with role', role='the role to give', campus_id='the campus needed')
async def sync_project(interaction: Interaction, pool_month: app_commands.Choice[int], pool_year: int, role: discord.Role, campus_id: int=0):
	cursor.execute(f"SELECT status FROM maintenance WHERE part='sync_config'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
		return
	level = admin_check(interaction.user.id)
	role_id = role.id
	if (not interaction.user.guild_permissions.administrator and level <= 2):
		await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
		return
	cursor.execute("INSERT INTO piscine (campus_id, pool_month, pool_year, guild_id, discord_id) VALUES (%s, %s, %s, %s, %s)", (campus_id, calendar.month_name[pool_month.value].lower(), pool_year, interaction.guild_id, role_id))
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
	cursor.execute(f"SELECT status FROM maintenance WHERE part='sync_config'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
		return
	level = admin_check(interaction.user.id)
	role_id = role.id
	if (not interaction.user.guild_permissions.administrator and level <= 2):
		await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
		return
	cursor.execute("INSERT INTO project (campus_id, intra_id, in_progress, finished, validated, guild_id, discord_id) VALUES (%s, %s, %s, %s, %s, %s, %s)", (campus_id, intra_id, in_progress.value, finished.value, validated.value, interaction.guild_id, role_id))
	db.commit()
	await interaction.response.send_message(f"configuration successfully update", ephemeral = True, delete_after=2)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "nick", description = "set the nick parameters on the sever (32 chr is the max len for a nickname)")
@app_commands.guild_only()
@app_commands.describe(namming_pattern='the patern to aply (&login, &campus , &display_name, &usual_name, &first_name, &wallet, &correction_point, &pool_month and &pool_years are a dynamic value)', campus_id='the campus needed')
async def nick(interaction: Interaction,namming_pattern: str, campus_id: int=0):
	cursor.execute(f"SELECT status FROM maintenance WHERE part='sync_config'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
		return
	level = admin_check(interaction.user.id)
	if (not interaction.user.guild_permissions.administrator and level <= 2):
		await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
		return
	cursor.execute("INSERT INTO nick (campus_id,format,guild_id) VALUES (%s,%s,%s)", (campus_id,namming_pattern,interaction.guild.id))
	db.commit()
	if (len(namming_pattern) > 20):
		await interaction.response.send_message(f"configuration successfully update\nWarning, the max len for a nickname is 32 so you can have problem", ephemeral = True, delete_after=3)
	else:
		await interaction.response.send_message(f"configuration successfully update", ephemeral = True, delete_after=2)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "config", description = "Send the current server configuration")
@app_commands.guild_only()
async def config_list(interaction: Interaction):
	cursor.execute(f"SELECT status FROM maintenance WHERE part='sync_config'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
		return
	level = admin_check(interaction.user.id)
	if (not interaction.user.guild_permissions.administrator and level <= 2):
		await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
		return
	
	msg = "```You have currently this configuration\n(the first two parameters are discord_role|intra_id)```\n"

	msg = f"{msg}``-> nick <-``\n"
	cursor.execute(f"SELECT campus_id,format FROM nick WHERE guild_id={interaction.guild_id}")
	nick_list = cursor.fetchall()
	for nick in nick_list:
		msg = f"{msg}{nick[1]}, campus_id: {nick[0]}\n"
	msg = f"{msg}\n"

	items = ["cursus", "coa", "groups", "years"]
	for item in items:
		msg = msg + f"``-> {item} <-``\n"
		cursor.execute(f"SELECT campus_id,intra_id,discord_id FROM {item} WHERE guild_id={interaction.guild_id}")
		sub_item_list = cursor.fetchall()
		for sub_item in sub_item_list:
			msg = f"{msg}<@&{sub_item[2]}> | {sub_item[1]}, campus_id: {sub_item[0]}\n"
		msg = f"{msg}\n"

	msg = f"\n{msg}``-> piscine <-``\n"
	cursor.execute(f"SELECT campus_id,pool_month,pool_year,discord_id FROM piscine WHERE guild_id={interaction.guild_id}")
	piscine_list = cursor.fetchall()
	for piscine in piscine_list:
		msg = f"{msg}<@&{piscine[3]}> | {piscine[1]} {piscine[2]}, campus_id: {piscine[0]}\n"

	msg = f"\n{msg}\n``-> project <-``\n"
	cursor.execute(f"SELECT campus_id,intra_id,discord_id,in_progress,finished,validated FROM project WHERE guild_id={interaction.guild_id}")
	project_list = cursor.fetchall()
	for project in project_list:
		msg = f"{msg}<@&{project[2]}> | {project[1]}, campus_id: {project[0]}, in_progess: {project[3]}, finished: {project[4]}, validated: {project[5]}\n"

	msg = f"{msg}\n```by Protocole Omega```"
	await interaction.response.send_message(msg, ephemeral=True)

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////#

@tree.command(name = "nick_reset", description = "reset the nick parameters on the sever")
@app_commands.guild_only()
async def nick_reset(interaction: Interaction):
	cursor.execute(f"SELECT status FROM maintenance WHERE part='sync_config'")
	maintenance = cursor.fetchone()[0]
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
	app_commands.Choice(name = 'piscine', value = 6),
])
@app_commands.choices(id_from=[
	app_commands.Choice(name = 'intra_id', value = 1),
	app_commands.Choice(name = 'role_id', value = 2),
])
@app_commands.describe(id_from='the type of id', id='the corresponding id')
async def delete(interaction: Interaction,type: app_commands.Choice[int], id_from: app_commands.Choice[int], id: str):
	cursor.execute(f"SELECT status FROM maintenance WHERE part='sync_config'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
		return
	level = admin_check(interaction.user.id)
	if (not interaction.user.guild_permissions.administrator and level <= 2):
		await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True)
		return
	if (id_from.name == "role_id"):
		cursor.execute(f"DELETE FROM {type.name} WHERE discord_id=%s and guild_id=%s", (id, interaction.guild.id))
	elif (id_from.name == "intra_id"):
		cursor.execute(f"DELETE FROM {type.name} WHERE intra_id=%s and guild_id=%s", (id, interaction.guild.id))
	db.commit()
	await interaction.response.send_message(f"configuration successfully update", ephemeral = True)

#####################################################################################################################################################

class Cancel(discord.ui.View):
	
	foo : bool = None
	
	async def on_timeout(self) -> None:
		pass
	
	@discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
	async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_message("Cancelling", delete_after=10)
		self.foo = True
		self.stop()

@client.event
async def on_interaction(interaction=Interaction):
	if str(interaction.type) == "InteractionType.component":
		data = interaction.data
		type = data['component_type']
		custom_id = data['custom_id']
		if type == 2:
			if custom_id[:9] == "reaction_":
				cursor.execute(f"SELECT status FROM maintenance WHERE part='reaction_role'")
				maintenance = cursor.fetchone()[0]
				if maintenance == "on":
					await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
					return
				guild = client.get_guild(interaction.guild_id)
				role = guild.get_role(int(custom_id[9:]))
				try:
					if role in interaction.user.roles:
						await interaction.user.remove_roles(role)
						await interaction.response.send_message(f"Remove {role.name}", ephemeral=True, delete_after=1)
					else:
						await interaction.user.add_roles(role)
						await interaction.response.send_message(f"Add {role.name}", ephemeral=True, delete_after=1)
				except:
					await interaction.response.send_message(f"someting went wrong", ephemeral=True, delete_after=3)
			if custom_id == "delete":
				view = Cancel(timeout=20)
				await interaction.response.send_message("Ticket deleted in 20 second", view=view)
				view.message = message
				await view.wait()
				if view.foo is True:
					return
				elif view.foo is None:
					cursor.execute(f"SELECT user_id FROM ticket WHERE channel_id={interaction.channel_id}")
					user = cursor.fetchone()[0]
					cursor.execute(f"DELETE FROM ticket WHERE channel_id='{interaction.channel_id}'")
					db.commit()
					user = await client.fetch_user(user)
					channel = await client.fetch_channel(interaction.channel_id)
					embed = Embed(title = f"Ticket Close", description=f"Your ticket have been close by the staff team", color=Color.red())
					await user.send(embed=embed)
					await channel.delete()
			if custom_id == "archive":
				view = Cancel(timeout=10)
				await interaction.response.send_message("Ticket archived in 10 second", view=view)
				view.message = message
				await view.wait()
				if view.foo is True:
					return
				elif view.foo is None:
					cursor.execute(f"SELECT user_id FROM ticket WHERE channel_id={interaction.channel_id}")
					user = cursor.fetchone()[0]
					cursor.execute(f"DELETE FROM ticket WHERE channel_id='{interaction.channel_id}'")
					db.commit()
					user = await client.fetch_user(user)
					channel = await client.fetch_channel(interaction.channel_id)
					guild = client.get_guild(int(MASTER_GUILD_ID))
					category = discord.utils.get(guild.categories, id=1090795985820733612)
					await channel.edit(name=f"{user}_old", category=category, sync_permissions=True)
					embed = Embed(title = f"Ticket Close", description=f"Your ticket have been close by the staff team", color=Colour.red())
					await user.send(embed=embed)

#####################################################################################################################################################


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
	cursor.execute(f"SELECT status FROM maintenance WHERE part='reaction_role'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		await interaction.response.send_message(f"🚧 Feature currently in maintenance 🚧", ephemeral = True, delete_after=5)
		return
	level = admin_check(interaction.user.id)
	if (not interaction.user.guild_permissions.administrator and level <= 2):
		await interaction.response.send_message(f"Not allowed !\nYou must be administrator", ephemeral = True, delete_after=2)
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
	custom_id = "reaction_" + str(role.id)
	button = discord.ui.Button(label=label, custom_id=custom_id, style=style)
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
	cursor.execute(f"SELECT status FROM maintenance WHERE part='admin_utils'")
	utils = cursor.fetchone()[0]
	cursor.execute(f"SELECT status FROM maintenance WHERE part='admin_sync'")
	sync = cursor.fetchone()[0]
	cursor.execute(f"SELECT status FROM maintenance WHERE part='status'")
	mstatus = cursor.fetchone()[0]
	if level >= 5:
		embed.add_field(name = "lock", value = f"manage maintenance mod", inline = False)
		if mstatus != "on":
			embed.add_field(name = "status", value = f"envoie les status du bot", inline = False)
			embed.add_field(name = "play", value = f"set un status pour le bot", inline = False)
			embed.add_field(name = "pause", value = f"retire un status du bot", inline = False)
	if level >= 4:
		if sync != "on":
			embed.add_field(name = "sync", value = f"syncronise un utilisateur avec omega", inline = False)
			embed.add_field(name = "logout", value = f"déconecte un utilisateur", inline = False)
		if utils != "on":
			embed.add_field(name = "leave", value = f"quitte un serveur", inline = False)
	if level >= 3:
		if utils != "on":
			embed.add_field(name = "join", value = f"genere une invitation vers le serveur", inline = False)
			embed.add_field(name = "list", value = f"envoie la liste des serveur du bot", inline = False)
			embed.add_field(name = "config", value = f"envoie la configuration de ce serveur", inline = False)
	if level >= 2:
		if utils != "on":
			embed.add_field(name = "send", value = f"envoie un mp avec le bot", inline = False)
	if level >= 1:
		if utils != "on":
			embed.add_field(name = "stats", value = f"donne des chifres sur l'utilisation du bot", inline = False)
	await message.channel.send(embed=embed)

async def stats(message):
	wait = await message.channel.send("waiting...")
	cursor.execute(f"SELECT intra_id FROM users")
	student_count = len(cursor.fetchall())
	cursor.execute(f"SELECT campus_id FROM nick")
	nick_count = len(cursor.fetchall())
	cursor.execute(f"SELECT campus_id FROM cursus")
	cursus_count = len(cursor.fetchall())
	cursor.execute(f"SELECT campus_id FROM coa")
	coalition_count = len(cursor.fetchall())
	cursor.execute(f"SELECT campus_id FROM piscine")
	piscine_count = len(cursor.fetchall())
	cursor.execute(f"SELECT campus_id FROM project")
	project_count = len(cursor.fetchall())
	cursor.execute(f"SELECT campus_id FROM groups")
	groups_count = len(cursor.fetchall())
	cursor.execute(f"SELECT campus_id FROM years")
	years_count = len(cursor.fetchall())

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
	embed.add_field(name = "__Piscine__", value = f"{piscine_count}", inline = True)
	embed.add_field(name = "__Project__", value = f"{project_count}", inline = True)
	embed.add_field(name = "__Groups__", value = f"{groups_count}", inline = True)
	embed.add_field(name = "__Years__", value = f"{years_count}", inline = True)
	await message.channel.send(embed=embed)
	await wait.delete()

async def admin_config(command, message):
	guild = await client.fetch_guild(int(command))
	if not guild:
		await message.channel.send("this guild does not exist")
		return
	msg = f"```{guild.name} have currently this configuration\n(the first two parameters are discord_role|intra_id)```\n"
	msg = f"{msg}``-> nick <-``\n"
	cursor.execute(f"SELECT campus_id,format FROM nick WHERE guild_id={command}")
	nick_list = cursor.fetchall()
	for nick in nick_list:
		msg = f"{msg}{nick[1]}, campus_id: {nick[0]}\n"
	msg = f"{msg}\n"
	items = ["cursus", "coa", "groups", "years"]
	for item in items:
		msg = msg + f"``-> {item} <-``\n"
		cursor.execute(f"SELECT campus_id,intra_id,discord_id FROM {item} WHERE guild_id={command}")
		sub_item_list = cursor.fetchall()
		for sub_item in sub_item_list:
			role = guild.get_role(sub_item[2])
			msg = f"{msg}{role} | {sub_item[1]}, campus_id: {sub_item[0]}\n"
		msg = f"{msg}\n"
	msg = f"\n{msg}``-> piscine <-``\n"
	cursor.execute(f"SELECT campus_id,pool_month,pool_year,discord_id FROM piscine WHERE guild_id={command}")
	piscine_list = cursor.fetchall()
	for piscine in piscine_list:
		role = guild.get_role(piscine[3])
		msg = f"{msg}{role} | {piscine[1]} {piscine[2]}, campus_id: {piscine[0]}\n"
	msg = f"{msg}\n"
	msg = f"\n{msg}``-> project <-``\n"
	cursor.execute(f"SELECT campus_id,intra_id,discord_id,in_progress,finished,validated FROM project WHERE guild_id={command}")
	project_list = cursor.fetchall()
	for project in project_list:
		role = guild.get_role(project[2])
		msg = f"{msg}{role} | {project[1]}, campus_id: {project[0]}, in_progess: {project[3]}, finished: {project[4]}, validated: {project[5]}\n"
	await message.channel.send(msg)

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
	channel = client.get_channel(LOGS_CHANNEL_ID)
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
	cursor.execute(f"SELECT name FROM status")
	status_list = cursor.fetchall()
	if not status_list:
		await message.channel.send("No status currently runing, default mode = \"Someone else broke it\"")
		return
	await message.channel.send("__This status are runing:__")
	for status in status_list:
		send = False
		i += 1
		msg = f"{msg}\n{status[0]}"
		if (i>=15):
			send = True
			i = 0
			await message.channel.send(msg)
			msg = ""
	if (send == False):
		await message.channel.send(msg)

async def new_status(command, message):
	cursor.execute(f"INSERT INTO status (name) VALUES ('{command}')")
	db.commit()
	await message.channel.send(f"Add : {command}")
	channel = client.get_channel(LOGS_CHANNEL_ID)
	title = f"{message.author} set a new status"
	color = random.randint(0, 16777215)
	color = Colour(color) 
	embed = Embed(title = f"{title}",color = color, description=f"{command}")
	if (str(message.author.avatar) != "None"):
		embed.set_thumbnail(url=message.author.avatar.url)
	await channel.send(embed=embed)

async def rm_status(command, message):
	cursor.execute(f"DELETE FROM status WHERE name='{command}'")
	db.commit()
	await message.channel.send(f"Remove : {command}")
	channel = client.get_channel(LOGS_CHANNEL_ID)
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
	channel = client.get_channel(LOGS_CHANNEL_ID)
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
		cursor.execute(f"SELECT discord_id FROM users WHERE intra_id='{command}'")
		dobble_login = cursor.fetchall()
		cursor.execute(f"DELETE FROM users WHERE intra_id='{command}'")
		db.commit()
		for dobble in dobble_login:
			await disconnect(dobble[0])
		channel = client.get_channel(LOGS_CHANNEL_ID)
		title = f"{message.author} logout"
		color = random.randint(0, 16777215)
		color = Colour(color) 
		embed = Embed(title = f"{title}",color = color, description=f"login : {command}")
		if (str(message.author.avatar) != "None"):
			embed.set_thumbnail(url=message.author.avatar.url)
		await channel.send(embed=embed)
	else:
		cursor.execute(f"DELETE FROM users WHERE discord_id={command}")
		db.commit()
		await disconnect(command)
		channel = client.get_channel(LOGS_CHANNEL_ID)
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
	await message.channel.send("__Omega are running on this server:__")
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
	if not guild:
		await message.channel.send("this guild does not exist")
		return
	channel = await guild.fetch_channels()
	for current in channel:
		try:
			invite = await current.create_invite(max_uses = 1, reason = "Omega master request", max_age=3600)
			await message.channel.send(invite)
			channel = client.get_channel(LOGS_CHANNEL_ID)
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
		channel = client.get_channel(LOGS_CHANNEL_ID)
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
	cursor.execute(f"SELECT part,status FROM maintenance")
	module_list = cursor.fetchall()
	if sub == "list":
		title = f"Maintenance module status"
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
			cursor.execute(f"UPDATE maintenance SET status='{command[1]}' WHERE part='{module[0]}'")
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
			cursor.execute(f"UPDATE maintenance SET status='{command[1]}' WHERE part='{module[0]}'")
			db.commit()
			await message.channel.send("Success...")
			return
	await message.channel.send("invalid module")


class Verify(discord.ui.View):
	
	foo : bool = None
	
	async def on_timeout(self) -> None:
		await self.message.channel.send("Ticket abort, Timedout")
	
	@discord.ui.button(label="Submit", style=discord.ButtonStyle.success)
	async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_message("Ticket created with succes\nyou can response here to talk with our staff team")
		self.foo = True
		self.stop()
		
	@discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
	async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.response.send_message("Cancelling")
		self.foo = False
		self.stop()

@client.event
async def on_message(message):
	if (message.author == client.user or str(message.author.discriminator) == "0000"):
		return
	elif (str(message.channel.type) == "private"):
		level = admin_check(message.author.id)
		if (level >= 1):
			cursor.execute(f"SELECT status FROM maintenance WHERE part='admin_utils'")
			utils = cursor.fetchone()[0]
			cursor.execute(f"SELECT status FROM maintenance WHERE part='admin_sync'")
			sync = cursor.fetchone()[0]
			cursor.execute(f"SELECT status FROM maintenance WHERE part='status'")
			mstatus = cursor.fetchone()[0]
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
			elif mp[:6] == "config" and level >= 3:
				if utils == "on":
					await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
					return
				await admin_config(mp[7:], message)
			elif mp[:5] == "leave" and level >= 4:
				if utils == "on":
					await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
					return
				await srv_leave(mp[6:], message)
			elif mp[:6] == "status" and level >= 5:
				if mstatus == "on":
					await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
					return
				await status(mp[7:], message)
			elif mp[:4] == "play" and level >= 5:
				if mstatus == "on":
					await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
					return
				await new_status(mp[5:], message)
			elif mp[:5] == "pause" and level >= 5:
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
			cursor.execute(f"SELECT status FROM maintenance WHERE part='ticket'")
			maintenance = cursor.fetchone()[0]
			if maintenance == "on":
				await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
				return
			
			cursor.execute(f"SELECT channel_id FROM ticket WHERE user_id={message.author.id}")
			channel = cursor.fetchall()
			if (not channel):
				embed = Embed(title = f"Open a support Ticket", description=f"Your a in proccess to create a ticket with the Omega staff\ndo you want to submit it ? \n(Warning the ticket is ony aviable for fix an issue withe *THE BOT*, we can't help you for the cursus or other issue related to 42)", color=Colour.green())

				view = Verify(timeout=50)
				await message.channel.send(embed=embed, view=view)
				view.message = message
				await view.wait()
				if view.foo is None:
					return
				elif view.foo is False:
					return              
				guild = client.get_guild(int(MASTER_GUILD_ID))
				category = discord.utils.get(guild.categories, id=1090772760415973417)
				channel = await guild.create_text_channel(name=f"{message.author}_ticket", category=category)
				view = discord.ui.View(timeout=None)
				button = discord.ui.Button(label="Archive", custom_id=f"archive", style=ButtonStyle.grey)
				view.add_item(button)
				button = discord.ui.Button(label="Close", custom_id=f"delete", style=ButtonStyle.danger)
				view.add_item(button)
				embed = Embed(title = f"Ticket from : {message.author}", description=f"close this ticket with the button below")
				embed.set_footer(text = f"id : {message.author.id}")
				if (str(message.author.avatar) != "None"):
					embed.set_thumbnail(url=message.author.avatar.url)
				await channel.send(embed=embed, view=view)
				cursor.execute(f"INSERT INTO ticket (user_id, channel_id) VALUES ({message.author.id},{channel.id})")
				db.commit()
			else:
				channel = channel[0][0]
				channel = await client.fetch_channel(channel)
				await message.add_reaction('🚀')
			try :
				avatar = await message.author.avatar.read()
				hook = await channel.create_webhook(name=message.author.name, avatar=avatar)
			except :
				hook = await channel.create_webhook(name=message.author.name)
			if (message.content):
				await hook.send(f"{message.content}")
			if (message.attachments):
				for attachment in message.attachments:
					await hook.send(attachment)
			await hook.delete()
	else:
		cursor.execute(f"SELECT status FROM maintenance WHERE part='ticket'")
		maintenance = cursor.fetchone()[0]
		if maintenance == "on":
			await message.channel.send(f"🚧 Feature currently in maintenance 🚧")
			return
		cursor.execute(f"SELECT user_id FROM ticket WHERE channel_id={message.channel.id}")
		channel = cursor.fetchall()
		if (channel and message.content):
			channel = channel[0][0]
			channel = await client.fetch_user(channel)
			content = message.content
			content = content.replace(f"{client.user.mention}", "")
			embed = Embed(title = f"{message.author}", description=f"{content}")
			if (str(message.author.avatar) != "None"):
				embed.set_thumbnail(url=message.author.avatar.url)
			try :
				await channel.send(embed=embed)
				if (message.attachments):
					for attachment in message.attachments:
						await channel.send(attachment)
				await message.add_reaction('🚀')
			except:
				await message.channel.send(f"Fail to mp this user")
				return

#####################################################################################################################################################

@client.event
async def on_member_join(member):
	cursor.execute(f"SELECT omega_id FROM users WHERE discord_id='{member.id}'")
	try:
		user = cursor.fetchone()[0]
	except:
		user = 0
	if (not user):
		try :
			cursor.execute(f"SELECT status FROM maintenance WHERE part='login'")
			maintenance = cursor.fetchone()[0]
			if maintenance == "on":
				await member.send(f"Hello and welcome to the {member.guild.name} server!\n\nThis server is powered by the Omega Protocol bot and therefore has automatic permissions based on your account on the 42 intranet.\n\n**Please authenticate via the /login command\n\nFor any problem with this step, I invite you to PM the bot with your request\n\nThe Omega master, Ngennaro")
				return
			uid = uuid.uuid4()
			cursor.execute(f"DELETE FROM temp_auth WHERE discord_id={member.id}")
			cursor.execute(f"INSERT INTO temp_auth (discord_id, code) VALUES ({member.id},'{uid}')")
			db.commit()
			await member.send(f"Hello and welcome to the {member.guild.name} server!\n\nThis server is powered by the Omega Protocol bot and therefore has automatic permissions based on your account on the 42 intranet.\n\n**Please authenticate via this link**\n{redirect}{uid}\n\nFor any problem with this step, I invite you to PM the bot with your request\n\nThe Omega master, Ngennaro")
		except :
			return

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
	if str(raw) == "<Response [200]>" or str(raw) == "<Response [404]>":
		return raw.json()
	else:
		print(f"bad request with : {url}")
		return raw.json()

#####################################################################################################################################################

async def update(login, id):
	user = await client.fetch_user(id)
	guild_list = user.mutual_guilds
	student = await request(f'users/{login}')
	#base init#
	display_name = student['displayname']
	usual_name = student['usual_full_name']
	first_name = student['usual_first_name']
	if (not first_name):
		first_name = student['first_name']
	wallet = student['wallet']
	correction_point = student['correction_point']
	pool_month = student['pool_month']
	pool_year = student['pool_year']
	#campus init#
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

	#piscine init#
	student_pool_month = student['pool_month']
	student_pool_year = student['pool_year']
	
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
		cursor.execute(f"SELECT campus_id,format FROM nick WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
		member =  guild.get_member(id)
		for data in data_list:
			campus_id = data[0]
			name = data[1]
			name = name.replace("&login", login)
			name = name.replace("&display_name", display_name)
			name = name.replace("&usual_name", usual_name)
			name = name.replace("&first_name", first_name)
			name = name.replace("&wallet", str(wallet))
			name = name.replace("&correction_point", str(correction_point))
			name = name.replace("&pool_month", str(pool_month))
			name = name.replace("&pool_year", str(pool_year))
			name = name.replace("&campus", ','.join(campus_list_name))
			if (campus_id in campus_list_id or campus_id == 0):
				try:
					if (member.nick != name):
						if (len(name) > 32):
							name = name[:32]
						await member.edit(nick=name)
				except:
						continue
		
		#cursus sync#
		cursor.execute(f"SELECT campus_id,intra_id,discord_id FROM cursus WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
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
		cursor.execute(f"SELECT campus_id,intra_id,discord_id FROM groups WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
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

		#piscine sync#
		cursor.execute(f"SELECT campus_id,pool_month,pool_year,discord_id FROM piscine WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
		for piscine in data_list:
			try:
				campus_id = piscine[0]
				pool_month = piscine[1]
				pool_year = piscine[2]
				discord_id = piscine[3]
				role = guild.get_role(discord_id)
				if (campus_id in campus_list_id or campus_id == 0):
					if (str(pool_year) == student_pool_year and pool_month == student_pool_month and role not in member.roles):
						await member.add_roles(role)
					elif ((str(pool_year) != student_pool_year or pool_month != student_pool_month) and role in member.roles):
						await member.remove_roles(role)
			except Exception as e:
				print(f"error {e} with role intra: {pool_month} {pool_year}, discord:{discord_id} on {guild.name}")
		
		#project sync#
		cursor.execute(f"SELECT campus_id,intra_id,discord_id,in_progress,finished,validated FROM project WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
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
		cursor.execute(f"SELECT campus_id,intra_id,discord_id FROM coa WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
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
		cursor.execute(f"SELECT campus_id,intra_id,discord_id FROM years WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
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

async def disconnect(id):
	user = await client.fetch_user(id)
	guild_list = user.mutual_guilds
	for guild in guild_list:
		member =  guild.get_member(int(id))
		#cursus sync#    
		cursor.execute(f"SELECT discord_id FROM cursus WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
		for data in data_list:
			try:
				data = data[0]
				role = guild.get_role(data)
				if (role in member.roles):
					await member.remove_roles(role)
			except:
				print(f"error to remove: {role}, discord:{data} on {guild.name}")
		
		#groups sync#
		cursor.execute(f"SELECT discord_id FROM groups WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
		for data in data_list:
			try:
				data = data[0]
				role = guild.get_role(data)
				if (role in member.roles):
					await member.remove_roles(role)
			except:
				print(f"error to remove: {role}, discord:{data} on {guild.name}")
		
		#piscine sync#
		cursor.execute(f"SELECT discord_id FROM piscine WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
		for data in data_list:
			try:
				data = data[0]
				role = guild.get_role(data)
				if (role in member.roles):
					await member.remove_roles(role)
			except:
				print(f"error to remove: {role}, discord:{data} on {guild.name}")
		#project sync#
		cursor.execute(f"SELECT discord_id FROM project WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
		for data in data_list:
			try:
				data = data[0]
				role = guild.get_role(data)
				if (role in member.roles):
					await member.remove_roles(role)
			except:
				print(f"error to remove: {role}, discord:{data} on {guild.name}")
		#coa sync#
		cursor.execute(f"SELECT discord_id FROM coa WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
		for data in data_list:
			try:
				data = data[0]
				role = guild.get_role(data)
				if (role in member.roles):
					await member.remove_roles(role)
			except:
				print(f"error to remove: {role}, discord:{data} on {guild.name}")
		
		#years sync#
		cursor.execute(f"SELECT discord_id FROM years WHERE guild_id='{guild.id}'")
		data_list = cursor.fetchall()
		for data in data_list:
			try:
				data = data[0]
				role = guild.get_role(data)
				if (role in member.roles):
					await member.remove_roles(role)
			except:
				print(f"error to remove: {role}, discord:{data} on {guild.name}")

@tasks.loop(seconds=2)
async def sync_users():
	cursor.execute(f"SELECT status FROM maintenance WHERE part='sync_task'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		return

	cursor.execute(f"SELECT discord_id, intra_id FROM users")
	users = cursor.fetchall()
	for user in users:
		try:
			login = user[1]
			id = int(user[0])
			await update(login, id)
			await asyncio.sleep(7)
		except:
			pass

		cursor.execute(f"SELECT status FROM maintenance WHERE part='sync_task'")
		maintenance = cursor.fetchone()[0]
		if maintenance == "on":
			return

@tasks.loop(seconds=1)
async def sync_new_users():
	cursor.execute(f"SELECT status FROM maintenance WHERE part='sync_task'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		return

	db.commit()
	cursor.execute(f"SELECT discord_id, intra_id FROM new_users")
	users = cursor.fetchall()
	for new in users:
		id = new[0]
		login = new[1]
		cursor.execute(f"DELETE FROM users WHERE discord_id={id}")
		db.commit()
		cursor.execute(f"SELECT discord_id FROM users WHERE intra_id='{login}'")
		dobble_login = cursor.fetchall()
		for dobble in dobble_login:
			if dobble[0] != id:
				await disconnect(dobble[0])
		cursor.execute(f"DELETE FROM users WHERE intra_id='{login}'")
		cursor.execute(f"DELETE FROM new_users WHERE discord_id={id} and intra_id='{login}'")
		db.commit()
		await update(login, id)
		cursor.execute(f"INSERT INTO users (discord_id, intra_id) VALUES ({id},'{login}')")
		db.commit()
		await asyncio.sleep(2)

##################################################setup discord and call token##################################################################

@tasks.loop(seconds=15)
async def presence():
	cursor.execute(f"SELECT status FROM maintenance WHERE part='status'")
	maintenance = cursor.fetchone()[0]
	if maintenance == "on":
		game = Game(name="🚧 maintenance 🚧")
		await client.change_presence(status=Status.do_not_disturb, activity=game)
		return
	cursor.execute(f"SELECT name FROM status")
	status_list = cursor.fetchall()
	if not status_list:
		game = Game(name="Someone else broke it")
		await client.change_presence(status=Status.idle, activity=game)
		return
	for status in status_list:
		cursor.execute(f"SELECT status FROM maintenance WHERE part='status'")
		maintenance = cursor.fetchone()[0]
		if maintenance == "on":
			game = Game(name="🚧 maintenance 🚧")
			await client.change_presence(status=Status.do_not_disturb, activity=game)
			return
		game = Game(name=status[0])
		await client.change_presence(status=Status.online, activity=game)
		await asyncio.sleep(15)

@client.event
async def on_ready():
	await tree.sync()
	presence.start()
	sync_users.start()
	sync_new_users.start()

client.run(os.getenv('BOT_TOKEN'))
