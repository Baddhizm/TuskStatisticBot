import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.gridspec import GridSpec
import io
from datetime import timedelta
plt.switch_backend('Agg')

edge_syst = [90, 120, 140, 160, 220]
edge_diast = [60, 80, 90, 100, 110]
colors = ['#478bca', '#77bb66', '#f5e042', '#f9a648', '#f1444a']
names_bar = [
    'LOW', 'NORMAL',
    'PRE \nHYPERTENSION',
    'HIGH: \nSTAGE 1 \nHYPERTENSION',
    'HIGH: \nSTAGE 2 \nHYPERTENSION'
]


def paint_zones(x, y1, y2):

    zones = [0]*5
    edges = list(zip(edge_diast, edge_syst))
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

    fig = plt.figure(figsize=(12, 6))

    gs = GridSpec(1, 5, figure=fig, wspace=0.5)
    fig.add_subplot(gs[0, :-3])
    plt.scatter(y2, y1, c='k', s=5, zorder=2)
    plt.ylim(40, 220)
    plt.xlim(40, 110)
    for n, i in enumerate(colors):
        # colored zone
        plt.axvspan(
            0, edge_diast[n], 0.0, (edge_syst[n] - 40)/(220 - 40),
            facecolor=i, zorder=-1 - 2 * n
        )
        # white zone
        plt.axvspan(
            0, edge_diast[n] + 0.96, 0.0, (edge_syst[n] - 40)/(220 - 40) + 0.008,
            facecolor='#FFFFFF', zorder=-1 - (2 * n + 1)
        )

    fig.add_subplot(gs[0, -3:])
    plt.tick_params(labelsize=8)
    zones = [i * 100 / x_max for i in zones]
    plt.bar(names_bar, zones, width=0.6, color=colors, edgecolor='k')

    return put_in_buffer()


def get_cmap(high, low, edges, name):

    def get_edge(value):
        return (value - low)/(high - low)

    colors_cmap = []
    for n, edge in enumerate(edges):
        colors_cmap.append((get_edge(edge), colors[n]))
    cmap = LinearSegmentedColormap.from_list('{0}'.format(name), colors_cmap, N=525)
    return cmap


def separate_plot(x, y, low, high, edges, name):
    # Plot lines
    plt.plot(x, y, '#D3D3D3', zorder=1)
    # points
    scat = plt.scatter(
        x, y, c=y, s=100,
        cmap=get_cmap(high, low, edges, name),
        norm=Normalize(vmin=low, vmax=high),
        edgecolors='black', zorder=2
    )
    # Set colorbar and label right
    cbar1 = plt.colorbar(scat)
    cbar1.set_label(name)


def paint_general(x, y1, y2):

    plt.figure(figsize=(12, 6))
    separate_plot(x, y1, 90, 220, edge_syst, "systolic edges")
    separate_plot(x, y2, 60, 110, edge_diast, "diastolic edges")

    # Set axis limit
    plt.ylim(40, 220)
    plt.xlim(min(x).date(), (max(x) + timedelta(days=1)).date())

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.grid(True)
    plt.gcf().autofmt_xdate()

    return put_in_buffer()


def put_in_buffer():
    """Put image in byte format on buffer"""

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return buffer
