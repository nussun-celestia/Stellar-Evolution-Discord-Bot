import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from generate_embed import generate_embed
import sse
import sse_plot


class EVOLV1Error(Exception):
    pass


def init():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='$', intents=intents)

    @bot.command()
    async def sync(ctx):
        await bot.tree.sync()
        await ctx.send('Successfully synced commands.')

    async def handle_evolv1_error(interaction: discord.Interaction, stdout: str) -> None:
        try:
            raise EVOLV1Error('An error has occured in EVOLV1; try using different parameters')
        except EVOLV1Error as e:
            embed = generate_embed(stdout, e, title='Error')
            await interaction.response.send_message(embed=embed)

    async def handle_nonpositive_mass(interaction: discord.Interaction) -> None:
        try:
            raise NotImplementedError('Negative or zero mass currently not supported')
        except NotImplementedError as e:
            embed = generate_embed('', e, title='Error')
            await interaction.response.send_message(embed=embed)

    def sse_input_descriptions(func):
        return app_commands.describe(
            # Descriptions borrowed from sse.f except for z_type
            mass='mass is in solar units.',
            z='z is metallicity in the range 0.0001 -> 0.03 where 0.02 is Population I.',
            z_type='units to use for metallicity; one of: (z, feh)',
            tphysf='tphysf is the maximum evolution time in Myr.',

            neta='neta is the Reimers mass-loss coefficent (neta*4x10^-13; 0.5 normally).',
            bwind='bwind is the binary enhanced mass loss parameter (inactive for single).',
            hewind='hewind is a helium star mass loss factor (1.0 normally).',
            sigma='sigma is the dispersion in the Maxwellian for the SN kick speed (190 km/s).',

            ifflag='ifflag > 0 uses WD IFMR of HPE, 1995, MNRAS, 272, 800 (0).',
            wdflag='wdflag > 0 uses modified-Mestel cooling for WDs (0).',
            bhflag='bhflag > 0 allows velocity kick at BH formation (0).',
            nsflag='nsflag > 0 takes NS/BH mass from Belczynski et al. 2002, ApJ, 572, 407 (1).',
            mxns='mxns is the maximum NS mass (1.8, nsflag=0; 3.0, nsflag=1).',
            idum='idum is the random number seed used in the kick routine.'
        )(func)

    @bot.tree.command()
    @sse_input_descriptions
    async def evolve(interaction: discord.Interaction,
                     mass: float, z: float, tphysf: float, z_type: str='z',
                     neta: float=0.5, bwind: float=0.0, hewind: float=0.5, sigma: float=190.0,
                     ifflag: int=0, wdflag: int=1, bhflag: int=0, nsflag: int=1, mxns: float=3.0, idum: int=999,
                     pts1: float=0.05, pts2: float=0.01, pts3: float=0.02) -> None:
        if mass > 0.0:
            if z_type == 'feh':
                z = 0.02 * 10**z
            await sse.construct_evolve_in(mass, z, tphysf,
                                          neta=neta, bwind=bwind, hewind=hewind, sigma=sigma,
                                          ifflag=ifflag, wdflag=wdflag, bhflag=bhflag, nsflag=nsflag, mxns=mxns, idum=idum,
                                          pts1=pts1, pts2=pts2, pts3=pts3)
            stdout = await sse.run_sse()
            if 'ERROR' in stdout:
                await handle_evolv1_error(interaction, stdout)
            else:
                embed = generate_embed(stdout, title='Output')
                await interaction.response.send_message(embed=embed)
                await interaction.channel.send(file=discord.File(f'{sse.SSE_FOLDER}/evolve.dat'))
        else:
            await handle_nonpositive_mass(interaction)

    @bot.tree.command()
    @sse_input_descriptions
    @app_commands.describe(
        xbounds='x-axis bounds for the plot.',
        ybounds='y-axis bounds for the plot.',
        theme='theme for the plot; use one of the available: (default, dark)'
    )
    async def plot(interaction: discord.Interaction,
                   mass: float, z: float, tphysf: float, z_type: str='z',
                   xbounds: str='default', ybounds: str='default', theme: str='default',
                   neta: float=0.5, bwind: float=0.0, hewind: float=0.5, sigma: float=190.0,
                   ifflag: int=0, wdflag: int=1, bhflag: int=0, nsflag: int=1, mxns: float=3.0, idum: int=999,
                   pts1: float=0.05, pts2: float=0.01, pts3: float=0.02) -> None:
        if mass > 0.0:
            if z_type == 'feh':
                z = 0.02 * 10**z
            await sse.construct_evolve_in(mass, z, tphysf,
                                          neta=neta, bwind=bwind, hewind=hewind, sigma=sigma,
                                          ifflag=ifflag, wdflag=wdflag, bhflag=bhflag, nsflag=nsflag, mxns=mxns, idum=idum,
                                          pts1=pts1, pts2=pts2, pts3=pts3)
            stdout = await sse.run_sse()
            if 'ERROR' in stdout:
                await handle_evolv1_error(interaction, stdout)
            else:
                await sse_plot.sse_plot(xbounds, ybounds, theme)
                embed = generate_embed(stdout, title='Output')
                file = discord.File(f'hrdiag.png', filename='hrdiag.png')
                embed.set_image(url=f'attachment://hrdiag.png')
                await interaction.response.send_message(file=file, embed=embed)
        else:
            await handle_nonpositive_mass(interaction)

    bot.run(TOKEN)


if __name__ == '__main__':
    init()
