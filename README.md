<div>
  <h1 align='center'>
    paginator.py
  </h1>
</div>
<div>
  <p align='center'>
    <img src=https://img.shields.io/pypi/dm/paginator.py?color=success&label=PyPi%20Downloads&style=flat-square>
    <img src=https://shields.io/github/issues-raw/FlamptX/discord-paginator?color=success&label=Active%20Issues&style=flat-square>
    <img src=https://img.shields.io/badge/Latest_Version-0.8.3-informational>
  </p>
  <p align='center'>
    Simple to use discord paginator for messages and embeds with reactions and buttons.
  </p>
</div>
<br>

## Features
- Very easy to use
- Customisable
- Change pages with buttons or reactions
- Actively maintained
## Links
- **[Documentation](https://flampt.gitbook.io/paginator)**
- **[PyPi](https://pypi.org/project/paginator.py)**
## Installation
You can easily install it using the python package manager `pip`

```
pip install paginator.py
```
Note: paginator.py only works with [Diskord](https://github.com/diskord-dev/diskord)

## Quickstart
Here are some examples that might help.
### Sending a message with pages that uses reaction

```python
from paginator import Paginator, Page, NavigationType
from diskord import Embed

...

paginator = Paginator(bot)


@bot.command()
async def test(ctx):
    pages = [
        Page(content="React!", embed=Embed(title="Page #1", description="Testing")),
        Page(embed=Embed(title="Page #2", description="Still testing")),
        Page(embed=Embed(title="Page #3", description="Guess... testing"))
    ]

    await paginator.send(ctx.channel, pages, type=NavigationType.Reactions)
```
### Sending a message with pages that uses buttons

```python
from paginator import Paginator, Page, NavigationType
from diskord import Embed

...

paginator = Paginator(bot)


@bot.command()
async def test(ctx):
    pages = [
        Page(content="Click!", embed=Embed(title="Page #1", description="Testing")),
        Page(embed=Embed(title="Page #2", description="Still testing")),
        Page(embed=Embed(title="Page #3", description="Guess... testing"))
    ]

    await paginator.send(ctx.channel, pages, type=NavigationType.Buttons)
```
## Changing the emojis

```python
from paginator import Paginator, PageEmojis

...

paginator = Paginator(bot)

class Emojis(PageEmojis):
    def __init__(self):
        super().__init__()

        self.back = "⏪"
        self.forward = "⏩"

paginator.page_emojis = Emojis()
```
## Contributions
Feel free to open pull requests and improve the library. If you find any issues, please report it.
