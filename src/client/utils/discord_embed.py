from discord import Embed

COLORS = {
    'red': 0xff0000,
    'green': 0x00ff00,
    'blue': 0x0000ff,
    'maroon': 0x800000,
    'orange': 0xff8000,
    'purple': 0x8000ff,
    'yellow': 0xffff00,
    'lightblue': 0x00ffff,
    'darkgreen': 0x008000,
}

"""
Creates Discord Embed's based on templates provided in here.

This allows for a standardized subset of Embeds that the bot can choose from, and customize before sending.
"""

def success_embed(**kwargs):
    success_thumb = "https://i.imgur.com/0ZRPBBr.png"

    embed = Embed(title=kwargs.pop('title', 'Success'), color=COLORS['green'])

    embed.set_thumbnail(url=success_thumb)

    _process_kwargs(embed, **kwargs)
    
    return embed
    
def error_embed(**kwargs):
    error_thumb = "https://i.imgur.com/GwSVr9K.png"

    embed = Embed(title=kwargs.pop('title', '**Error**'), color=COLORS['red'])

    embed.set_thumbnail(url=error_thumb)

    _process_kwargs(embed, **kwargs)
    
    return embed

def informational_embed(**kwargs):
    embed = Embed(title=kwargs.pop('title', 'Information'), color=COLORS['orange'])

    _process_kwargs(embed, **kwargs)
    
    return embed
    
def general_embed(**kwargs):
    embed = Embed(title=kwargs.pop('title', 'General'), color=COLORS['blue'])

    if kwargs.get('color') and kwargs.get('color') in COLORS:
        embed.color = COLORS[kwargs.get('color')]

    _process_kwargs(embed, **kwargs)
    
    return embed

def _process_kwargs(embed, **kwargs):
    if kwargs.get('description'):
        embed.description = kwargs.get('description')

    if kwargs.get('thumbnail'):
        embed.set_thumbnail(url=kwargs.get('thumbnail'))

    if kwargs.get('author'):
        embed.set_author(name=kwargs.get('author'))

    if kwargs.get('footer'):
        embed.set_footer(text=kwargs.get('footer'))

    if kwargs.get('image'):
        embed.set_image(url=kwargs.get('image'))

    if kwargs.get('timestamp'):
        embed.timestamp(kwargs.get('timestamp'))

    if kwargs.get('url'):
        embed.url = kwargs.get('url')
