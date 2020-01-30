import random
import logging
from pprint import pprint as pp
import uuid
import hashlib

from blockchain import Blockchain
import globals


class Node:
    def __init__(self, node_type, initial_block_list, initial_known_nodes, transmission_time, tied_to_network):
        self.short_name = str(self)[-5:-1:1]
        self.display_name = None
        self.type = node_type
        self.known_nodes = initial_known_nodes
        self.blockchain = Blockchain(initial_block_list=initial_block_list)
        self.transmission_time = transmission_time
        self.available_to_transmit_at_time = 0
        self.network = tied_to_network  # should probably be deleted later
        self.update_desc()

    def update_desc(self):
        self.display_name = self.short_name + ':' + str(self.blockchain.block_to_append_to.height)

    def simulate_pow(self):
        block = self.blockchain.simulate_pow(creating_node=self)
        if block.is_valid():
            self.blockchain.add_block_to_tree(block)
            self.update_desc()
            self.network.process_creation(block=block, creator=self)
            # print(
            #     'node', self.short_name,
            #     'block', block.short_name,
            #     'height', block.height,
            #     'average', block.average_of_recent_ancestors / 1000 if block.average_of_recent_ancestors else 'N/A',
            #     'factor', block.adjustment_factor,
            #     'difficulty', block.difficulty,
            #     '*')
            if globals.PLOT_ON_CREATE:
                self.network.graph.plot()

    # def adjust_difficulty(self, recent_block):  # should be done with blockchain data instead for difficulty
    #     if recent_block.height > globals.MIN_LEN:
    #         num_of_blocks_for_adjustment = min(recent_block.height, globals.STABILIZATION_LEN)
    #         recent_block.register_difficulty(self.network.difficulty)
        #     logging.debug('network difficulty:' + str(self.network.difficulty))
        #     measured_time_for_block = float(recent_block.time - recent_block.last_block.last_block.last_block.last_block.time)/5
        #     logging.debug('time for block:' + str(int(float(measured_time_for_block)/1000)))
        #     logging.debug('time wanted:' + str(globals.BLOCK_TIME))
        #     ratio_delta = measured_time_for_block / globals.BLOCK_TIME - 1
        #     logging.debug('delta ratio:' + str(ratio_delta))
        #     factor = 1.0 / (1 + (0.1 * ratio_delta))   # stabilizing parameters go here
        #     logging.debug('factor:' + str(factor))
        #     self.network.difficulty = int(float(self.network.difficulty) * factor)
        #     logging.debug('new difficulty:' + str(self.network.difficulty))
        #     logging.debug('time for block:' + str(int(float(measured_time_for_block)/1000)) + ' sec, difficulty:' + str(self.network.difficulty))
            # input()

    def _receiver_policy(self):  # type strategy for choosing receivers
        if self.type == 'share':
            receiver = random.choice(self.known_nodes)
        elif self.type == 'hide':
            receiver = None
        else:
            receiver = None
            logging.critical('node type not recognized')

        return receiver     # if type is undefined it is as if type is hide

    def send_blocks_to_random_receiver(self): # send the block the node is working to append to, along with its ancestors
        # only send if available (not busy with previous transmission
        if self.available_to_transmit_at_time > globals.time:
            return
        block = self.blockchain.block_to_append_to
        receiver = self._receiver_policy()
        if receiver is None:
            logging.debug('time:' + str(int(globals.time/1000)) + ':' + self.short_name + ' attempts to send block ' +
                          block.display_name + ', does not send to anyone')
        elif block in receiver.blockchain.tree:
            logging.debug('time:' + str(int(globals.time/1000)) + ':' + self.short_name + ' attempts to send block ' +
                          block.display_name + ' to ' + receiver.short_name + ', but it knows it already')
        else:
            block_list = self.blockchain.prepare_block_list_to_send(block)
            # can allow for strategies in sending and\or receiving instead of the following
            receiver.receive_block(block_list)
            self.network.process_transmission(block=block, sender=self, receiver=receiver)
            # self.network.graph.add_edge(sender=self, receiver=receiver)

    def receive_block(self, block_list):
        self.blockchain.ordered_list_to_tree(block_list)
        self.update_desc()
        if globals.PLOT_ON_RECEIVE:
            self.network.graph.plot()