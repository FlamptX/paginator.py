from discord import Embed
from typing import Union
from .errors import *

_type = type

class PagesType:
    """
    For those who don't want to remember two numbers, use this in the MessagePages type
    """
    Reactions = 1  # Change page with reactions
    Buttons = 2  # Change page with buttons

class Page:
    """
    Used in MessagePages pages argument
    """
    def __init__(self, content: str = None, embed: Embed = None):
        self.content = content
        self.embed = embed

class MessagePages:
    """
    Only put Page objects in the pages list or you an error will raise
    type must be either 1 or 2, alternative you can use PagesType which returns one of those
    """
    def __init__(self, pages: list, type: int):
        self.pages = pages
        self.type = type

        if type not in [1, 2]:
            raise InvalidTypeError(f"Type {type} is not valid. It should either be 1 or 2.")

        for page in self.pages:
            if not isinstance(page, Page):
                raise InvalidTypeError(f"Found object {_type(page)} in the pages list. Only Page objects should be in it.")

class PageEmojis:
    """
    This can be changed by setting the Paginator.page_emojis to your own class with the PageEmojis inheritance
    """
    def __init__(self):
        self.forward = "➡️"
        self.back = "⬅️"
