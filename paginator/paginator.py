# Imports
import asyncio
import discord
from .objects import *

from discord import TextChannel, DMChannel, Client, Member, User
from discord.ui import View, Button
from discord.ext import commands
from typing import Union, Optional, Awaitable, Callable

_type = type

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
        pages: PagesMessage
            The object containing data to send the message
        Raises
        -----
          TypeError:
          - the type is not 1 or 2
          - the pages list is empty or has an object that is not a Page
    """
    def __init__(self, bot: Union[Client, commands.Bot]):
        self.bot = bot
        self._page_emojis = PageEmojis()

    @property
    def page_emojis(self):
        return self._page_emojis

    @page_emojis.setter
    def page_emojis(self, obj: PageEmojis):
        self._page_emojis = obj

    async def send(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.create_task(self._send_pages(*args, **kwargs))

    async def _send_pages(self, channel: Union[TextChannel, DMChannel], pages: list, type: int = 2, timeout: Optional[int, None] = 60, author: Optional[Union[discord.Member, discord.User]] = None, disable_on_timeout: bool = True, timeout_callback: Optional[Callable[[], Awaitable[None]]] = None):
        """
        Only put Page objects in the pages list.
        Type must be either 1 or 2, an alternative you can use is NavigationType which has those values.
        """

        if type not in [1, 2]:
            raise TypeError(f"Type {type} is not valid. It should either be 1 or 2.")

        if pages is []:
            raise TypeError("pages list is empty")

        for page in pages:
            if not isinstance(page, Page):
                raise TypeError(f"Found {_type(page)} in the pages list. Only Page objects should be in it.")

        if timeout_callback and not asyncio.iscoroutinefunction(timeout_callback):
            raise TypeError("disable_callback must be a coroutine")

        embed = pages[0].embed

        if type == 1:
            if embed is not None:
                try:
                    footer_text = embed.footer.text
                    footer_edit = footer_text + f"Page 1 of {len(pages)}"
                except TypeError:
                    footer_edit = f"Page 1 of {len(pages)}"
                embed.set_footer(text=footer_edit)

            msg = await channel.send(content=pages[0].content, embed=embed)

            emojis = [self.page_emojis.back, self.page_emojis.forward]

            for emoji in emojis:
                await msg.add_reaction(emoji)

            current_page = 0

            while not self.bot.is_closed():
                try:
                    reaction, reaction_user = await self.bot.wait_for('reaction_add', check=lambda r, r_user: r.message.id == msg.id and str(r.emoji) in emojis and (r_user == author) if author is not None else r_user != self.bot.user, timeout=timeout)

                    if str(reaction.emoji) == emojis[1]:
                        if current_page != len(pages) - 1:
                            current_page += 1
                            embed = pages[current_page].embed

                            if embed is not None:
                                try:
                                    embed.set_footer(text=footer_text + f"Page {current_page + 1} of {len(pages)}")
                                except TypeError:
                                    embed.set_footer(text=f"Page {current_page + 1} of {len(pages)}")

                            await msg.edit(content=pages[current_page].content, embed=pages[current_page].embed)
                    else:
                        if current_page != 0:
                            current_page -= 1
                            embed = pages[current_page].embed

                            if embed is not None:
                                try:
                                    embed.set_footer(text=footer_text + f"Page {current_page + 1} of {len(pages)}")
                                except TypeError:
                                    embed.set_footer(text=f"Page {current_page + 1} of {len(pages)}")

                            await msg.edit(content=pages[current_page].content, embed=pages[current_page].embed)

                    await msg.remove_reaction(str(reaction.emoji), reaction_user)

                except asyncio.TimeoutError:
                    if disable_on_timeout:
                        await msg.clear_reactions()
                    if timeout_callback:
                        await timeout_callback()
                    break

        elif type == 2:
            view = View(timeout=timeout)
            btns = [
                Button(emoji=self.page_emojis.back, custom_id="back", disabled=True),
                Button(label=f"1/{len(pages)}", disabled=True),
                Button(emoji=self.page_emojis.forward, custom_id="forward")
            ]
            for i in btns:
                view.add_item(i)

            msg = await channel.send(content=pages[0].content, embed=embed, view=view)

            current_page = 0

            while not self.bot.is_closed():
                try:
                    interaction = await self.bot.wait_for('interaction', check=lambda i: i.message.id == msg.id and (i.user == author) if author is not None else True, timeout=None)
                    custom_id = interaction.data["custom_id"]
                    if custom_id == "forward":
                        current_page += 1
                        view = View()
                        btns = [
                            Button(emoji=self.page_emojis.back, custom_id="back"),
                            Button(label=f"{current_page + 1}/{len(pages)}", disabled=True),
                            Button(emoji=self.page_emojis.forward, custom_id="forward", disabled=True if current_page == len(pages) - 1 else False)
                        ]
                        for i in btns:
                            view.add_item(i)

                        await interaction.response.edit_message(content=pages[current_page].content, embed=pages[current_page].embed, view=view)
                    elif custom_id == "back":
                        current_page -= 1
                        view = View()
                        btns = [
                            Button(emoji=self.page_emojis.back, custom_id="back", disabled=True if current_page == 0 else False),
                            Button(label=f"{current_page + 1}/{len(pages)}", disabled=True),
                            Button(emoji=self.page_emojis.forward, custom_id="forward")
                        ]
                        for i in btns:
                            view.add_item(i)

                        await interaction.response.edit_message(content=pages[current_page].content, embed=pages[current_page].embed, view=view)

                except asyncio.TimeoutError:
                    if disable_on_timeout:
                        view = View()
                        btns = [
                            Button(emoji=self.page_emojis.back, custom_id="back", disabled=True),
                            Button(label=f"{current_page + 1}/{len(pages)}", disabled=True),
                            Button(emoji=self.page_emojis.forward, custom_id="forward", disabled=True)
                        ]
                        for i in btns:
                            view.add_item(i)

                        await msg.edit(content=pages[current_page].content, embed=pages[current_page].embed, view=view)
                    if timeout_callback:
                        await timeout_callback()
                    break
