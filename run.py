"""
Actually runs the code
"""
from asyncio import get_event_loop
from bot import Yinbot
from cogs import Spoils, Filter, Janitor, Moderation, Stats


def run():
    """
    Builds the bot object using the various cogs
    """
    loop = get_event_loop()
    bot = loop.run_until_complete(Yinbot.get_instance())
    cogs = [
      Spoils(bot),
      Filter(bot),
      Janitor(bot),
      Moderation(bot),
      Stats(bot)
    ]
    bot.start_bot(cogs)


if __name__ == '__main__':
    run()
