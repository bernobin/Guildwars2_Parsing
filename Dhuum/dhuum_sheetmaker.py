import struct
import matplotlib.pyplot as plt

from parser import Parser

dhuum_parser = Parser()
agents, skills, events = dhuum_parser.get_ase("20231106-204156")
trails = dhuum_parser.get_agent_trails("20231106-204156")

def plot(trails, addr):
    locations = trails[addr]['locations']
    times = trails[addr]['times']

    x_coords = [i for (i, _, _) in locations]
    y_coords = [i for (_, i, _) in locations]
    z_coords = [i for (_, _, i) in locations]

    fig, ax = plt.subplots()

    ax.scatter(x_coords[1:], y_coords[1:], c=z_coords[1:])
    ax.axis('equal')

    plt.show()

plot(trails, 2000)