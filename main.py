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

    @bot.tree.command()
    @app_commands.describe(
        # Descriptions borrowed from sse.f
        mass='mass is in solar units.',
        z='z is metallicity in the range 0.0001 -> 0.03 where 0.02 is Population I.',
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
    )
    async def evolve(interaction: discord.Interaction,
                     mass: float, z: float, tphysf: float,
                     neta: float=0.5, bwind: float=0.0, hewind: float=0.5, sigma: float=190.0,
                     ifflag: int=0, wdflag: int=1, bhflag: int=0, nsflag: int=1, mxns: float=3.0, idum: int=999,
                     pts1: float=0.05, pts2: float=0.01, pts3: float=0.02) -> None:
        if mass > 0.0:
            await sse.construct_evolve_in(mass, z, tphysf,
                                        neta=neta, bwind=bwind, hewind=hewind, sigma=sigma,
                                        ifflag=ifflag, wdflag=wdflag, bhflag=bhflag, nsflag=nsflag, mxns=mxns, idum=idum,
                                        pts1=pts1, pts2=pts2, pts3=pts3)
            stdout = await sse.run_sse()
            if 'ERROR' in stdout:
                try:
                    raise EVOLV1Error('An error has occured in EVOLV1; try using different parameters')
                except EVOLV1Error as e:
                    await interaction.response.send_message(f'```{stdout}``````{e}```')
            else:
                embed = generate_embed(stdout, title='Output')
                await interaction.response.send_message(file=discord.File(f'{sse.SSE_FOLDER}/evolve.dat'), embed=embed)
        else:
            try:
                raise NotImplementedError('Negative or zero mass currently not supported')
            except NotImplementedError as e:
                await interaction.response.send_message(f'```{e}```')

    @bot.tree.command()
    @app_commands.describe(
        # Descriptions borrowed from sse.f except for xbounds and ybounds
        mass='mass is in solar units.',
        z='z is metallicity in the range 0.0001 -> 0.03 where 0.02 is Population I.',
        tphysf='tphysf is the maximum evolution time in Myr.',

        xbounds='x-axis bounds for the plot.',
        ybounds='y-axis bounds for the plot.',

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
    )
    async def plot(interaction: discord.Interaction,
                   mass: float, z: float, tphysf: float,
                   xbounds: str='default', ybounds: str='default',
                   neta: float=0.5, bwind: float=0.0, hewind: float=0.5, sigma: float=190.0,
                   ifflag: int=0, wdflag: int=1, bhflag: int=0, nsflag: int=1, mxns: float=3.0, idum: int=999,
                   pts1: float=0.05, pts2: float=0.01, pts3: float=0.02) -> None:
        if mass > 0.0:
            await sse.construct_evolve_in(mass, z, tphysf,
                                        neta=neta, bwind=bwind, hewind=hewind, sigma=sigma,
                                        ifflag=ifflag, wdflag=wdflag, bhflag=bhflag, nsflag=nsflag, mxns=mxns, idum=idum,
                                        pts1=pts1, pts2=pts2, pts3=pts3)
            stdout = await sse.run_sse()
            if 'ERROR' in stdout:
                try:
                    raise EVOLV1Error('An error has occured in EVOLV1; try using different parameters')
                except EVOLV1Error as e:
                    await interaction.response.send_message(f'```{stdout}``````{e}```')
            else:
                await sse_plot.sse_plot(xbounds, ybounds)
                embed = generate_embed(stdout, title='Output')
                file = discord.File(f'hrdiag.png', filename='hrdiag.png')
                embed.set_image(url=f'attachment://hrdiag.png')
                await interaction.response.send_message(file=file, embed=embed)
        else:
            try:
                raise NotImplementedError('Negative or zero mass currently not supported')
            except NotImplementedError as e:
                await interaction.response.send_message(f'```{e}```')

    bot.run(TOKEN)


if __name__ == '__main__':
    init()
