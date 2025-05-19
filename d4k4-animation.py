import src.graphs as graphs
import networkx as nx
import argparse

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation

# plt.rcParams["figure.figsize"] = [10,10]

n = graphs.D4K4.as_undirected().simplify(loops=True).to_networkx()
l = nx.spectral_layout(n, center=(0,0), scale=10)

plt.rcParams["figure.figsize"] = [10, 10]
pos = { k: [x, y, (k % 2) * 0.2] for k,[x,y] in l.items() }
nodes = np.array([pos[v] for v in n])
edges = np.array([(pos[u], pos[v]) for u, v in n.edges()])

fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")

def init():
    for vizedge in edges:
        ax.plot(
            *vizedge.T,
            alpha=1,
            color="lightgray",
            linewidth=0.6,
            zorder=1,
        )
    ax.scatter(
        *nodes.T,
        alpha=1,
        s=80,
        color=['orange' if i < 20 else 'green' if i < 40 else 'lightblue' for i in n.nodes()],
        zorder=2,
    )
    ax.grid(False)
    ax.set_axis_off()
    # for dim in (ax.xaxis, ax.yaxis, ax.zaxis):
    #     dim.set_ticks([])
    ax.view_init(45, 45)
    ax.set_zlim(-1, 1)
    plt.tight_layout()
    return

def _frame_update(index):
    # ax.view_init(index * 0.2, index * 0.5)
    ax.view_init(index * 0.1, index * 0.25)
    return

# ############################################################################ #
# Main

parser=argparse.ArgumentParser()
parser.add_argument("--mp4-file")
parser.add_argument("--interval", default=100)
parser.add_argument("--frames", default=2000)
parser.add_argument("--fps", default=40)
args=parser.parse_args()

ani = animation.FuncAnimation(
    fig,
    _frame_update,
    init_func=init,
    interval=args.interval,
    # cache_frame_data=False,
    frames=args.frames,
)

if args.mp4_file is not None:
    FFwriter = animation.FFMpegWriter(fps=args.fps)
    ani.save(args.mp4_file, writer = FFwriter)

else:
    plt.show()