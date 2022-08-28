import subprocess
from platform import system
import asyncio

from astropy.io import ascii

if system() == "Windows":
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
elif system() == "Linux":
    si = None
else:
    raise NotImplementedError("This program is not supported on this system.")


async def construct_evolve_in(mass, z, tphysf,
                              neta=0.5, bwind=0.0, hewind=0.5, sigma=190.0,
                              ifflag=0, wdflag=1, bhflag=0, nsflag=1, mxns=3.0, idum=999,
                              pts1=0.05, pts2=0.01, pts3=0.02):

    with open('sse/evolve.in', 'w') as evolve_in:
        evolve_in.write(f'{mass} {z} {tphysf}\n')
        evolve_in.write(f'{neta} {bwind} {hewind} {sigma}\n')
        evolve_in.write(f'{ifflag} {wdflag} {bhflag} {nsflag} {mxns} {idum}\n')
        evolve_in.write(f'{pts1} {pts2} {pts3}\n')


async def run_sse():
    if system() == "Windows":
        start_file = "start_sse.bat"
    elif system() == "Linux":
        start_file = ["bash", "start_sse.sh"]
    else:
        raise RuntimeError()
    
    sse = subprocess.run(start_file, capture_output=True, text=True, startupinfo=si)
    stdout = sse.stdout
    stdout = stdout.replace('\n\n', '\n')
    return stdout


def read_evolve_dat():
    return ascii.read('sse/evolve.dat')


async def debug():
    await construct_evolve_in(5, 0.00001, 12000)
    stdout = await run_sse()
    print(stdout)


if __name__ == "__main__":
    asyncio.run(debug())