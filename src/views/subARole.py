import asyncio
import discord
from src.extras.emojis import *
from discord.ext import commands
from src.extras.func import db_fetch_object, db_push_object


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


async def sub_view_arole(
        ctx: commands.Context,
        interaction: discord.Interaction,
        bot: discord.Client
):
    data = await db_fetch_object(
        guildId=ctx.guild.id,
        key='arole'
    )
    if data and data['item'][0].isdigit():
        role = ctx.guild.get_role(int(data['item'][0]))
    else:
        role = None

    string = role.mention if role else '**None**'

    emd = discord.Embed(
        description=f'**{ctx.guild.me.display_name}\'s** current **alert role** is {string}'
                    f'\n\nTo set new **Alert Role** tap **` Edit `**'
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
        new = await interaction.message.edit(
            content=f'{ctx.author.mention}',
            embed=discord.Embed(
                description='Please mention a **Role** to set as **Alert Role:**'
                            '\n **Note:** `@everyone` isn\'t even a proper role'
            ),
            view=None
        )

        def check(m):
            return m.author == ctx.author

        try:
            response = await bot.wait_for('message', check=check, timeout=20)
            mentions = response.role_mentions
            role = mentions[0] if mentions else None
            try:
                await new.delete()
            except discord.errors.NotFound:
                pass
            if role:
                await ctx.send(
                    content=f'{ctx.author.mention}',
                    embed=discord.Embed(
                        description=f'{Emo.CHECK} **{ctx.guild.me.display_name}\'s** '
                                    f'new alert role is {role.mention}',
                    )
                )
                await db_push_object(
                    guildId=ctx.guild.id,
                    key='arole',
                    item=[str(role.id)]
                )
            else:
                await ctx.send(
                    content=f'{ctx.author.mention}',
                    embed=discord.Embed(
                        description=f'{Emo.WARN}'
                                    f' you did not mention a role',
                    )
                )
        except asyncio.TimeoutError:
            await ctx.send('**Bye! you took so long**')
    elif view.value == 2:
        await interaction.message.delete()
        await ctx.send(
            content=f'{ctx.author.mention}',
            embed=discord.Embed(
                description=f'{Emo.CHECK} **{ctx.guild.me.display_name}\'s** '
                            f'alert role has been removed',
            )
        )
        await db_push_object(
            guildId=ctx.guild.id,
            key='arole',
            item=['REMOVED']
        )
    elif view.value == 0:
        try:
            await interaction.message.delete()
        except discord.errors.NotFound:
            pass