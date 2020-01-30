import random
import uuid
import copy
import graph
import logging
from pprint import pprint as pp

from blockchain import Block
from node import Node
import globals


class Network:
    def __init__(self, number_of_nodes, number_of_hiders):
        # initialize nodes
        self.number_of_nodes = number_of_nodes
        self.number_of_hiders = number_of_hiders
        self.nodes = []
        genesis_block = self.generate_genesis_block()
        initial_block_list = [genesis_block]
        self.create_nodes(initial_block_list)


        # logs
        self.creations_log = []
        self.transmissions_log = []
        self.recent_pairwise_transmissions = {}     # used to draw edges

        # plots
        self.graph = graph.Graph()
        self.graph.select_nodes(self.nodes, self.recent_pairwise_transmissions)





    def create_nodes(self, block_list):
        # add nodes
        for i in range(self.number_of_nodes):
            if i < self.number_of_hiders:
                node = Node(
                    node_type='hide',
                    initial_block_list=block_list,
                    initial_known_nodes=self.nodes,  # network is always fully connected
                    transmission_time=globals.TRANSMISSION_TIME,
                    tied_to_network=self)
            else:   # all the rest are type share
                node = Node(
                    node_type='share',
                    initial_block_list=block_list,
                    initial_known_nodes=self.nodes,  # network is always fully connected
                    transmission_time=globals.TRANSMISSION_TIME,
                    tied_to_network=self)
            self.nodes.append(node)
        # add nodes to the graph

    @staticmethod
    def generate_genesis_block():
        genesis_block = Block(
            nonce=uuid.uuid4().hex,
            last_block=None,
            content_hash=None,
            creating_node=None)
        return genesis_block

    def run(self):
        globals.time = 0
        try:
            while True:
                globals.time += globals.TIME_RES
                node = random.choice(self.nodes)
                node.simulate_pow()
                node = random.choice(self.nodes)
                node.send_blocks_to_random_receiver()
                if globals.time >= globals.ROUNDS * globals.TIME_RES:
                    break
        except KeyboardInterrupt:
            pass
        return self.creations_log, self.transmissions_log

    def process_transmission(self, block, sender, receiver):
        self._add_recent_pairwise_transmission(block, sender, receiver)
        self._log_transmission(block, sender, receiver)
        logging.debug('<receive> block:' + block.display_name + ', time:' + str(int(globals.time / 1000)) + ', node:'
                      + receiver.short_name + ', sender: ' + sender.short_name)  # time presented in sec

    def process_creation(self, block, creator):
        self._log_creation(block, creator)
        logging.debug('<create> block:' + block.display_name + ', time:' + str(int(globals.time / 1000)) + ', node:'
                      + creator.short_name)  # time presented in sec

    def _add_recent_pairwise_transmission(self, block, sender, receiver):
        self.recent_pairwise_transmissions[(sender, receiver)] = block

    def _log_transmission(self, block, sender, receiver):
        transmission = Transmission(block, sender, receiver)
        self.transmissions_log.append(transmission)

    def _log_creation(self, block, creator):
        if self.creations_log:  # if list is empty
            creation = Creation(block, creator, self.creations_log[-1])
        else:
            creation = Creation(block, creator, None)
        self.creations_log.append(creation)

    def get_results(self):
        print('simulation time:', globals.time)
        if self.creations_log:
            average_creation_time = (float(globals.time) / 1000) / len(self.creations_log)
            print(len(self.creations_log), 'creations with average creation time is sec:', average_creation_time)
        else:
            average_creation_time = None
            print('no blocks')
            pp(self.creations_log)
        if self.transmissions_log:
            average_transmission_time = (float(globals.time) / 1000) / len(self.transmissions_log)
            print(len(self.transmissions_log), 'transmissions with average transmission time is sec:', average_transmission_time)
        else:
            average_transmission_time = None
            print('no transmissions')
            pp(self.transmissions_log)
        return len(self.creations_log), average_creation_time, len(self.transmissions_log), average_transmission_time


class LogItem:
    def __init__(self, block):
        self.time = copy.copy(globals.time)     # time in ms
        self.block = block


class Transmission(LogItem):
    def __init__(self, block, sender, receiver):
        super(Transmission, self).__init__(block)
        self.sender = sender
        self.receiver = receiver


class Creation(LogItem):
    def __init__(self, block, creator, last_creation):
        super(Creation, self).__init__(block)
        self.creator = creator
        self.creation_time = copy.copy(self.time)
        if last_creation:
            self.creation_time -= last_creation.time
        logging.debug('time:', self.time/1000, 'last time:', last_creation.time/1000 if last_creation else 'N/A',
                      'creation_time:', self.creation_time/1000, '***')