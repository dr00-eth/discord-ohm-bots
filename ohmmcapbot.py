import discord
from discord.ext import commands
from discord.ext import tasks
from helpers import human_format, get_price_ohm, get_circulating_supply
import traceback

class OhmMarketCapDiscordBot:
    def __init__(self, commandprefix, adminrole, updateinterval):
        self.adminrole = adminrole
        self.updateinterval = updateinterval
        self.bot = commands.Bot(command_prefix=commandprefix)
        self.lastval = ''

        self.bot.event(self.on_ready)
        self.update_mcap = tasks.loop(minutes=self.updateinterval)(self._update_mcap)
        self.bot.add_command(commands.Command(name='fixpresence', func=self._fixpresence, pass_context=True))
        self.bot.add_command(commands.Command(name='forceupdate', func=self._forceupdate, pass_context=True))

    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name}")
        print("------")
        if self.update_mcap.is_running():
            print("Task Already Running on_ready")
        else:
            self.update_mcap.start()

    async def _forceupdate(self, ctx):
        if not await self.role_check(ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        await ctx.send("Yes ser, on it boss.")
        newName = await self.get_ohm_mcap()
        for guild in self.bot.guilds:
            await guild.me.edit(nick=newName)
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM MCAP"))
        await ctx.send("Happy to report it has been updated!")

    async def _fixpresence(self, ctx):
        if not await self.role_check(ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        for guild in self.bot.guilds:
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM MCAP"))
        await ctx.send("Yes ser, on it boss.")

    async def role_check(self, user_roles):
        for role in user_roles:
            if role.name == self.adminrole:
                return True
        return False
    
    async def _update_mcap(self):
        try:
            newName = await self.get_ohm_mcap()
            print(f"Updating nickname to: {newName}")
            ## dynamic updates
            for guild in self.bot.guilds:
                await guild.me.edit(nick=newName)
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"OHM MCAP"))
        except:
            print("likely discord rate limit")
    
    async def get_ohm_mcap(self):
        try:
            price = get_price_ohm()
            circ_supply = get_circulating_supply()
            mcap = price * circ_supply
            name_val = human_format(float(mcap))
            self.lastval = name_val
            return name_val
        except:
            traceback.print_exc()
            print("subgraph exception")
            return self.lastval