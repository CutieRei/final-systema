import discord
import dotenv
import os
from discord.ext import commands

dotenv.load_dotenv()
import utils

bot = utils.custom_models.Systema(command_prefix=utils.checks.get_prefix,owner_ids=tuple(int(i) for i in os.getenv("OWNER_IDS").split(";")),embed_color=discord.Color.from_rgb(75, 147, 213))
bot.load_extension("jishaku")
if os.name == 'nt':
	os.system('cls')
else:
	os.system("clear")

extensions = ['moderation','economy']

for ext in extensions:
	bot.load_extension("ext."+ext)

bot.run(os.getenv('TOKEN'))