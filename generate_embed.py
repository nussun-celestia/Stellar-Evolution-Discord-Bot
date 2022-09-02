from discord import Embed
import numpy as np
import re


EMBED_COLOR = 0xCCDFF0
ERROR_COLOR = 0xFF0000


def generate_embed(*args, title: str):
    args = list(args)

    if not ('ERROR' in args[0] or True in (issubclass(type(i), Exception) for i in args)):
        stdout = args.pop(0)

        matches = re.findall('(.+\\b)\s+Time\s+([\d.]+)\s+Mass\s+([\d.]+)', stdout)

        columns = ['\n'.join(np.char.strip(column)) for column in zip(*matches)]

        embed = Embed(title=title, colour=EMBED_COLOR)
        embed.add_field(name='Stage', value=columns[0], inline=True)
        embed.add_field(name='Time', value=columns[1], inline=True)
        embed.add_field(name='Mass', value=columns[2], inline=True)
    else:
        embed = Embed(title=title, colour=ERROR_COLOR)
        if 'ERROR' in args[0]:
            stdout = args.pop(0)
            embed.add_field(name='Output', value=stdout, inline=False)
        else:
            stdout = ''
    
    value = ''.join([str(field) for field in args])
    
    if value:
        embed.description = value

    return embed
