import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.gridspec import GridSpec
import numpy as np
import io
from datetime import timedelta
plt.switch_backend('Agg')

edge_syst = [40, 90, 120, 140, 160, 220]
edge_diast = [40, 60, 80, 90, 100, 110]
edge_difference = [10, 30, 40, 60, 70, 100]
colors = ['#478bca', '#478bca', '#77bb66', '#f5e042', '#f9a648', '#f1444a']
names_bar = [
    'LOW', 'NORMAL',
    'PRE \nHYPERTENSION',
    'HIGH: \nSTAGE 1 \nHYPERTENSION',
    'HIGH: \nSTAGE 2 \nHYPERTENSION'
]


def paint_zones(x, y1, y2, hand):

    # Initialize empty list
    zones = [0]*5
    # Get "real" zones
    edges = list(zip(edge_diast[1:], edge_syst[1:]))
    # Check hits into zones
    for i in range(len(x)):
        for n, (low, high) in enumerate(edges):
            if y2[i] <= low and y1[i] <= high:
                zones[n] += 1
                break
            else:
                continue
        else:
            zones[4] += 1

    x_max = len(x)

    fig = plt.figure(figsize=(19.20, 10.80), dpi=100)

    # Plot zones and points
    gs = GridSpec(1, 5, figure=fig, wspace=0.5)
    fig.add_subplot(gs[0, :-3])
    # Get color for current point
    point_colors = [(0, 0, 0, a / x_max) for a in range(1, x_max + 1)]
    plt.scatter(y2, y1, c=point_colors, s=200/(x_max**0.6), zorder=2, cmap='binary')
    plt.ylim(40, 220)
    plt.xlim(40, 110)
    for n, i in enumerate(colors[1:]):
        n = n + 1
        # Colored zone
        plt.axvspan(
            0, edge_diast[n], 0.0, (edge_syst[n] - 40)/(220 - 40),
            facecolor=i, zorder=-1 - 2 * n
        )
        # White zone
        plt.axvspan(
            0, edge_diast[n] + 0.96, 0.0, (edge_syst[n] - 40)/(220 - 40) + 0.008,
            facecolor='#FFFFFF', zorder=-1 - (2 * n + 1)
        )
    plt.ylabel('Systolic, mmHg')
    plt.xlabel('Diastolic, mmHg')
    plt.title('Distribution measurements by zones')

    # Plot percent
    fig.add_subplot(gs[0, -3:])
    plt.tick_params(labelsize=8)
    zones = [i * 100 / x_max for i in zones]
    plt.bar(names_bar, zones, width=0.6, color=colors[1:], edgecolor='k')
    for i, value in enumerate(zones):
        plt.text(i, value, f'{value:.2f}%', ha='center', color='k', fontweight='bold')
    plt.ylabel('Percent, %')
    plt.xlabel('Categories')
    plt.title('Distribution measurements by categories')

    return put_in_buffer()


def get_cmap(high, low, edges, name):

    def get_edge(value):
        return (value - low)/(high - low)

    colors_cmap = []
    for n, edge in enumerate(edges):
        colors_cmap.append((get_edge(edge), colors[n]))
    cmap = LinearSegmentedColormap.from_list('{0}'.format(name), colors_cmap, N=525)
    return cmap


def separate_plot(x, y, low, high, edges, name, c_reg='#fc34ff'):
    # Plot lines
    plt.plot(x, y, '#D3D3D3', zorder=0)
    # Points
    scat = plt.scatter(
        x, y, c=y, s=200/(len(x)**0.3),
        cmap=get_cmap(high, low, edges, name),
        norm=Normalize(vmin=low, vmax=high),
        edgecolors='black', zorder=2
    )
    # Set colorbar and label right
    cbar1 = plt.colorbar(scat)
    cbar1.set_label(name + ' edges')

    # Set axis limit
    plt.ylim(low, high)
    plt.xlim(min(x).date(), (max(x) + timedelta(days=1)).date())

    # Linear regression
    x = mdates.date2num(x)
    matrix = np.vstack([x, np.ones(len(x))]).T
    k, b = np.linalg.lstsq(matrix, y, rcond=1)[0]
    sign = '+' if b >= 0 else '-'
    avg_pressure = sum(y) / len(x)
    plt.plot(
        x, k * x + b, c_reg,
        zorder=1, linewidth=0.8,
        label=f'{k}x {sign} {abs(b)}\nAverage: {avg_pressure:.2f}'
    )

    # Labels
    plt.ylabel('Pressure, mmHg', style='italic', fontsize=14)
    plt.xlabel('Date', style='italic', fontsize=14)
    plt.title(f'{name} pressure', fontsize=16)

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.legend()


def paint_general(x, y1, y2, hand):

    fig = plt.figure(figsize=(19.20, 10.80), dpi=100)
    separate_plot(x, y2, 40, 110, edge_diast, "Diastolic")
    separate_plot(x, y1, 40, 220, edge_syst, "Systolic", c_reg='b')

    plt.title('Arterial pressure', fontsize=16)

    return put_in_buffer()


def detail_text(fig, x, y, difference):
    plt.text(
        x, y,
        'Difference between the right and left hand: {0:.2f}'.format(difference),
        ha='center', va='center',
        transform=fig.transFigure, style='italic',
        fontsize=16
    )


def paint_detail_graphs(*args):

    x, y1, y2, hand = [list(reversed(a)) for a in args]

    fig = plt.figure(figsize=(19.20, 19.20), dpi=100)
    fig.suptitle("Pressure on the left and right hand", fontsize=24)
    gs = GridSpec(3, 2, figure=fig, hspace=0.5)

    data = {i: {'l': [], 'r': []} for i in ['x', 'y1', 'y2']}

    while hand:
        h = hand.pop()
        data['x'][h].append(x.pop())
        data['y1'][h].append(y1.pop())
        data['y2'][h].append(y2.pop())

    diff = {'r': [], 'l': []}

    for n, h in enumerate(['l', 'r']):
        fig.add_subplot(gs[0, n])
        separate_plot(data['x'][h], data['y1'][h], 40, 220, edge_syst, "Systolic")
        fig.add_subplot(gs[1, n])
        separate_plot(data['x'][h], data['y2'][h], 40, 110, edge_diast, "Diastolic")
        fig.add_subplot(gs[2, n])
        diff[h] = list(map(lambda z: z[0] - z[1], zip(data['y1'][h], data['y2'][h])))
        separate_plot(
            data['x'][h], diff[h],
            10, 100, edge_difference, "Difference"
        )

    def difference(right, left):
        return abs((sum(right)/len(right)) - (sum(left)/len(left)))

    detail_text(fig, 0.5, 0.91, difference(data['y1']['r'], data['y1']['l']))
    detail_text(fig, 0.5, 0.655, difference(data['y2']['r'], data['y2']['l']))
    detail_text(fig, 0.5, 0.4, difference(diff['r'], diff['l']))

    return put_in_buffer()


def put_in_buffer():
    """Put image in byte format on buffer"""

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', quality=100)
    buffer.seek(0)
    plt.close()

    return buffer
