"""Actually runs the code."""
from asyncio import get_event_loop
from bot import Yinbot
from cogs import Admin, AutoAssign, Filter, Gateway, Info, Logging, Moderation
from cogs import Owner, Pings, RNG, Roles, Stats, Voice, Warnings


def run():
    """Build the bot object using the various cogs."""
    loop = get_event_loop()
    bot = loop.run_until_complete(Yinbot.get_instance())
    cogs = [
      Admin(bot),
      AutoAssign(bot),
      Filter(bot),
      Gateway(bot),
      Info(bot),
      Logging(bot),
      Moderation(bot),
      Owner(bot),
      Pings(bot),
      RNG(bot),
      Roles(bot),
      Stats(bot),
      Voice(bot),  
      Warnings(bot)
    ]
    bot.start_bot(cogs)


if __name__ == '__main__':
    run()
