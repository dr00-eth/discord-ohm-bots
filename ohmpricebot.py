from pycoingecko import CoinGeckoAPI
import discord
from discord.ext import commands
from discord.ext import tasks
import traceback
from helpers import human_format, get_price_ohm
import json

class OhmPriceDiscordBot:
    def __init__(self, commandprefix, adminrole, updateinterval):
        self.adminrole = adminrole
        self.cg = CoinGeckoAPI()
        self.lastprice = -1
        self.updateinterval = updateinterval
        self.bot = commands.Bot(command_prefix=commandprefix)

        self.bot.event(self.on_ready)
        self.update_ohm_price = tasks.loop(minutes=self.updateinterval)(self._update_ohm_price)
        self.bot.add_command(commands.Command(name='fixpresence', func=self._fixpresence, pass_context=True))
        self.bot.add_command(commands.Command(name='forceupdate', func=self._forceupdate, pass_context=True))

    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name}")
        print("------")
        if self.update_ohm_price.is_running():
            print("Task Already Running on_ready")
        else:
            self.update_ohm_price.start()

    async def _forceupdate(self, ctx):
        await ctx.send("Yes ser, on it boss.")
        newName = await self.get_ohm_price()
        for guild in self.bot.guilds:
            await guild.me.edit(nick=newName)
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM Price"))
        await ctx.send("Happy to report it has been updated!")

    async def _fixpresence(self, ctx):
        if not await self.role_check(ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        for guild in self.bot.guilds:
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM price"))
        await ctx.send("Yes ser, on it boss.")

    async def role_check(self, user_roles):
        for role in user_roles:
            if role.name == self.adminrole:
                return True
        return False

    async def _update_ohm_price(self):
        try:   
            newName = await self.get_ohm_price()
            print(f"Updating nickname to: {newName}")
        
            for guild in self.bot.guilds:
                await guild.me.edit(nick=newName)
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"OHM price"))
        except:
            for guild in self.bot.guilds:
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"OHM price"))
            print("likely discord rate limit")
            traceback.print_exc()

    async def get_ohm_price(self):
        raw_data = self.cg.get_price(ids='olympus', vs_currencies='usd, eth')
        market_data = json.dumps(raw_data)
        json_data = json.loads(market_data)
        usdPrice = get_price_ohm()
        ethPrice = json_data["olympus"]["eth"]
    
        if self.lastprice != -1 and (abs(((usdPrice - self.lastprice) / usdPrice) * 100) > 10):
            print(f"Caught Price Exception, reverting to last price", {usdPrice} | {self.lastprice})
            return "{} | Ξ{}".format(human_format(self.lastprice),"%.3f" % round(ethPrice, 3))
        else:
            #print("else")
            self.lastprice = usdPrice
            name_val = "{} | Ξ{}".format(human_format(usdPrice),"%.3f" % round(ethPrice, 3))
        
        return name_val