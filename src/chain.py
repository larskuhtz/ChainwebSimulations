from simpy import Process, AllOf, Event
from simpy.resources.store import FilterStoreGet, StorePut

from . ctx import Ctx
from . block import Block
from . durations import pactDelay, latencyDelay
from . mine import Mine

class AwaitParents(Process):
    def __init__(self, env, graph, block : Block):
    
        def run():
            # No parents for the genesis block
            if block is None: 
                return []
    
            def f (b : Block):
                return b.height == block.height

            chainId = block.chainId
            edges = graph.vs[chainId].in_edges()

            # first check if all parents are already available
            parent_events = AllOf(env, [ FilterStoreGet(e["link"], f) for e in edges ])
            results = yield parent_events
            parents = list(results.values())
            return parents

# TODO
#             results = yield parent_events | Event(env).succeed('unblocked')
#             if not parent_events in results:
#                 # if not, wait for them
#                 # TODO mark chain as blocked
#                 results = yield AllOf(env, [ FilterStoreGet(e["link"], f) for e in edges ])
#                 # TODO unblock chain
#             parents = list(results.parent_events.values())
#             return parents
    
        super().__init__(env, run())

# asynchronously publish block to each adjacent chain
#
# TODO should this be a process or is it fine for it to be instantaneous?
#
class Publish:
    def __init__(self, ctx : Ctx, block : Block):
        self.ctx = ctx
        self.conf = ctx.conf
        self.env = ctx.env
        self.graph = ctx.conf.GRAPH
        self.block = block
        self.chain = block.chainId
        self.run()

    def run(self):
        for e in self.graph.vs[self.chain].out_edges():
            self.env.process(self.publishToChain(e))
        
    def publishToChain(self,e):
        yield self.env.timeout(latencyDelay(self.ctx))
        yield StorePut(e["link"], self.block)

class Chain:
    def __init__(self, ctx : Ctx, chain_id : int):

        self.chain = chain_id

        # Context
        self.ctx = ctx
        self.conf = ctx.conf
        self.env = ctx.env
        self.graph = ctx.graph
        self.da = ctx.da

        # State
        self.current_block = None

        # Monitors and Statistics
        self.is_blocked = False        
        self.cycle_times = []
        self.blocked_times = []
        self.new_block_times = []
        self.mine_times = []
        self.targets = []
        self.hash_power_factors = []

        # start chain process
        self.action = self.env.process(self.run())
        
    def run(self):
        while True:
            t0 = self.env.now

            # await parents for new block
            t1 = self.env.now
            self.is_blocked = True
            parents = yield AwaitParents(self.env, self.graph, self.current_block)
            self.is_blocked = False
            self.blocked_times.append(self.env.now - t1)

            # pact new block (TODO: do we call this here? There should
            # no reason to wait for *all* adjacents for calling new block)
            d = pactDelay(self.ctx)
            yield self.env.timeout(d)
            self.new_block_times.append(d)

            # mine
            t1 = self.env.now
            block = yield Mine(self.ctx, self.chain, self.current_block, parents)
            self.mine_times.append(self.env.now - t1)
            self.current_block = block
            self.targets.append(block.target)
                    
            # publish block asynchronously
            Publish(self.ctx, block)
                
            self.cycle_times.append(self.env.now - t0)