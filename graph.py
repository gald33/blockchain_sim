import matplotlib.pyplot as plt
import networkx as nx
import time
import globals
from pprint import pprint as pp


class Graph:
    def __init__(self):
        self.g = None
        self.nodes = None
        # self.edges = {}
        self.recent_pairwise_transmissions = None
        self.vertices = None
        self.layout = None
        self.color_map = []
        plt.subplot(111)

    def select_nodes(self, nodes, recent_pairwise_transmissions):
        self.nodes = nodes
        self.recent_pairwise_transmissions = recent_pairwise_transmissions
        # fix positions
        self.g = nx.Graph()
        self.vertices = {node.short_name: node for node in self.nodes}    # tie id to node
        self.g.add_nodes_from(self.vertices)
        self.layout = nx.random_layout(self.g)
        # now add labels with height
        # self.update_node_labels()

    def prepare_node_labels(self):
        # create graph with new labels and update position mapping to new labels
        self.g = nx.Graph()
        labels = {}
        for old_key in self.layout:
            key_id = old_key.split(':')[0]
            node = self.vertices[key_id]
            height = str(node.blockchain.block_to_append_to.height)
            new_key = key_id + ':' + height
            self.layout[new_key] = self.layout.pop(old_key)
            labels[new_key] = node
        self.g.add_nodes_from(labels)

    # def add_edge(self, sender, receiver):
    #     self.edges[(sender, receiver)] = sender.blockchain.block_to_append_to.color

    def prepare_edges_for_plot(self):
        for (sender, receiver) in self.recent_pairwise_transmissions:
            self.g.add_edge(sender.display_name, receiver.display_name,
                            color=self.recent_pairwise_transmissions[(sender, receiver)].color)

    def plot(self):
        pp(self.nodes)
        print(len(self.nodes))
        self.prepare_node_labels()
        self.prepare_edges_for_plot()
        node_colors = [node.blockchain.block_to_append_to.color for node in self.nodes]
        print(len(node_colors))
        pp(node_colors)
        edge_colors = [self.g[u][v]['color'] for u, v in self.g.edges]
        options = {
            'labels': None,
            # 'node_color': node_colors,
            'edge_color': edge_colors,
            'node_size': 300,
            'width': 3
        }
        nx.draw(self.g, self.layout, **options)
        plt.show()
        time.sleep(globals.DELAY_TIME)






