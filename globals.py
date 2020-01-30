# application configuration variables

BLOCK_TIME = 60000
TRANSMISSION_TIME = 500
TIME_RES = 40  # jumps in time counter (used in network.run()) in ms
DELAY_TIME = 0  # sleep in seconds after a plot
PLOT_ON_CREATE = False
PLOT_ON_RECEIVE = False
ROUNDS = 2000000
CALIBRATION_BLOCKS = 50    # number of blocks to drop in summary for average creation time
STABILIZATION_LEN = 50
MIN_LEN = 50

# conditioned consts
initial_difficulty = int(BLOCK_TIME / TIME_RES)    # this value fits quick enough transmission (and/or few hiders)

# global variables

time = 0        # global time counter
