import networkx as nx
import matplotlib.pyplot as plt
import math
import permutation as perm

def draw_graph(x,i,filename):
    graph = nx.Graph()
    for p in x:
        if x[p] == 0:
            continue
        graph.add_node(p,present=x[p], inner=i[p])
        for n in perm.get_neighborhood(list(p)):
            if tuple(n) in x and x[tuple(n)] == 1:
                graph.add_edge(p, tuple(n))

    save_graph(graph, filename)


def save_graph(graph, file_name):
    #initialze Figure
    plt.figure(num=None, figsize=(100, 100), dpi=200)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.bfs_layout(graph,k=1/math.sqrt(graph.order()))
    color_map = []
    present = nx.get_node_attributes(graph, "present")
    inner = nx.get_node_attributes(graph, "inner")
    for node in graph:
        if present[node] and inner[node]:
            color_map.append('green')
        elif present[node]: 
            color_map.append('red')      
        else:
            color_map.append('blue')
    nx.draw(graph, pos, node_color=color_map, with_labels=True)
    # nx.draw_networkx_nodes(graph,pos, node_size=300)
    # colors = nx.get_edge_attributes(graph,'color').values()
    # widths = nx.get_edge_attributes(graph,'width').values()
    # nx.draw_networkx_edges(graph,pos)
    # nx.draw_networkx_labels(graph,pos)

    cut = 1.00
    eps = 0.2
    xmax = cut * max(xx for xx, yy in pos.values())+eps
    ymax = cut * max(yy for xx, yy in pos.values())+eps
    xmin = cut * min(xx for xx, yy in pos.values())-eps
    ymin = cut * min(yy for xx, yy in pos.values())-eps
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    plt.savefig(file_name,bbox_inches="tight")
    plt.close()
    del fig
