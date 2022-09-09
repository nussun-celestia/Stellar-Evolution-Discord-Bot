import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator

import sse


async def sse_plot(xbounds: str='default', ybounds: str='default', theme: str='default') -> None:
    # Set theme
    if theme == 'dark':
        plt.style.use('dark_background')
        line_color = (1, 1, 1)
    else:
        line_color = (0, 0, 0)

    # Create figure
    fig = plt.figure('SSE HR-diagram', figsize=(4, 5.7), dpi=200.0)
    ax = plt.gca()

    # Make window not be resizable
    mng = plt.get_current_fig_manager()
    mng.window.resizable(False, False)

    # Set limits
    if xbounds == 'default':
        plt.xlim(4.75, 3.3)
    elif xbounds == 'auto':
        ax.invert_xaxis()
    else:
        xmin, xmax = xbounds.split(',')
        xmin, xmax = float(xmin), float(xmax)
        plt.xlim(xmin, xmax)
    if ybounds == 'default':
        plt.ylim(-1.8, 6.5)
    elif ybounds != 'auto':
        ymin, ymax = ybounds.split(',')
        ymin, ymax = float(ymin), float(ymax)
        plt.ylim(ymin, ymax)

    # Set ticks to appear on all axes
    ax.xaxis.set_ticks_position('both')
    ax.yaxis.set_ticks_position('both')

    # Set ticks to face inward
    plt.tick_params(axis='both', which='both', direction='in')

    # Set major tick frequency
    ax.xaxis.set_major_locator(MultipleLocator(base=0.5))
    ax.yaxis.set_major_locator(MultipleLocator(base=1))

    # Set minor tick frequency
    ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    ax.yaxis.set_minor_locator(AutoMinorLocator(5))

    # Rotate tick labels
    plt.yticks(rotation=90)

    # Set math text to appear as regular text
    params = {'mathtext.default': 'regular'}
    plt.rcParams.update(params)

    # Set axis labels
    plt.xlabel('$log(T_{eff}/K)$')
    plt.ylabel('$log(L/L_{⊙})$')

    # Retrieve evolution track data
    track = sse.read_evolve_dat()
    x = track['log10(Teff)']
    y = track['log10(L)']

    # Plot on the HR-diagram
    plt.plot(x, y, color=line_color, lw=1)

    # Save to file
    plt.savefig('hrdiag.png')

    # Close the figure
    plt.close()
