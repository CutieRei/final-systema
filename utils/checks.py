from .custom_models import GuildPrefix

def mentions(bot):
	return [f'<@{bot.user.id}> ',f'<@!{bot.user.id}> ']

async def get_prefix(bot,msg):
	if msg.guild is None:
		prefix = mentions(bot)
		prefix.append("s.")
		return prefix
	try:
		prefix = mentions(bot)
		prefix.append(bot.prefixes[str(msg.guild.id)])
		return prefix
	except KeyError:
		guild = await GuildPrefix.new_guild(msg.guild,bot)
		prefix = mentions(bot)
		prefix.append(guild.prefix)
		return prefix