# Imports
import asyncio
import discord
from discord import TextChannel, DMChannel, Client
from discord.ext import commands
from discord_components import DiscordComponents, InteractionType, Button
from .objects import *

class Paginator:
    """
    The main paginator class used for sending the message

    __init__
        bot: Union[Client, commands.Bot]
            Needed to send the message and wait for a reaction or button click
        page_emojis
            The emojis used to go back and forward
            It can be changed by making your own class for it

    send coroutine
        channel: Union[TextChannel, DMChannel]
            The channel to send the message to
        pages_message: PagesMessage
            The object containing data to send the message
    """
    def __init__(self, bot: Union[Client, commands.Bot]):
        self.bot = bot
        self._page_emojis = PageEmojis()

        self.components = False

    @property
    def page_emojis(self):
        return self._page_emojis

    @page_emojis.setter
    def page_emojis(self, obj: PageEmojis):
        self._page_emojis = obj

    async def send(self, channel: Union[TextChannel, DMChannel], pages_message: MessagePages, timeout: int = 60, restricted_user: Union[discord.Member, discord.User] = None, disable_on_timeout: bool = True):

        embed = pages_message.pages[0].embed

        if pages_message.type == 1:
            if embed is not None:
                try:
                    footer_text = embed.footer.text
                    footer_edit = footer_text + f"Page 1 of {len(pages_message.pages)}"
                except TypeError:
                    footer_edit = f"Page 1 of {len(pages_message.pages)}"
                embed.set_footer(text=footer_edit)

            msg = await channel.send(content=pages_message.pages[0].content, embed=embed)

            emojis = [self.page_emojis.back, self.page_emojis.forward]

            for emoji in emojis:
                await msg.add_reaction(emoji)

            current_page = 0

            while not self.bot.is_closed():
                try:
                    reaction, reaction_user = await self.bot.wait_for('reaction_add', check=lambda r, r_user: r.message.id == msg.id and str(r.emoji) in emojis and (r_user == restricted_user) if restricted_user is not None else r_user != self.bot.user, timeout=timeout)

                    if str(reaction.emoji) == emojis[1]:
                        if current_page != len(pages_message.pages) - 1:
                            current_page += 1

                            if embed is not None:
                                try:
                                    embed.set_footer(text=footer_text + f"Page {current_page + 1} of {len(pages_message.pages)}")
                                except TypeError:
                                    embed.set_footer(text=f"Page {current_page + 1} of {len(pages_message.pages)}")

                            await msg.edit(content=pages_message.pages[current_page].content, embed=pages_message.pages[current_page].embed)
                    else:
                        if current_page != 0:
                            current_page -= 1

                            if embed is not None:
                                try:
                                    embed.set_footer(text=footer_text + f"Page {current_page + 1} of {len(pages_message.pages)}")
                                except TypeError:
                                    embed.set_footer(text=f"Page {current_page + 1} of {len(pages_message.pages)}")

                            await msg.edit(content=pages_message.pages[current_page].content, embed=pages_message.pages[current_page].embed)

                    await msg.remove_reaction(str(reaction.emoji), reaction_user)

                except asyncio.TimeoutError:
                    if disable_on_timeout:
                        await msg.clear_reactions()
                    break

        elif pages_message.type == 2:
            if not self.components:
                DiscordComponents(self.bot)
                self.components = True

            msg = await channel.send(content=pages_message.pages[0].content, embed=embed, components=[[
                Button(emoji=self.page_emojis.back, id="back", disabled=True),
                Button(label=f"1/{len(pages_message.pages)}", disabled=True),
                Button(emoji=self.page_emojis.forward, id="forward")
            ]])

            current_page = 0

            while not self.bot.is_closed():
                try:
                    interaction = await self.bot.wait_for('button_click', check=lambda i: i.message.id == msg.id and (i.user == restricted_user) if restricted_user is not None else True, timeout=timeout)
                    if interaction.component.id == "forward":
                        current_page += 1

                        await interaction.respond(content=pages_message.pages[current_page].content, embed=pages_message.pages[current_page].embed, type=InteractionType.UpdateMessage, components=[[
                            Button(emoji=self.page_emojis.back, id="back"),
                            Button(label=f"{current_page + 1}/{len(pages_message.pages)}", disabled=True),
                            Button(emoji=self.page_emojis.forward, id="forward", disabled=True if current_page == len(pages_message.pages) - 1 else False)
                        ]])
                    elif interaction.component.id == "back":
                        current_page -= 1

                        await interaction.respond(content=pages_message.pages[current_page].content, embed=pages_message.pages[current_page].embed, type=InteractionType.UpdateMessage, components=[[
                            Button(emoji=self.page_emojis.back, id="back", disabled=True if current_page == 0 else False),
                            Button(label=f"{current_page + 1}/{len(pages_message.pages)}", disabled=True),
                            Button(emoji=self.page_emojis.forward, id="forward")
                        ]])

                except asyncio.TimeoutError:
                    if disable_on_timeout:
                        await msg.edit(content=pages_message.pages[current_page].content, embed=pages_message.pages[current_page].embed, components=[[
                            Button(emoji=self.page_emojis.back, id="back", disabled=True),
                            Button(label=f"{current_page + 1}/{len(pages_message.pages)}", disabled=True),
                            Button(emoji=self.page_emojis.forward, id="forward", disabled=True)
                        ]])
                    break

