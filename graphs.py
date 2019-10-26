import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap, Normalize
import io
from datetime import timedelta
plt.switch_backend('Agg')

edge_syst = [40, 100, 120, 130, 140, 150, 160, 170, 220]
edge_diast = [40, 55, 80, 85, 90, 95, 100, 110, 120]
colors = ['#00FFFF', '#00FFFF', '#00FF00', '#FFFF00', '#FFFF00', '#FFA500', '#FFA500', '#FF0000', '#FF0000']


def get_cmap(high, low, edges, name):

    def get_edge(value):
        return (value - low)/(high - low)

    colors_cmap = []
    for n, edge in enumerate(edges):
        colors_cmap.append((get_edge(edge), colors[n]))
    cmap = LinearSegmentedColormap.from_list('{0}'.format(name), colors_cmap, N=729)
    return cmap


def paint_zones(x, y1, y2):

    zones = [0]*5

    edges = [[60, 90], [80, 120], [90, 140], [100, 160]]
    for i in range(len(x)):
        for n, (low, high) in enumerate(edges):
            if y2[i] <= low and y1[i] <= high:
                zones[n] += 1
                break
            else:
                continue
        else:
            zones[n + 1] += 1

    names = ['LOW', 'NORMAL', 'PRE \nHYPERTENSION', 'HIGH: \nSTAGE 1 \nHYPERTENSION', 'HIGH: \nSTAGE 2 \nHYPERTENSION']
    colors = ['#478bca', '#77bb66', '#f5e042', '#f9a648', '#f1444a']
    xmax = len(x)

    plt.figure(figsize=(12, 6))

    plt.subplot(121)
    d = 60
    x0 = [60, 80, 90, 100, 120]
    y0 = [(90 - d) / (220 - d), (120 - d) / (220 - d), (140 - d) / (220 - d), (160 - d) / (220 - d), 1]
    plt.scatter(y2, y1, c='k', s=5, zorder=2)
    plt.ylim(60, 220)
    plt.xlim(40, 120)
    for n, i in enumerate(colors):
        plt.axvspan(0, x0[n], 0.0, y0[n], facecolor=i, zorder=-1 - 2 * n)
        plt.axvspan(0, x0[n] + 0.96, 0.0, y0[n] + 0.008, facecolor='#FFFFFF', zorder=-1 - (2 * n + 1))

    plt.subplot(122)
    zones = [i * 100 / xmax for i in zones]
    plt.bar(names, zones, width=0.6, color=colors)

    return put_in_buffer()


def paint_general(x, y1, y2):

    plt.figure(figsize=(12, 6))

    # Plot lines
    plt.plot(x, y1, '#D3D3D3', zorder=1)
    plt.plot(x, y2, '#D3D3D3', zorder=1)

    # Systolic points
    one = plt.scatter(
        x, y1, c=y1, s=50,
        cmap=get_cmap(220, 40, edge_syst, 'one'),
        norm=Normalize(vmin=40, vmax=220),
        edgecolors='black', zorder=2
    )
    # Diastolic points
    two = plt.scatter(
        x, y2, c=y2, s=50,
        cmap=get_cmap(120, 40, edge_diast, 'two'),
        norm=Normalize(vmin=40, vmax=120),
        edgecolors='black', zorder=2
    )

    # Set two colorbar right
    cbar_1 = plt.colorbar(one)
    cbar_1.set_label("systolic edges")
    cbar_2 = plt.colorbar(two)
    cbar_2.set_label("diastolic edges")

    # Set axis limit
    plt.ylim(40, 220)
    plt.xlim(min(x).date(), (max(x) + timedelta(days=1)).date())

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator())
    plt.grid(True)
    plt.gcf().autofmt_xdate()

    return put_in_buffer()


def put_in_buffer():

    # Put graph in buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    return buffer
