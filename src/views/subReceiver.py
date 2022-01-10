import discord
from src.extras.emojis import *
from discord.ext import commands
from src.extras.func import db_push_object, db_fetch_object


class BaseView(discord.ui.View):

    def __init__(
            self,
            message: discord.Message = None,
    ):
        self.message = message
        super().__init__()
        self.value = None
        self.timeout = 30

    async def on_timeout(self) -> None:
        try:
            self.clear_items()
            await self.message.edit(view=self)
        except Exception:
            pass


class Option(discord.ui.View):
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.message = None
        super().__init__()
        self.value = None

    @discord.ui.button(label='Edit', style=discord.ButtonStyle.green)
    async def edit(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 1
            self.stop()

    @discord.ui.button(label='Remove', style=discord.ButtonStyle.blurple)
    async def remove(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 2
            self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.ctx.author == interaction.user:
            self.value = 0
            self.stop()


class TextMenu(discord.ui.Select):

    def __init__(
            self,
            bot: discord.Client,
            context: commands.Context,
    ):
        self.ctx = context
        self.bot = bot
        channels = context.guild.text_channels
        eligible = [
            channel for channel in channels if channel.permissions_for(
                context.guild.me
            ).embed_links
        ]
        options = [
            discord.SelectOption(
                label=channel.name,
                value=str(channel.id),
                emoji=Emo.TEXT
            ) for channel in eligible[:24]
        ]
        options.insert(
            0, discord.SelectOption(label='Exit', value='0', emoji=Emo.WARN)
        )
        super().__init__(
            placeholder='Select a text channel',
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.ctx.author:
            if int(self.values[0]) != 0:
                channel = self.bot.get_channel(int(self.values[0]))
                emd = discord.Embed(
                    title=f'{Emo.YT} Receiver channel edited!',
                    description=f'{Emo.CHECK} The new receiver channel is {channel.mention}'
                                f'\nThis channel will be used to receive livestream & upload notifications'
                )
                await interaction.message.edit(
                    embed=emd,
                    view=None

                )
                await db_push_object(
                    guild_id=self.ctx.guild.id,
                    item=[self.values[0]],
                    key='alertchannel'
                )
            else:
                await interaction.message.delete()


async def sub_view_receiver(
        ctx: commands.Context,
        interaction: discord.Interaction,
        bot: discord.Client
):
    raw = await db_fetch_object(guild_id=ctx.guild.id, key='alertchannel')

    def _check():
        if raw and raw[0].isdigit():
            receiver = ctx.guild.get_channel(int(raw[0]))
            try:
                return receiver.mention
            except AttributeError:
                return '**`None`**'
        else:
            return '**`None`**'

    emd = discord.Embed(
        description=f'To set new receiver tap **` Edit `**'
                    f'\n\n{Emo.WARN} Only accepts text channels where'
                    f'\nit has permission to **embed links** and **urls**'
                    f'\n\n**{ctx.guild.name}\'s** current receiver is {_check()}'
    )
    if ctx.guild.icon:
        emd.set_author(
            icon_url=ctx.guild.icon.url,
            name=ctx.guild.name
        )
    else:
        emd.set_author(
            icon_url=ctx.guild.me.avatar.url,
            name=ctx.guild.me.name
        )

    view = Option(ctx)
    await interaction.response.edit_message(embed=emd, view=view)
    await view.wait()

    if view.value == 1:
        view.clear_items()
        new_view = BaseView()
        new_view.add_item(TextMenu(context=ctx, bot=bot))
        new_view.message = await interaction.message.edit(
            content=f'{ctx.author.mention}',
            embed=discord.Embed(
                description='Please **select** a text channel to use as **receiver:**'
            ),
            view=new_view
        )
    elif view.value == 2:
        await interaction.message.edit(
            content=f'{ctx.author.mention}',
            embed=discord.Embed(
                description=f'{Emo.DEL} Receiver removed'
            ),
            view=None
        )
        await db_push_object(
            guild_id=ctx.guild.id,
            item=['removed'],
            key='alertchannel'
        )
    elif view.value == 0:
        await interaction.message.delete()
