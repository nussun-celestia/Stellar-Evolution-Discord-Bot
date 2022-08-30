from discord import Embed
import numpy as np
import re


def generate_embed(stdout: str, title: str):
    matches = re.findall('(.+\\b)\s+Time\s+([\d.]+)\s+Mass\s+([\d.]+)', stdout)

    columns = ['\n'.join(np.char.strip(column)) for column in zip(*matches)]

    embed = Embed(title=title, colour=0xCCDFF0)
    embed.add_field(name='Stage', value=columns[0], inline=True)
    embed.add_field(name='Time', value=columns[1], inline=True)
    embed.add_field(name='Mass', value=columns[2], inline=True)

    return embed
