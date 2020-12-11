import discord
import random
from discord.ext import commands
import asyncio

class Economy(commands.Cog):
    
    def __init__(self,bot):
        self.bot = bot
        bot.loop.create_task(self.fetch_users(save=True))
        self._multiplier = 1
        self._min_max = [10,20]
        self.levels = {}
    
    async def bot_check(self,ctx):
        if str(ctx.author.id) not in self.levels:
            self.levels[str(ctx.author.id)] = [0,1]
        if not str(ctx.author.id) in self.users:
            await self.bot.db.execute("INSERT INTO economy_balance VALUES ($1,$2)",ctx.author.id,0)
            self.users[str(ctx.author.id)] = 0
        return True

    def cog_check(self,ctx):
        if ctx.author.id in []:
            return False
        return True

    async def fetch_users(self,*,save=True):
        users = await self.bot.db.fetch("SELECT * FROM economy_balance")
        users = {str(i["id"]):i["money"] for i in users}
        if save:
            self.users = users
        return users

    @commands.command()
    async def balance(self,ctx,user:discord.User=None):
        if user is None:
            user = ctx.author
        try:
            self.users[str(user.id)]
            not_registered = False
        except:
            not_registered = True
        balance = 0 if not_registered else self.users[str(user.id)]
        embed = discord.Embed(title=f"{user} balance", description=f"**Money**\n<:system_chip:786377572161159209> {balance}\n**Level progress**\n"+("<:bar_empty:786734023992803329>"*10).replace("<:bar_empty:786734023992803329>","<:bar_full:786734102375563325>",int(self.levels[str(user.id)][0]))+"\nlevel: **{}**".format(self.levels[str(user.id)][1]))
        if not_registered:
            embed.set_footer(text="user is not registered, this is a temporary display")
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1,6000,commands.BucketType.user)
    async def work(self,ctx):
        money = random.randint(*self._min_max)*self._multiplier
        author_id = str(ctx.author.id)
        try:
            self.levels[author_id]
        except KeyError:
            self.levels[author_id] = [0,1]
        exp = random.randint(0,5)*(0.5+(self.levels[author_id][1]/2))
        self.levels[author_id][0] += exp
        level_reset = False
        if self.levels[author_id][0] > (10):
            current_exp = self.levels[author_id][0]
            self.levels[author_id][1] += 1
            self.levels[author_id][0] = current_exp-10
            level_reset = True
        self.users[author_id] += money
        await self.bot.db.execute("UPDATE economy_balance SET money = money + $1 WHERE id = $2", money, ctx.author.id)
        await ctx.send(f"you worked and got <:system_chip:786377572161159209>**{money}** and <:bar_full:786734102375563325>**x{exp}**"+ (" and new level!" if level_reset else ""))
    
    @work.error
    async def on_work_error(self,ctx,err):
        return

def setup(bot):
    bot.add_cog(Economy(bot))
    print("[Economy] Loaded module")