"""Actually runs the code."""
from asyncio import get_event_loop
from bot import Yinbot


def import_from(module, name):
    """Generalized importer."""
    module = __import__(module, fromlist=[name])
    print(f'Loaded: {module}.{name}')
    return getattr(module, name)


def run():
    """Build the bot object using the various cogs."""
    loop = get_event_loop()
    bot = loop.run_until_complete(Yinbot.get_instance())
    bot.loaded_cogs = []
    for cog in bot.botcogs:
        c = import_from(f'cogs.{cog}', f'{cog[0].upper()}{cog[1:]}')  # noqa
        bot.loaded_cogs.append(c(bot))
    bot.start_bot(bot.loaded_cogs)


if __name__ == '__main__':
    run()
