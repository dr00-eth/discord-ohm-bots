from pycoingecko import CoinGeckoAPI
import discord
from discord.ext import commands
from discord.ext import tasks
import traceback
from helpers import human_format, get_price_gohm
import json

class GohmPriceDiscordBot:
    def __init__(self, commandprefix, adminrole, updateinterval):
        self.adminrole = adminrole
        self.cg = CoinGeckoAPI()
        self.lastprice = -1
        self.updateinterval = updateinterval
        self.bot = commands.Bot(command_prefix=commandprefix)

        self.bot.event(self.on_ready)
        self.update_gohm_price = tasks.loop(minutes=self.updateinterval)(self._update_gohm_price)
        self.bot.add_command(commands.Command(name='fixpresence', func=self._fixpresence, pass_context=True))

    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name}")
        print("------")
        if self.update_gohm_price.is_running():
            print("Task Already Running on_ready")
        else:
            self.update_gohm_price.start()

    async def _fixpresence(self, ctx):
        if not await self.role_check(ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        for guild in self.bot.guilds:
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"gOHM price"))
        await ctx.send("Yes ser, on it boss.")

    async def role_check(self, user_roles):
        for role in user_roles:
            if role.name == self.adminrole:
                return True
        return False

    async def _update_gohm_price(self):
        try:   
            newName = await self.get_gohm_price()
            print(f"Updating nickname to: {newName}")
            ## dynamic updates
        
            for guild in self.bot.guilds:
                await guild.me.edit(nick=newName)
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"gOHM price"))
        except:
            for guild in self.bot.guilds:
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"gOHM price"))
            print("likely discord rate limit")
            traceback.print_exc()

    async def get_gohm_price(self):

        raw_data = self.cg.get_price(ids='governance-ohm', vs_currencies='usd, eth')
        market_data = json.dumps(raw_data)
        json_data = json.loads(market_data)
        
        usdPrice = get_price_gohm() #fetches from latest subgraph block
        ethPrice = json_data["governance-ohm"]["eth"] #fetches from CG, not available in subgraph

        if self.lastprice != -1 and (abs(((usdPrice - self.lastprice) / usdPrice) * 100) > 10):
            print(f"Caught Price Exception, reverting to last price", {usdPrice} | {self.lastprice})
            return "{} | Ξ{}".format(human_format(self.lastprice),"%.2f" % round(ethPrice, 2))
        else:
            #print("else")
            self.lastprice = usdPrice
            name_val = "{} | Ξ{}".format(human_format(usdPrice),"%.2f" % round(ethPrice, 2))
        
        return name_val