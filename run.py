"""
Actually runs the code
"""
from asyncio import get_event_loop
from bot import Yinbot
from cogs import Moderation, Owner, Roles, Slowmode, Stats, RNG, Pings
from cogs import Admin, Gateway, Info, Logging, Voice, Filter, Warnings


def run():
    """
    Builds the bot object using the various cogs
    """
    loop = get_event_loop()
    bot = loop.run_until_complete(Yinbot.get_instance())
    cogs = [
      Admin(bot),
      Filter(bot),
      Gateway(bot),
      Info(bot),
      Logging(bot),
      Moderation(bot),
      RNG(bot),
      Roles(bot),
      Slowmode(bot),
      Stats(bot),
      Voice(bot),
      Owner(bot),
      Warnings(bot),
      Pings(bot)
    ]
    bot.start_bot(cogs)


if __name__ == '__main__':
    run()
