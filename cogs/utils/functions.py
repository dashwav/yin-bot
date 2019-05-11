"""Generalized Functions Hub."""

# internal modules
import re

# external modules
import discord
from discord.ext import commands

# relative modules

class MemberID(commands.Converter):
    """Extract a member id and force to be in guild.
    
    The main purpose is for banning people and forcing the to-be-banned user in the guild.
    """
    async def convert(self, ctx, argument):
        try:
            argument = extract_id(argument)
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return str(int(argument, base=10))
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid'\
                                            'member or member ID.") from None
        else:
            can_execute = ctx.author.id == ctx.bot.owner_id or \
                ctx.author == ctx.guild.owner or \
                ctx.author.top_role > m.top_role

            if not can_execute:
                raise commands.BadArgument('You cannot do this action on this'
                                           ' user due to role hierarchy.')
            return m

class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        member_id = extract_id(argument)
        if member_id != None:
            entity = discord.utils.find(
                lambda u: str(u.user.id) == str(member_id), ban_list)
            return entity
        else:
            raise commands.BadArgument("Not a valid previously-banned member.")


class GeneralMember(commands.Converter):
    """Generalized member maker.
    
    This will try to resolve a member given some argument, if unable to and the argument is an id, will contruct a fake user. If argument isnt an id then fail
    """
    async def convert(self, ctx, argument):
        failed = False
        target = None
        try:
            target = get_member(ctx, argument)
        except Exception as e:
            failed = True
            self.bot.logger.warning(f'Problems resolving member, making a fake user. Probably was removed from the guild. {e}')
        if failed or isinstance(target, type(None)):
            try:
                member_id = extract_id(argument, 'member')
                target = create_fake_user(member_id)
                target.guild = ctx.guild
                target.bot = False
            except Exception as e:
                self.bot.logger.warning(f'Problems resolving member, making a fake user. Probably was removed from the guild. {e}')
        if target != None:
            return target
        else:
            raise commands.BadArgument("Not a valid member.")


def create_fake(target_id: str, dtype: str='member'):
    if dtype == 'member':
        return create_fake_user(target_id)


def create_fake_user(user_id: str):
    member = fake_object(int(user_id))
    member.name = 'GenericUser'
    member.displayname = member.name
    member.discriminator = '0000'
    member.mention = f'<@{member.id}>'
    member.joined_at = datetime.datetime.utcnow()
    return member

class fake_object:

    def __init__(self, snowflake):
        self.id = int(snowflake)
        self.name = ''
        self.created_at = datetime.datetime.utcnow()

    def __repr__(self):
        return ''.format(self.id)

    def __eq__(self, other):
        return self.id == other.id

def clean_command(argument: str):
    """Check if argument is # or <@#>.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare id
    """
    i = 1
    for x in argument:
        if x != ' ':
            i += 1
        else:
            break
    return argument[i:]


def clean_str(argument: str, dtype: str='role'):
    argument = str(argument)
    general = argument.replace('<', '').replace('>', '')\
                      .replace('@', '')
    if dtype == 'role':
        return general.replace('&', '')
    if dtype == 'channel':
        return general.replace('#', '')
    else:
        return general.replace('#', '').replace('&', '')


def is_id(argument: str):
    """Check if argument is #.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare id
    """
    status = True
    for x in argument:
        try:
            _ = int(x)
        except:
            status = False
            return False
    return True


def get_member(ctx, argument: str):
    """Tries to return a member object.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    discord.Member
        member object to return
    """
    ret = extract_id(argument, 'member')
    t_st = clean_str(argument, 'member').lower()
    if not ret:
        ret = discord.utils.find(lambda m: (m.id == ret) or (m.name.lower() == t_st), ctx.guild.members)
    else:
        ret = ctx.guild.get_member(int(ret))
    if not ret:
        ret = ctx.guild.get_member_named(t_st)
    if ret:
        return ret
    else:
        return None

def extract_id(argument: str, dtype: str='member'):
    """Check if argument is # or <@#>.

    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare id
    """
    if argument.strip(' ') == '':
        return ''
    argument = clean_str(argument, dtype)
    if is_id(argument):
        return argument
    if dtype == 'member':
        regexes = (
            r'\<?\@?(\d{17,})\>?',  # '<@!?#17+>'
            r'\<?\@?(\d{1,})\>?',  # '<@!?#+>'
            r'?(\d{17,})',  # '!?#17+>'
            r'?(\d{1,})',  # '!?#+>'
        )
    elif dtype == 'role':
        regexes = (
            r'\<?\@?\&?(\d{17,})\>?',  # '<@!?#17+>'
            r'\<?\@?\&?(\d{1,})\>?',  # '<@!?#+>'
            r'?(\d{17,})',  # '!?#17+>'
            r'?(\d{1,})',  # '!?#+>'
        )
    elif dtype == 'channel':
        regexes = (
            r'\<?\#?(\d{17,})\>?',  # '<@!?#17+>'
            r'\<?\#?(\d{1,})\>?',  # '<@!?#+>'
            r'?(\d{17,})',  # '!?#17+>'
            r'?(\d{1,})',  # '!?#+>'
        )
    else:
        regexes = (
            r'?(\d{17,})',  # '!?#17+>'
            r'?(\d{1,})',  # '!?#+>'
        )
    i = 0
    member_id = ''
    while i < len(regexes):
        regex = regexes[i]
        try:
            match = re.finditer(regex, argument, re.MULTILINE)
        except:
            match = None
        i += 1
        if match is None:
            continue
        else:
            match = [x for x in match]
            if len(match) > 0:
                match = match[0]
                member_id = int(match[0], base=10)
                return str(member_id)
    return None

# end of code

# end of file
