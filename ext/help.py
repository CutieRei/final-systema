import discord
from discord.ext import commands
import datetime

class CommandCogConverter(commands.Converter):
	async def convert(self,ctx,arg):
		cogs,commands = ctx.bot.cogs,ctx.bot.commands
		if arg in cogs:
			return cogs[arg]
		return ctx.bot.get_command(arg)

class Help(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	def get_cog_info(self,cog):
		commands = cog.get_commands()
		hidden_command = [i for i in commands if i.hidden]
		disabled_command = [i for i in commands if not i.enabled]
		

	@commands.command(usage='[command|category]')	
	async def help(self,ctx,*,cmd:CommandCogConverter=None):
		if cmd is None:
			embed=

def setup(bot):
	bot.add_cog(Help(bot))
	print("[Help] Loaded module")