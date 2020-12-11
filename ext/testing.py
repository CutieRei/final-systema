import discord
from discord.ext import commands
import typing


class Testing(commands.Cog):
    
    def __init__(self,bot):
        self.bot = bot

    
    @commands.command()
    async def test(self, ctx, arg: typing.Union[int,float]):
       await ctx.send(f"your argument type is **{type(arg).__name__}**")
       

def setup(bot):
    bot.add_cog(Testing(bot))
    print("[Testing] Loaded")
    print("-- Beware that Testing cog is used for testing purposes and cannot be used in production please refrain from doing so --")