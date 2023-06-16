### imports
import os
import constants
import asyncio
import gohmpricebot
import ohmpricebot
import ohmindexbot
import ohmlbbot
import ohmmcapbot
import sentinelbot

gpb = gohmpricebot.GohmPriceDiscordBot("olyprice!",constants.ADMIN_ROLE, constants.PRICE_UPDATE_INTERVAL)

opb = ohmpricebot.OhmPriceDiscordBot("ohmprice!",constants.ADMIN_ROLE, constants.PRICE_UPDATE_INTERVAL)

oib = ohmindexbot.OhmIndexDiscordBot("olyindex!",constants.ADMIN_ROLE, constants.INDEX_UPDATE_INTERVAL)

olbb = ohmlbbot.OhmLiquidBackingDiscordBot("ohmliq!",constants.ADMIN_ROLE, constants.LB_UPDATE_INTERVAL)

omcb = ohmmcapbot.OhmMarketCapDiscordBot("olymcap!",constants.ADMIN_ROLE, constants.PRICE_UPDATE_INTERVAL)

sentinel = sentinelbot.SentinelDiscordBot("oly!",constants.ADMIN_ROLE, constants.INTERN_ROLE)

#run
loop = asyncio.get_event_loop()

# loop.create_task(oib.bot.start(os.environ['INDEX_BOT_TOKEN']))

# loop.create_task(gpb.bot.start(os.environ['GOHM_PRICE_BOT_TOKEN']))

# loop.create_task(opb.bot.start(os.environ['OHM_BOT_TOKEN']))

# loop.create_task(omcb.bot.start(os.environ['MCAP_BOT_TOKEN']))

# loop.create_task(sentinel.bot.start(os.environ['SENTINEL_BOT_TOKEN']))

# loop.create_task(olbb.bot.start(os.environ['LB_SMA_BOT_TOKEN']))

try:
  loop.run_forever()
finally:
  loop.stop()