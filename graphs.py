import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.gridspec import GridSpec
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


def paint_zones(x, y1, y2):

    zones = [0]*5
    edges = list(zip(edge_diast[1:], edge_syst[1:]))
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
    point_colors = [(0, 0, 0, a / x_max) for a in range(1, x_max + 1)]
    plt.scatter(y2, y1, c=point_colors, s=200/(x_max**0.6), zorder=2, cmap='binary')
    plt.ylim(40, 220)
    plt.xlim(40, 110)
    for n, i in enumerate(colors[1:]):
        n = n + 1
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
    plt.bar(names_bar, zones, width=0.6, color=colors[1:], edgecolor='k')

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
        x, y, c=y, s=200/(len(x)**0.3),
        cmap=get_cmap(high, low, edges, name),
        norm=Normalize(vmin=low, vmax=high),
        edgecolors='black', zorder=2
    )
    # Set colorbar and label right
    cbar1 = plt.colorbar(scat)
    cbar1.set_label(name)

    # Set axis limit
    plt.ylim(low, high)
    plt.xlim(min(x).date(), (max(x) + timedelta(days=1)).date())

    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.grid(True)
    plt.gcf().autofmt_xdate()


def paint_general(x, y1, y2):

    plt.figure(figsize=(12, 6))
    separate_plot(x, y2, 40, 110, edge_diast, "diastolic edges")
    separate_plot(x, y1, 40, 220, edge_syst, "systolic edges")

    return put_in_buffer()


def paint_detail_graphs(x, y1, y2):

    fig = plt.figure(figsize=(9, 16), dpi=160)
    gs = GridSpec(3, 1, figure=fig, hspace=0.5)
    fig.add_subplot(gs[0, 0])
    separate_plot(x, y1, 40, 220, edge_syst, "systolic edges")
    fig.add_subplot(gs[1, 0])
    separate_plot(x, y2, 40, 110, edge_diast, "diastolic edges")
    fig.add_subplot(gs[2, 0])
    separate_plot(
        x, list(map(lambda z: z[0] - z[1], zip(y1, y2))),
        10, 100, edge_difference, "difference edges"
    )

    return put_in_buffer()


def put_in_buffer():
    """Put image in byte format on buffer"""

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', quality=100)
    buffer.seek(0)
    plt.close()

    return buffer
