"""Generalized Functions Hub."""

# internal modules
import datetime

# external modules
import discord
from discord.ext import commands

# relative modules


class MemberID(commands.Converter):
    """Extract a member id and force to be in guild."""

    """
    The main purpose is for banning people and forcing
    the to-be-banned user in the guild.
    """
    async def convert(self, ctx, argument):
        """Discord converter."""
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
    """Find a banned user."""

    async def convert(self, ctx, argument):
        """Discord converter."""
        ban_list = await ctx.guild.bans()
        member_id = extract_id(argument)
        if member_id is not None:
            entity = discord.utils.find(
                lambda u: str(u.user.id) == str(member_id), ban_list)
            return entity
        else:
            raise commands.BadArgument("Not a valid previously-banned member.")


class GeneralMember(commands.Converter):
    """Generalized member maker."""

    """
    This will try to resolve a member given some argument,
    if unable to and the argument is an id, will contruct a fake user.
    If argument isn't an id then fail
    """
    async def convert(self, ctx, argument):
        """Discord Convert."""
        failed = False
        target = None
        try:
            target = get_member(ctx, argument)
        except Exception as e:
            failed = True
            self.bot.logger.warning(f'Problems resolving member, making a fake user. Probably was removed from the guild. {e}')  # noqa
        if failed or target is None:
            try:
                member_id = extract_id(argument, False)
                assert member_id is not None
                target = create_fake_user(member_id)
                target.guild = ctx.guild
                target.bot = False
            except Exception as e:
                self.bot.logger.warning(f'Problems making a fake user.{e}')  # noqa
        if target is not None:
            return target
        else:
            raise commands.BadArgument("Not a valid member.")


def create_fake(target_id: str, dtype: str = 'member'):
    """General ABC creator."""
    if dtype == 'member':
        return create_fake_user(target_id)


def create_fake_user(user_id: str):
    """Create fake ABC for a user."""
    member = fake_object(int(user_id))
    member.name = 'GenericUser'
    member.displayname = member.name
    member.discriminator = '0000'
    member.mention = f'<@{member.id}>'
    member.joined_at = datetime.datetime.utcnow()
    member.bot = False
    return member


def duplicate_member(base_member):
    """Duplicate a member object."""
    new_member = create_fake_user(base_member.id)
    for i in dir(base_member):
        if '__' in i:
            continue
        setattr(new_member, i, getattr(base_member, i))
    return new_member


class fake_object(object):
    """Recreate ABC class."""

    def __init__(self, snowflake):
        """Init. Method."""
        self.id = int(snowflake)
        self.name = ''
        self.created_at = datetime.datetime.utcnow()

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)

    def __repr__(self):
        """Repr method."""
        return ''.format(self.id)

    def __eq__(self, other):
        """Equiv Method."""
        return self.id == other.id


def get_member(ctx, argument: str):
    """Return a member object."""
    """
    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    discord.Member
        member object to return
    """
    ret = extract_id(argument)
    t_st = argument.lower()
    if not ret:
        ret = discord.utils.find(lambda m: (m.id == ret) or
                                           (t_st in [m.name.lower(), m.display_name.lower()]),  # noqa
                                 ctx.guild.members)
    else:
        ret = ctx.guild.get_member(int(ret))
    if not ret:
        ret = ctx.guild.get_member_named(t_st)
    if ret:
        return ret
    else:
        return None


def extract_id(argument: str, strict: bool=True):
    """Extract id from argument."""
    """
    Parameters
    ----------
    argument: str
        text to parse

    Returns
    ----------
    str
        the bare id
    """
    ex = ''.join(list(filter(str.isdigit, str(argument))))
    if strict:
        if len(ex) < 15:
            return None
    return ex


# end of code

# end of file
