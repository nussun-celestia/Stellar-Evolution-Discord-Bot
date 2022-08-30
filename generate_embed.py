import re
from discord import Embed

def generate_embed(stdout: str):
    matches = re.findall("(.+\\b)\s+Time\s+([\d.]+)\s+Mass\s+([\d.]+)", stdout)

    values = ["", "", ""]
    for line in matches:
        for i in range(3):
            values[i] += line[i] + '\n'
    
    for i in range(3):
        values[i] = values[i][:-1]

    embed = Embed(title="Plot", colour=0x00FF00)
    embed.add_field(name="Stage", value=values[0], inline=True)
    embed.add_field(name="Time", value=values[1], inline=True)
    embed.add_field(name="Mass", value=values[2], inline=True)

    return embed


