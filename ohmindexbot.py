import discord
from discord.ext import commands
from discord.ext import tasks
from helpers import get_raw_index

class OhmIndexDiscordBot:
    def __init__(self, commandprefix, adminrole, updateinterval):
        self.adminrole = adminrole
        self.updateinterval = updateinterval
        self.bot = commands.Bot(command_prefix=commandprefix)

        self.bot.event(self.on_ready)
        self.update_index = tasks.loop(minutes=self.updateinterval)(self._update_index)
        self.bot.add_command(commands.Command(name='fixpresence', func=self._fixpresence, pass_context=True))
        self.bot.add_command(commands.Command(name='forceupdate', func=self._forceupdate, pass_context=True))

    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name}")
        print("------")
        if self.update_index.is_running():
            print("Task Already Running on_ready")
        else:
            self.update_index.start()

    async def _forceupdate(self, ctx):
        await ctx.send("Yes ser, on it boss.")
        newName = await self.get_ohm_index()
        for guild in self.bot.guilds:
            await guild.me.edit(nick=newName)
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM Index"))
        await ctx.send("Happy to report it has been updated!")

    async def _fixpresence(self, ctx):
        if not await self.role_check(ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        for guild in self.bot.guilds:
            await self.bot.change_presence(activity=discord.Activity(
                type=discord.ActivityType.watching, name=f"OHM Index"))
        await ctx.send("Yes ser, on it boss.")

    async def role_check(self, user_roles):
        for role in user_roles:
            if role.name == self.adminrole:
                return True
        return False

    async def _update_index(self):
        try:
            newName = await self.get_ohm_index()
            print(f"Updating index bot nickname to: {newName}")
            ## dynamic updates
            for guild in self.bot.guilds:
                await guild.me.edit(nick=newName)
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"OHM Index"))
        except:
            for guild in self.bot.guilds:
                await self.bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.watching, name=f"OHM Index"))

    async def get_ohm_index(self):
        rawindex = get_raw_index()
        
        name_val = round(float(rawindex),4)
    
        return str(name_val)