import discord
from discord.ext import commands
from discord.ext import tasks
from helpers import human_format, get_7d_floating_supply, get_current_day_lb, get_7d_lb_sma, get_7d_token_values, get_7d_lb_sma_raw
import constants
import traceback

class OhmLiquidBackingDiscordBot:
    def __init__(self, commandprefix, adminrole, updateinterval):
        self.adminrole = adminrole
        self.updateinterval = updateinterval
        self.bot = commands.Bot(command_prefix=commandprefix)

        self.bot.event(self.on_ready)
        self.update_lb = tasks.loop(minutes=self.updateinterval)(self._update_lb)
        self.bot.add_command(commands.Command(name='fixpresence', func=self._fixpresence, pass_context=True))
        self.bot.add_command(commands.Command(name='forceupdate', func=self._forceupdate, pass_context=True))
        self.bot.add_command(commands.Command(name='getrawfloating', func=self._getrawfloating, pass_context=True))
        self.bot.add_command(commands.Command(name='ping', func=self._ping, pass_context=True))
        self.bot.add_command(commands.Command(name='getrawtokens', func=self._getrawtokens, pass_context=True))
        self.bot.add_command(commands.Command(name='getrunninglb', func=self._getrunninglb, pass_context=True))

    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name}")
        print("------")
        if self.update_lb.is_running():
            print("Task Already Running on_ready")
        else:
            self.update_lb.start()

    async def _forceupdate(self, ctx):
        try:
            if not await self.role_check(ctx.author.roles):
                await ctx.send("You don't have permission to use this command.")
                return
            await ctx.send("Yes ser, on it boss.")
            newName = await self.get_ohm_lb()
            for guild in self.bot.guilds:
                await guild.me.edit(nick=newName)
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"OHM LB 7D SMA"))
            await ctx.send("Happy to report it has been updated!")
        except:
            await ctx.send("Exception Raised, check https://status.thegraph.com/ for any outages")
            traceback.print_exc()

    async def _fixpresence(self, ctx):
        if not await self.role_check(ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        for guild in self.bot.guilds:
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM LB 7D SMA"))
        await ctx.send("Yes ser, on it boss.")

    async def role_check(self, user_roles):
        for role in user_roles:
            if role.name == self.adminrole:
                return True
        return False
    
    async def _getrawfloating(self, ctx):
        try:
            await ctx.send("Yes ser, on it boss.")
            data = get_7d_floating_supply()
            embed = discord.Embed(title="7 Day Floating Supply", color=discord.Color.blue())
            for k, v in data.items():
                embed.add_field(name=k, value="{:,}".format(v), inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Exception Raised, check https://status.thegraph.com/ for any outages")
            traceback.print_exc()

    async def _ping(self, ctx):
        try:
            lb_today = get_current_day_lb()
            _, removed, upper, lower = get_7d_lb_sma()
            embed = discord.Embed(title="Pong", color=discord.Color.blue())
            embed.add_field(name="Current LB", value=f"${lb_today:,.2f}", inline=False)
            embed.add_field(name="Upper Bound", value=f"${upper:,.2f}", inline=False)
            embed.add_field(name="Lower Bound", value=f"${lower:,.2f}", inline=False)
            if removed:
                excluded_values = "\n".join([f"{k}: ${v:,.2f}" for k, v in removed])
                embed.add_field(name="Excluded Value(s)", value=excluded_values, inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Exception Raised, check https://status.thegraph.com/ for any outages")
            traceback.print_exc()

    async def _getrawtokens(self, ctx):
        try:
            await ctx.send("Yes ser, on it boss.")
            data = get_7d_token_values()
            embed = discord.Embed(title="7 Day Token Values", color=discord.Color.blue())
            for k, v in data.items():
                embed.add_field(name=k, value=f"${v:,.2f}", inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Exception Raised, check https://status.thegraph.com/ for any outages")
            traceback.print_exc()

    async def _getrunninglb(self, ctx):
        try:
            await ctx.send("Yes ser, on it boss.")
            data = get_7d_lb_sma_raw()
            embed = discord.Embed(title="7 Day Liquid Backing", color=discord.Color.blue())
            for k, v in data.items():
                embed.add_field(name=k, value=f"${v:,.2f}", inline=False)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Exception Raised, check https://status.thegraph.com/ for any outages")
            traceback.print_exc()

    async def _update_lb(self):
        try:
            newName = await self.get_ohm_lb()
            print(f"Updating lb sma bot nickname to: {newName}")
            ## dynamic updates
            for guild in self.bot.guilds:
                await guild.me.edit(nick=newName)
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"OHM LB 7D SMA"))
        except:
            traceback.print_exc()
            for guild in self.bot.guilds:
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"OHM LB 7D SMA"))
                
    async def get_ohm_lb(self):
        try:
            lb_val, removed, _, _ = get_7d_lb_sma()

            if removed:
                channel = self.bot.get_channel(constants.LOG_CHANNEL)
                removed_string = "|".join([f"{k}: ${v:,.2f}" for k, v in removed])
                await channel.send(
                    f"<@&924860610775253043> Detected anomalous price in 7-day liquid backing, please check ohmliq!getrunninglb, ohmliq!getrawtokens, ohmliq!getrawfloating to determine outlier. Removed price(s):, {removed_string}")
        
            return human_format(lb_val)
        except:
            traceback.print_exc()