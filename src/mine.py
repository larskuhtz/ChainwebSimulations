from simpy import Process, Interrupt

from . config import Config
from . durations import miningDelay
from . block import Block
from . ctx import Ctx

def targetMultiplier(conf : Config, chainId : int) -> float:
    """
    The target multiplier can be used to simulate a situation where different
    chains receive different amounts of hash power or use different hash
    algorithms.
    """
    n = conf.NUMBER_OF_HASH_FUNCTIONS
    m = conf.MAX_TARGET_MULTIPLIER
    return (1 + (chainId % n)) * (m / n)

# Beside the static target multiplier, we also dynamically adjust the target
# based on the number of unblocked chains.

class Mine(Process):
    _counter = 0

    @classmethod
    def reset(cls):
        cls._counter = 0

    @classmethod
    def set(cls):
        cls._counter += 1
        return cls._counter
    
    @classmethod
    def unset(cls):
        cls._counter -= 1
        return cls._counter

    def __init__(self, ctx : Ctx, chainId : int, parent : Block, parents : list[Block]):
        
        self.ctx = ctx
        self.env = ctx.env
        self.conf = ctx.conf
        self.da = ctx.da

        self.parent = parent
        self.parents = parents
        self.chain_id = chainId
        self.target_multiplier = targetMultiplier(self.conf, chainId)

        self.chain = self.ctx.graph.vs[chainId]["chain"]

        super().__init__(self.env, self.run())

    def run(self):
        # adjust difficulty
        epoch_time, target = self.da.run(self.parent, self.parents)
        
        height = 0 if self.parent is None else self.parent.height + 1

        # mine
        # FIXME: update this each time the chain counter changes
        c = type(self).set()
        assert c > 0
        hash_power_factor = c / self.ctx.graph.vcount()

        solve_time = miningDelay(self.ctx, target * self.target_multiplier * hash_power_factor)
        new_time = self.env.now + solve_time * self.conf.BLOCK_TIME_CHOICE # current miner behavior: 0
        self.chain.hash_power_factors.append(hash_power_factor)
        yield self.env.timeout(solve_time)
        type(self).unset()

        # create new block
        block = Block(
                chainId = self.chain_id,
                height = height,
                time = new_time,
                epochTime = epoch_time,
                target = target
            )
        return block

# class Mine2(Process):
#     def __init__(self, ctx : Ctx, chainId : int, parent : Block, parents : list[Block]):
#         
#         self.ctx = ctx
#         self.env = ctx.env
#         self.conf = ctx.conf
#         self.da = ctx.da
# 
#         self.parent = parent
#         self.parents = parents
#         self.chain_id = chainId
#         self.target_multiplier = targetMultiplier(self.conf, chainId)
# 
#         self.chain = self.ctx.graph.vs[chainId]["chain"]
# 
#         super().__init__(self.env, self.run())
# 
#     def run(self):
#         # adjust difficulty
#         epoch_time, target = self.da.run(self.parent, self.parents)
#         
#         height = 0 if self.parent is None else self.parent.height + 1
# 
#         # mine
#         # FIXME: update this each time the chain counter changes
#         c = type(self).set()
# 
#         done = False
#         while not done:
#             c = type(self).get()
#             assert c > 0
#             hash_power_factor = c / self.ctx.graph.vcount()
# 
#             delay = target * self.target_multiplier * hash_power_factor
#             solve_time = miningDelay(self.ctx, delay)
#             new_time = self.env.now + solve_time * self.conf.BLOCK_TIME_CHOICE # current miner behavior: 0
#             self.chain.hash_power_factors.append(hash_power_factor)
# 
#             # can be interrupted
#             solved = self.env.timeout(solve_time) 
#             ret = yield solved | type(self).update
#             done = solved.processed
# 
#         type(self).unset()
# 
#         # create new block
#         block = Block(
#                 chainId = self.chain_id,
#                 height = height,
#                 time = new_time,
#                 epochTime = epoch_time,
#                 target = target
#             )
#         return block