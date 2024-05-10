from simpy.resources.store import FilterStore
from . chain import Chain

class Chainweb:

    def __init__(self, ctx):
        self.ctx = ctx
        
        self.graph = self.ctx.graph
        self.env = self.ctx.env
        self.da = self.ctx.da
        self.conf = self.ctx.conf

        for i in self.graph.es:
            i["link"] = FilterStore(self.env)

        for i in self.graph.vs:
            chain = Chain(self.ctx, i.index)
            i["chain"] = chain
        
        self.chains = self.graph.vs["chain"]