import discord
from discord.ext import commands
from utils import custom_models
import datetime
import asyncio

class Moderation(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    async def cog_check(self,ctx):
        return ctx.guild is not None

    async def _setup_mute(self,ctx,role,who,delay):
        try:
            await who.add_roles(role)
            await who.send(f"You have been muted in **{ctx.guild}** for `{delay} seconds`")
            await asyncio.sleep(delay)
            try:
                if not role in who.roles:
                    return
                await who.remove_roles(role)
                await who.send("you have been unmuted in **{ctx.guild}**")
            except:
                return
        except:
            return

    @commands.command()
    @commands.is_owner()
    async def mute(self,ctx,who:discord.Member, duration:int=5):
        role = ctx.guild.get_role((await custom_models.GuildConfig.get_guild(ctx.guild,self.bot)).mute_role_id)
        if role is None:
            await ctx.send("mute role is not set")
            return
        self.bot.loop.create_task(self._setup_mute(ctx, role, who, duration))
        await ctx.send(f"muted **{who}** for `{duration} seconds`")

    @commands.group(name='config',invoke_without_commands=True)
    @commands.has_permissions(kick_members=True)
    async def _config(self,ctx):
        """
        Base config command for current server
        """
        return

    @_config.command(name='muterole',usage='[new role]')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def _config_muterole(self,ctx,role:discord.Role=None):
        """
        Set new mute role or show mute role if a role argument is not passed
        """
        guild = await custom_models.GuildConfig.get_guild(ctx.guild,self.bot)
        if guild is None:
            guild = await custom_models.GuildConfig.new_guild(ctx.guild,self.bot)
        if role is not None:
            await guild.set_mute_role(role)
            await ctx.send(f"**{role}** is now muted role",allowed_mentions=discord.AllowedMentions.none())
            return
        muted_role = ctx.guild.get_role(guild.mute_role_id)
        if muted_role is not None:
            muted_role = muted_role.mention
        embed = discord.Embed(title='Muterole',description=f'Current server mute role is {muted_role or "NaN"}',timestamp=datetime.datetime.utcnow())
        await ctx.send(embed=embed)

    @_config.command(name='prefix',usage='<new prefix>')
    async def _config_prefix(self,ctx,new):
        """
        Set new prefix for current server
        """
        if len(new) > 5:
            await ctx.send("Prefix cannot be more than 5 characters")
            return
        if new.strip() == '':
            await ctx.send("Prefix cannot be empty")
        prefix = self.bot.prefixes[str(ctx.guild.id)]
        if new == prefix:
            await ctx.send("New prefix cannot be the same as the old one")
            return
        guild = await custom_models.GuildPrefix.get_guild(ctx.guild,self.bot)
        await guild.change_prefix(new)
        await ctx.send(f"Changed prefix from `{prefix}` to `{new}`")
        self.bot.prefixes[str(ctx.guild.id)] = new

    @commands.command(name='kick',usage='<member> [reason]')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def _kick(self,ctx,member:discord.Member,*,reason=None):
        if member == ctx.author:
            await ctx.send("You can't kick yourself")
            return
        if member == ctx.guild.me:
            await ctx.send("That's not possible")
            return
        if member.top_role > ctx.author.top_role:
            await ctx.send("It seems like that member has higher role than you")
            return
        if member.top_role > ctx.guild.me.top_role:
            await ctx.send("I can't kick that member, they have higher role than me")
            return
        if reason is None:
            reason = f'{member} kicked by {ctx.author}'
        await member.kick(reason=reason)
        await ctx.send(f'Kicked **{member}**')

    @commands.command(name='ban',usage='<member> [delete message days] [reason]')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def _ban(self,ctx,member:discord.Member,msg:int=0,*,reason=None):
        if member == ctx.author:
            await ctx.send("You can't ban yourself")
            return
        if member == ctx.guild.me:
            await ctx.send("That's not possible")
            return
        if member.top_role > ctx.author.top_role:
            await ctx.send("It seems like that member has higher role than you")
            return
        if member.top_role > ctx.guild.me.top_role:
            await ctx.send("I can't ban that member, they have higher role than me")
            return
        if reason is None:
            reason = f'{member} banned by {ctx.author}'
        await member.ban(reason=reason,delete_message_days=msg)
        await ctx.send(f"Banned **{member}**")

    @commands.command(name='softban',usage='<member>  [delete message days] [reason]')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def _softban(self,ctx,member:discord.Member,msg:int=7,*,reason=None):
        if member == ctx.author:
            await ctx.send("You can't ban yourself")
            return
        if member == ctx.guild.me:
            await ctx.send("That's not possible")
            return
        if member.top_role > ctx.author.top_role:
            await ctx.send("It seems like that member has higher role than you")
            return
        if member.top_role > ctx.guild.me.top_role:
            await ctx.send("I can't ban that member, they have higher role than me")
            return
        if reason is None:
            reason = f'{member} softbanned by {ctx.author}'
        await member.ban(reason=reason,delete_message_days=msg)
        await ctx.send(f"Successfully softbanned **{member}**")
        await ctx.guild.unban(discord.Object(id=member.id))

    @commands.command(name='unban',usage='<user id> [reason]')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def _unban(self,ctx,member:int,*,reason=None):
        if reason is None:
            reason = 'No reason provided'
        try:
            await ctx.guild.unban(discord.Object(id=member))
            await ctx.send(f"Unbanned **{member}**")
        except discord.HTTPException:
            await ctx.send('Something went wrong while unbanning member')

def setup(bot):
    bot.add_cog(Moderation(bot))
    print('[Moderation] Loaded module')