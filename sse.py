import asyncio
import subprocess
from platform import system

from astropy.io import ascii


SYSTEM = system()
if SYSTEM == 'Windows':
    SSE_FOLDER = 'sse'
    START_SSE = 'start_sse.bat'
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
elif SYSTEM == 'Linux':
    SSE_FOLDER = 'linux-sse'
    START_SSE = ['bash', 'start_sse.sh']
    si = None
else:
    raise NotImplementedError('This program is not supported on this system.')


async def construct_evolve_in(mass: float, z: float, tphysf: float,
                              neta: float=0.5, bwind: float=0.0, hewind: float=0.5, sigma: float=190.0,
                              ifflag: int=0, wdflag: int=1, bhflag: int=0, nsflag: int=1, mxns: float=3.0, idum: int=999,
                              pts1: float=0.05, pts2: float=0.01, pts3: float=0.02) -> None:
        
    with open(f'{SSE_FOLDER}/evolve.in', 'w') as evolve_in:
        evolve_in.write(f'{mass} {z} {tphysf}\n')
        evolve_in.write(f'{neta} {bwind} {hewind} {sigma}\n')
        evolve_in.write(f'{ifflag} {wdflag} {bhflag} {nsflag} {mxns} {idum}\n')
        evolve_in.write(f'{pts1} {pts2} {pts3}\n')


async def run_sse() -> str:
    sse = subprocess.run(START_SSE, capture_output=True, text=True, startupinfo=si)
    stdout = sse.stdout
    stdout = stdout.replace('\n\n', '\n')
    return stdout


def read_evolve_dat() -> None:
    return ascii.read(f'{SSE_FOLDER}/evolve.dat')


async def debug():
    await construct_evolve_in(5.0, 0.02, 12000.)
    stdout = await run_sse()
    print(stdout)


def main():
    asyncio.run(debug())


if __name__ == '__main__':
    main()