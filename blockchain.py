import logging
import uuid
import hashlib
import random
from pprint import pprint as pp
import copy
import math


import globals


class Blockchain:
    def __init__(self, initial_block_list):
        self.list = initial_block_list
        self.tree = {}
        self.genesis_block = None
        self.block_to_append_to = None

        self.ordered_list_to_tree(self.list)

    def ordered_list_to_tree(self, block_list):     # blocks in list are after their parent blocks
        for block in block_list:
            if not self.genesis_block and block.height == 0:    # move some of this case statements to the relevant methods
                self.genesis_block = block
                self.tree[block] = []   # tree contains the edges from node to its children
                self.block_to_append_to = self.genesis_block
                logging.debug('block ' + str(self.block_to_append_to) + ' is now the block to append to in blockchain ' +
                   str(self) + ' at height ' + str(self.block_to_append_to.height))
                logging.debug('added genesis block ' + str(block))
            elif block.last_block:
                self.add_block_to_tree(block)
                logging.debug('added block ' + str(block))
            else:
                logging.debug('did not add block ' + str(block))

    def find_block_in_tree(self, target_block, subtree_root):   # is currently not used
        logging.debug('searching for block ' + str(target_block) + ' in subtree of ' + str(subtree_root))
        for block in self.tree[subtree_root]:
            if block == target_block:
                return block
            else:
                self.find_block_in_tree(target_block, block)
            # otherwise return None

    def update_block_to_append_to(self):
        for block in self.tree:
            if block.height > self.block_to_append_to.height:
                self.block_to_append_to = block
                logging.debug('time:' + str(int(globals.time/1000)) + ':block ' + str(self.block_to_append_to)[-5: -1: 1] + ' is now the block to append to in blockchain ' +
                              str(self)[-5: -1: 1] + ' at height ' + str(self.block_to_append_to.height))

    def add_block_to_tree(self, block):
        if block not in self.tree: # make sure not to replace known branches
            self.tree[block.last_block].append(block)
            self.tree[block] = []
            self.update_block_to_append_to()

    def simulate_pow(self, creating_node):  # create random block
        nonce = uuid.uuid4().hex
        content_hash = uuid.uuid4().hex
        block = Block(nonce, content_hash, self.block_to_append_to, creating_node)
        return block

    def prepare_block_list_to_send(self, block):
        block_list = []
        self.collect_chain(block, block_list)
        return reversed(block_list)

    def collect_chain(self, block, block_list): # add blocks to list recursuvely from last_blocks
        block_list.append(block)
        if block.last_block:
            self.collect_chain(block.last_block, block_list)


class Block:
    def __init__(self, nonce, content_hash, last_block, creating_node):
        self.nonce = nonce
        self.content_hash = content_hash
        self.last_block = last_block
        self.node = creating_node
        if self.last_block is None:
            self.height = 0     # for genesis block

        else:
            self.height = self.last_block.height + 1
        self.time = copy.copy(globals.time)

        # stats
        self.average_of_recent_ancestors = None
        self.adjustment_factor = None

        # for network adjustment
        self.difficulty = self._set_difficulty()    # difficulty when appending to this block

        # style
        # self.short_name = str(self)[-5: -1: 1]
        self.short_name = str(uuid.uuid4())[-4::]
        # self.color = '#' + str(hex(random.randint(0, pow(16, 6))))[2::]
        self.color = (random.random(), random.random(), random.random())
        self.display_name = None
        self.update_desc()

    def _set_difficulty(self):  # should be done with blockchain data instead for difficulty
        if self.height > globals.MIN_LEN:
            num_of_blocks_for_adjustment = min(self.height, globals.STABILIZATION_LEN)
            goal_height = self.last_block.height - num_of_blocks_for_adjustment
            ancestor_time = self.ancestor_time(goal_height)
            average = (self.last_block.time - ancestor_time) / num_of_blocks_for_adjustment
            factor = math.pow(average / globals.BLOCK_TIME, 1/20)
            difficulty = int(self.last_block.difficulty / factor)
            # print(
            #     'height', self.height,
            #     'goal height', goal_height,
            #     'ancestor time', ancestor_time/1000,
            #     'time', self.time/1000,
            #     'average', average/1000,
            #     'block time', globals.BLOCK_TIME/1000,
            #     'pre_factor', average / globals.BLOCK_TIME,
            #     'factor', factor,
            #     'last block difficulty', self.last_block.difficulty,
            #     'difficulty', difficulty,
            #     '*')
            # input('PPP')
            self.average_of_recent_ancestors = average
            self.adjustment_factor = factor
            return difficulty
        else:
            # print(
            #     'height', self.height,
            #     'time', self.time,
            #     'block time', globals.BLOCK_TIME,
            #     '*')
            # input('PPP')
            return globals.initial_difficulty

    def ancestor_time(self, goal_height):  #return the ancestor of a block at a given height
        if self.height == goal_height:
            return self.time
        elif self.height > goal_height:
            return self.last_block.ancestor_time(goal_height)
        else:
            logging.critical('Something wrong with the difficulty adjustment')

    def register_difficulty(self, difficulty):  # should be based on the blockchain later
        self.difficulty = difficulty

    def update_desc(self):
        self.display_name = self.short_name + ':' + str(self.height)

    def hash_of_block(self):
        val = str(self.nonce)
        if self.last_block:
            val += str(self.last_block)
        if self.content_hash:
            val += str(self.content_hash)
        if self.node:
            val += str(self.node)
        hash_val = '0x' + hashlib.md5(val.encode('ascii')).hexdigest()
        return hash_val

    # checks if the
    # genesis block is by definition invalid as it has no last block to point to
    def is_valid(self):
        if self.last_block:
            difficulty = self.difficulty if self.difficulty >=1 else 1 # difficulty is based on the block appending to
            # later the difficulty should be derived from the instance of blockchain./.
            logging.debug('difficulty:' + str(difficulty) + ', ' + str(int(self.hash_of_block(), 16) % difficulty) + ' ' +
                          str(int(hashlib.md5(str(id(self.last_block)).encode('ascii')).hexdigest(), 16)
                              % difficulty))
            if int(self.hash_of_block(), 16) % difficulty == \
                    int(hashlib.md5(str(id(self.last_block)).encode('ascii')).hexdigest(), 16) % difficulty:
                return True
            return False
