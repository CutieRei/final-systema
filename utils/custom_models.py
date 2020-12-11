import discord
from typing import Union
from discord.ext import commands
import asyncpg
import datetime
import asyncio
import aiohttp
from concurrent import futures
import os
import cachetools

def mentions(bot):
	return [f'<@{bot.user.id}> ',f'<@!{bot.user.id}> ']

class SysContext(commands.Context):
	pass

class Systema(commands.Bot):
	def __init__(self,*args,**kwargs):
		self.cache = cachetools.LRUCache(69420)
		self.thread_pool = futures.ThreadPoolExecutor()
		activity = discord.Activity(name='@ for prefix',type=discord.ActivityType.listening)
		loop = asyncio.get_event_loop()
		self.db = loop.run_until_complete(asyncpg.create_pool(os.getenv("PSQL_URI")))
		self.prefixes = {str(i['id']):i['prefix'] for i in loop.run_until_complete(self.db.fetch("SELECT * FROM prefixes"))}
		super().__init__(intents=discord.Intents.all(),activity=activity,*args,**kwargs)

	def __repr__(self):
		return f'<{self.__class__.__name__} guilds={len(self.guilds)} users={len(self.users)} messages={len(self.cached_messages)} cache_obj={self.cache}>'

	async def close(self):
		if hasattr(self,"session"):
		    await self.session.close()
		await self.db.close()
		print("[Database] Disconnected")
		self.thread_pool.shutdown()
		await super().close()

	async def on_message(self,msg):
		if msg.author.bot or msg.author == self.user:
			return
		if msg.content in [i.strip(' ') for i in mentions(self)]:
			await msg.channel.send(f'Hello my prefix is `{(await self.get_prefix(msg))[-1]}`')
		await self.process_commands(msg)

	async def on_ready(self):
		if not hasattr(self,"session"):
		    self.session = aiohttp.ClientSession()
		print(f'[Bot] Logged in as {self.user}')

	async def on_disconnect(self):
		print('[Bot] Disconnected')

	async def get_context(self,msg,*,cls=SysContext):
		return await super().get_context(msg,cls=SysContext)

class GuildAlreadyExists(Exception):
	pass

class GuildConfig:
	def __init__(self,payload:Union[tuple,list],bot):
		self.id = payload[0]
		self.mute_role_id = payload[1]
		self._pool = bot.db

	__tablename__ = 'guildconfig'

	@classmethod
	async def get_guild(cls,guild:Union[discord.Guild,int],bot):
		guild_id = guild
		if not isinstance(guild_id,int):
			guild_id = guild_id.id
		async with bot.db.acquire() as conn:
			data = await conn.fetchrow(f'SELECT * FROM {cls.__tablename__} WHERE id = $1',guild_id)
			if data is None:
				return None
			return cls(data,bot)

	@classmethod
	async def new_guild(cls,guild:Union[discord.Guild,int],bot):
		guild_id = guild
		if not isinstance(guild_id,int):
			guild_id = guild_id.id
		async with bot.db.acquire() as conn:
			data = await conn.fetchrow(f'SELECT * FROM {cls.__tablename__} WHERE id = $1',guild_id)
			if data:
				raise GuildAlreadyExists(f"Guild with the id of {guild_id} already exist")
			await conn.execute(f"INSERT INTO {cls.__tablename__} VALUES ($1,$2)",guild_id,None)
			return cls((guild_id,None),bot)

	async def set_mute_role(self,role:Union[discord.Role,int]):
		role_id = role
		if not isinstance(role_id,int):
			role_id = role_id.id
		async with self._pool.acquire() as conn:
			await conn.execute(f'UPDATE {self.__tablename__} SET mute_role = $1 WHERE id = $2',role_id,self.id)
			self.mute_role_id = role_id

class GuildPrefix:
	def __init__(self,bot,payload:Union[tuple,list]):
		self.id = payload[0]
		self.prefix = payload[1]
		self._pool = bot.db

	__tablename__ = 'prefixes'

	@classmethod
	async def get_guild(cls,guild:Union[discord.Guild,int],bot):
		guild_id = guild
		if not isinstance(guild_id,int):
			guild_id = guild_id.id
		async with bot.db.acquire() as conn:
			data = await conn.fetchrow(f'SELECT * FROM {cls.__tablename__} WHERE id = $1',guild_id)
			if data is None:
				return None
			return cls(bot,data)

	@classmethod
	async def new_guild(cls,guild:Union[discord.Guild,int],bot,prefix='s.'):
		guild_id = guild
		if not isinstance(guild_id,int):
			guild_id = guild_id.id
		async with bot.db.acquire() as conn:
			data = await conn.fetchrow(f'SELECT * FROM {cls.__tablename__} WHERE id = $1',guild_id)
			if data:
				raise GuildAlreadyExists(f"Guild with the id of {guild_id} already exist")
			await conn.execute(f"INSERT INTO {cls.__tablename__} VALUES ($1,$2)",guild_id,prefix)
			bot.prefixes[str(guild_id)] = prefix
			return cls(bot,(guild_id,prefix))

	async def change_prefix(self,new):
		async with self._pool.acquire() as conn:
			await conn.execute(f"UPDATE {self.__tablename__} SET prefix = $1 WHERE id = $2",new,self.id)
			self.prefix = new 