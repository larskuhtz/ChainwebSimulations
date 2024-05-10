from . import graphs
from . da import AvgDA

# FIXME: do not use class properties for configuration
#
class Config:
    """
    Simulation Configuration

    All durations are in seconds.
    """

    def __init__(self):
        """
        the da argument is a Class, not an object!
        """
        self.DA = AvgDA
    
        # targeted mean block time (per chain)
        self.MEAN_BLOCK_TIME = 30

        # number of blocks in an epoch
        self.EPOCH = 120

        # Median delay of pact new block call delay
        self.PACT_VALIDATION_TIME = 0.01
        self.PACT_NEW_BLOCK_TIME = self.PACT_VALIDATION_TIME

        # The mean latency for propagating a block in the network
        self.NETWORK_LATENCY = 0.5

        # overall block latencies (validation + network + validation, including pact validation)
        self.NUMBER_OF_MINING_NODES = 30
        self.LOCAL_BLOCK_LATENCY = 2 * self.PACT_VALIDATION_TIME
        self.REMOTE_BLOCK_LATENCY = 2 * self.PACT_VALIDATION_TIME + self.NETWORK_LATENCY
    
        self.GRAPH = graphs.Twenty

        # Seed for the PRNG
        self.RNG_SEED = 17
    
        # Difficulty Adjustement Parameters
        # (this is particularly relevant for the localDA algorithm)
        self.BLOCK_TIME_CHOICE = 0.9 # how close to the solve time the block time is chosen (0,1)
    
        # Support for multiple hash functions:
        self.NUMBER_OF_HASH_FUNCTIONS = 1
        self.MAX_TARGET_MULTIPLIER = 1

Default = Config()
