import discord
from discord.ext import commands
import asyncio
import time
import constants
from helpers import get_image_data

class SentinelDiscordBot:
    def __init__(self, commandprefix, adminrole, optionalrole = None):
        self.adminrole = adminrole
        self.optionalrole = optionalrole
        self.streak_threshold = 3
        self.streak_message = None
        self.streak_count = 0
        self.streak_users = []
        self.sequence_position = 0
        self.intents = discord.Intents.default()
        self.intents.members = True
        self.intents.presences = True
        self.bot = commands.Bot(command_prefix=commandprefix, intents=self.intents)

        self.bot.event(self.on_ready)
        self.bot.event(self.on_member_update)
        self.bot.event(self.on_member_join)
        self.bot.event(self.on_message)
        self.bot.add_command(commands.Command(name='masskick', func=self._masskick, pass_context=True))
        self.bot.add_command(commands.Command(name='listzero', func=self._listzero, pass_context=True))
        self.bot.add_command(commands.Command(name='bulkrole', func=self._bulkrole, pass_context=True))
        self.bot.add_command(commands.Command(name='sususers', func=self._sususers, pass_context=True))

    async def role_check(self, user_roles, allow_optional = False):
        for role in user_roles:
            if self.optionalrole and allow_optional:
                if role.name == self.optionalrole:
                    return True
            if role.name == self.adminrole:
                return True
        return False
    
    async def on_ready(self):
        print(f"Logged in as {self.bot.user.name}")
        print("------")

    async def on_member_join(self, member):
        await asyncio.sleep(360)
        
        guild = self.bot.get_guild(member.guild.id)
        e_role = discord.utils.get(guild.roles, name="@everyone")
        #use fetch_member because get_member pulls from cache
        try:
            member_check = await guild.fetch_member(member.id)
        except:
            member_check = None
            print(f"Couldn't locate member {member.id} | {member.name}")
        if member_check:
            if (len(member_check.roles) == 1 and e_role in member_check.roles):
                print(f"Kicking, {member_check.name} | {member_check.id}")
                print("------")
                channel = self.bot.get_channel(constants.LOG_CHANNEL)
                await channel.send(
                    f"Notified and kicked user that verified and selected no roles, {member_check.name}|{member_check.id}")
                try:
                    await member_check.send(
                f"You have been kicked from {guild.name} because you did not assign roles within 6 minutes of joining the server, please rejoin and select roles to avoid being kicked.")
                except:
                    pass
        
                await guild.kick(member_check)

    async def on_member_update(self, before, after):
        guild = self.bot.get_guild(before.guild.id)
        
        g_role = discord.utils.get(guild.roles, name=constants.GRASSHOPPER) # role object for grasshoppers
        
        if (g_role not in before.roles and g_role in after.roles):
            print(f"detected new grasshopper, {after.name}|{after.id}") #CONSOLE LOGGING
            #LOGGING OUTPUT
            channel = self.bot.get_channel(constants.LOG_CHANNEL)
            await channel.send(
                f"Notifying new grasshopper to disable DMs, {after.name} | {after.id}")
            #NOTIFY USER VIA DM      
            try:
                await after.send(
                "**WARNING:**\n\nYou recently opened Direct Messages from server members and are vulnerable to DM scams until you disable direct messages from server members.\n\nThis is the most common attack vector and is easily mitigated. \n\nPlease go to the server settings and uncheck **Allow direct messages from server members**. Stay safe!")
            except:
                print(f"Could not DM: {after.name} | {after.id}")
                await asyncio.sleep(30)
            #WELCOME USER IN GENERAL
            genChannel = self.bot.get_channel(constants.GENERAL_CHANNEL)
            await genChannel.send(
                f"Welcome young grasshopper <@{after.id}>, it's great to have you here.\n\nTell us a little about yourself and what brings you to Olympus!", delete_after=constants.EXPIRATION)
            await asyncio.sleep(90)
            #INTRODUCE USER IN LEARN
            learn = self.bot.get_channel(constants.LEARN_CHANNEL)
            await learn.send(
                f"Once you've had a chance to introduce yourself in <#{constants.GENERAL_CHANNEL}>, <@{after.id}>, be sure to check out this channel and ask any of those burning questions you might have!\n\nAlso check out the top of the channels list to RSVP for any of this week's events.", delete_after=constants.EXPIRATION)
            #await asyncio.sleep(90)
            #INTRODUCE USER IN OT
            #ot = bot.get_channel(OT_CHANNEL)
            #await ot.send(
            #    f"Looking to blow off some steam or connect with other Ohmies <@{after.id}>? <#{OT_CHANNEL}> is not for the faint of heart, do you have what it takes?", delete_after=EXPIRATION)
            await asyncio.sleep(90)
            await genChannel.send(f"<@{after.id}>, Do you hold sOHM or gOHM? Check out <#981648330822152333> to verify your assets to gain the exclusive `Ohmies (Verified)` role!", delete_after=constants.EXPIRATION)


    async def _masskick(self, ctx, role: discord.Role):
        if not await self.role_check(ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        total = len(role.members)
        kicked = 0

        await ctx.message.add_reaction('🧠')  # lets user know command is processing

        print(f"queued for kick: {total}")  #console
        for member in role.members:
            await ctx.guild.kick(member)
            await ctx.channel.send(
                f"[{kicked}/{total}] kicked: {member.name} | <@{member.id}>"
            )  # discord
            print(
                f"[{kicked}/{len(role.members)}] kicked: {member.name} | <@{member.id}>"
            )  # console
            kicked += 1  #increment
            await asyncio.sleep(1)  # sleep call between interactions to avoid 429 rate limit

        await ctx.message.clear_reaction('🧠')  # remove processing reaction
        await ctx.message.add_reaction('✅')  # add finished reaction
        time.sleep(1)
        await ctx.message.reply(f"kicked {total} users in given role.")  # let user know

    async def _listzero(self, ctx, role: discord.Role):
        if not await self.role_check(ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        members = filter(lambda m: len(m.roles) == 1, role.members)
        try:
            await ctx.send(" ".join(str(member.id) for member in members))
        except:
            await ctx.send("No members found")

    async def _bulkrole(self, ctx, role: discord.Role, *users):
        if not await self.role_check(ctx.author.roles):
            await ctx.send("You don't have permission to use this command.")
            return
        guild = self.bot.get_guild(ctx.guild.id)
        count = 0
        await ctx.message.add_reaction('🧠')  # lets user know command is processing
        for user in users:
            try:
                member = await guild.fetch_member(user)
                await member.add_roles(role)
                count += 1
            except:
                pass
                await asyncio.sleep(1)

        await ctx.message.add_reaction('✅')  # add finished reaction
    
        await ctx.send("Added {} to {} users".format(role,count))

    async def _sususers(self, ctx):
        if not await self.role_check(ctx.author.roles, True):
            await ctx.send("You don't have permission to use this command.")
            return

        await ctx.message.add_reaction('🧠')  # lets user know command is processing

        for guild in self.bot.guilds:
            found_members = []
            for member in guild.members:
                if member.id in constants.EXCLUDE_IDS or member.id in constants.EXCLUDE_COMM_IDS:
                    continue
                for keyword in constants.SCAMMER_KEYWORDS:
                    if keyword in member.name or (member.nick and keyword in member.nick):
                        print(f'Found member {member.name} ({member.id}) with keyword {keyword}')
                        found_members.append(member)
            if not found_members:
                keywords = "\n".join(constants.SCAMMER_KEYWORDS)
                response = f'No members found with keywords: {keywords}'
            else:
                response = 'Found members:\n'
                for member in found_members:
                    response += f'{member} (ID: {member.id})\n'
            
            await ctx.send(response)


    async def add_reactions(self, message, count=None):
        try:
            if count is None:
                # If the count is equal to the threshold, add a green checkmark emoji
                if self.streak_count == self.streak_threshold:
                    await message.add_reaction(u"\u2705")  # Green checkmark emoji
                # If the count is less than or equal to 9, add the corresponding number emoji
                elif self.streak_count <= 9:
                    await message.add_reaction(str(self.streak_count) + u"\u20e3")
                # If the count is 33, add the custom :33: reaction
                elif self.streak_count == 33:
                    await message.add_reaction(":33:")
                # If the count is greater than 9, add the tens and ones digit emojis
                else:
                    tens_digit = self.streak_count // 10
                    ones_digit = self.streak_count % 10
                    await message.add_reaction(str(tens_digit) + u"\u20e3")
                    await message.add_reaction(str(ones_digit) + u"\u20e3")
            else:
                # If the count is less than or equal to 9, add the corresponding number emoji
                if count <= 9:
                    await message.add_reaction(str(count) + u"\u20e3")
                # If the count is 33, add the custom :33: reaction
                elif count == 33:
                    await message.add_reaction(":33:")
                # If the count is greater than 9, add the tens and ones digit emojis
                else:
                    tens_digit = count // 10
                    ones_digit = count % 10
                    await message.add_reaction(str(tens_digit) + u"\u20e3")
                    await message.add_reaction(str(ones_digit) + u"\u20e3")
        except Exception as e:
            print(f"Error adding reactions: {e}")


    # Define a function to reset the streak variables
    def reset_streak(self):
        self.streak_message = None
        self.streak_count = 0
        self.streak_users = []
        self.sequence_position = 0

    async def on_message(self, message):

        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return
        
        if message.content.lower().startswith('oly!'):
            await self.bot.process_commands(message)

        # Check if the message was sent in the desired channel
        desired_channel_id = 798371943324844042  # Replace with the ID of the desired channel
        if message.channel.id != desired_channel_id:
            return

        # Check for Captain Planet streak message sequence
        if self.sequence_position < len(constants.STREAK_MESSAGE_SEQUENCE) and message.content.lower() == constants.STREAK_MESSAGE_SEQUENCE[self.sequence_position]:
            print(f'{message.author} said {constants.STREAK_MESSAGE_SEQUENCE[self.sequence_position]}')
            self.sequence_position += 1
            self.streak_users.append(message.author)
            self.streak_count += 1
            if self.sequence_position == len(constants.STREAK_MESSAGE_SEQUENCE):
                print('Captain Planet Summoned')
                self.reset_streak()
                captain_planet_url = "https://media.tenor.com/WrD2KCj7EEIAAAAC/captain-planet.gif"
                image_data = get_image_data(captain_planet_url)
                caption = "By your powers combined... I AM CAPTAIN PLANET!"
                await message.channel.send(content=caption, file=discord.File(image_data, "captain_planet.gif"))

            return

        # If there is no current streak message, set the message and return
        if self.streak_message is None:
            self.streak_message = message.content
            self.streak_users = [(message.author, 1)]
            self.streak_count = 1
            return

        # If the message matches the streak message
        if message.content.lower() == self.streak_message.lower():

            # If the streak was broken, end the game
            if self.streak_count >= self.streak_threshold and message.author == self.streak_users[-1][0]:
                await message.channel.send(f'{message.author.mention} failed, can\'t pasta twice bruv, better luck next time!')
                self.reset_streak()
                print(f"Streak ended: {self.streak_message}, {self.streak_count}, {self.streak_users}")
                return

            # Add the user to the set of streak participants
            self.streak_users.append((message.author, self.streak_count))

            # Increment the streak count
            self.streak_count += 1

            # If the streak threshold has been reached, announce the start of the contest and add reactions
            if self.streak_count == self.streak_threshold:
                await message.channel.send(f'PASTA ALERT! **{self.streak_message}** has been pasta\'d {self.streak_threshold} times, how long can we keep it going?')
                await self.add_reactions(message)

            # If the streak count is above the threshold, add reactions for the current streak count
            elif self.streak_count > self.streak_threshold:
                await self.add_reactions(message, self.streak_count - self.streak_threshold)
        elif self.streak_count >= self.streak_threshold and self.sequence_position > 0:
            await message.channel.send(f'{message.author.mention} do you hate the planet or something? Be more considerate of our environment, ser.')
            self.reset_streak()
            streak_message = message.content
            self.streak_users = [(message.author, 1)]
            self.streak_count = 1
        # If the message does not match the streak message, reset the streak
        else:
            if self.streak_count >= self.streak_threshold:
                await message.channel.send(f'{message.author.mention} has broken the pasta, thx for nothing buzzkill. Better luck next time!')
            self.reset_streak()
            self.streak_message = message.content
            self.streak_users = [(message.author, 1)]
            self.streak_count = 1