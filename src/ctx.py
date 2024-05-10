from numpy.random import default_rng, RandomState

class Ctx:
    def __init__(self, env, conf):
        self.env = env
        self.conf = conf
        self.graph = conf.GRAPH
        
        # Initialize DA object
        self.da = conf.DA(self)
        
        # PRNGs
        self.prng = default_rng(conf.RNG_SEED)
        self.prng_ = RandomState(conf.RNG_SEED) # scipy uses the legacy generator

