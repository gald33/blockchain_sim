import globals
from network import Network
from pprint import pprint as pp
import hashlib
import csv
import math
import logging
from datetime import datetime
import sys

logging.basicConfig(level=logging.INFO)
sys.setrecursionlimit(100000)

def run_network_simulation():
    summary = []
    num_of_sim_rounds = 10   # at least 3 to get multiple nodes
    num_of_nodes = int(math.pow(1.3, num_of_sim_rounds))
    for i in range(num_of_sim_rounds):
        num_of_hiders = int(math.pow(1.3, i))
        print('number of hider in simulation', num_of_hiders, 'of', num_of_nodes)
        network = Network(number_of_nodes=num_of_nodes, number_of_hiders=num_of_hiders)
        start_time = datetime.now()
        creations_log, transmissions_log = network.run()
        end_time = datetime.now()
        time_delta = end_time - start_time
        print('duration of simulation is:', time_delta)
        num_of_creations, average_creation_time, num_of_transmissions, average_transmission_time = \
            network.get_results()
        with open('creations_' + str(num_of_hiders) + '_of_' + str(num_of_nodes), mode='w') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(['time',
                             'block',
                             'height',
                             'node',
                             'difficulty',
                             'creation time'])
            height = 0
            for creation in creations_log:
                if creation.block.height > height:
                    height = creation.block.height
                creation_row = [int(creation.time / 1000),
                                creation.block.short_name,
                                creation.block.height,
                                creation.creator.short_name,
                                creation.block.difficulty if creation.block.difficulty else 'N/A',
                                creation.creation_time / 1000]
                writer.writerow(creation_row)
        with open('transmissions' + str(num_of_hiders) + '_of_' + str(num_of_nodes), mode='w') as output_file:
            writer = csv.writer(output_file)
            writer.writerow(['time',
                             'block',
                             'height',
                             'sender',
                             'receiver'])
            for transmission in transmissions_log:
                transmission_row = [int(transmission.time / 1000),
                                    transmission.block.short_name,
                                    transmission.block.height,
                                    transmission.sender.short_name,
                                    transmission.receiver.short_name]
                writer.writerow(transmission_row)

        summary.append([num_of_nodes,
                        num_of_hiders,
                        globals.ROUNDS,
                        time_delta,
                        num_of_creations,
                        average_creation_time,
                        int((creations_log[-1].time - creations_log[globals.CALIBRATION_BLOCKS].time) /
                            (len(creations_log) - globals.CALIBRATION_BLOCKS) / 1000),
                        num_of_transmissions,
                        (creations_log[-1].time / 1000) / len(transmissions_log)
                        if len(transmissions_log) != 0 else 'N/A',
                        height,
                        float(num_of_creations - height)/num_of_creations,
                        int(float(globals.ROUNDS * globals.TIME_RES) / height / 1000)])

    with open('summary' + str(datetime.now())[-6::], mode='w') as output_file:
        writer = csv.writer(output_file)
        writer.writerow(['num of nodes', 'num of hiders', 'sim time', 'real duration',
                        'num of creations', 'average creation time', 'calibrated average', 'num of transmissions',
                         'average transmission time', 'height', '%orphans', 'non-orphan time'])
        for item in summary:
            writer.writerow(item)


if __name__ == '__main__':
    run_network_simulation()


