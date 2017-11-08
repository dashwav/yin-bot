"""
Actually runs the code
"""
from asyncio import get_event_loop
from bot import Yinbot
from cogs import Moderation, Owner, Roles, Stats, Admin, Gateway, Logging, Voice


def run():
    """
    Builds the bot object using the various cogs
    """
    loop = get_event_loop()
    bot = loop.run_until_complete(Yinbot.get_instance())
    cogs = [
      Admin(bot),
      Gateway(bot),
      Logging(bot),
      Moderation(bot),
      Owner(bot),
      Roles(bot),
      Stats(bot),
      Voice(bot)
    ]
    bot.start_bot(cogs)


if __name__ == '__main__':
    run()
