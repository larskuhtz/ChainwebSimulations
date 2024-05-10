from . block import Block

def avg(a : list[float]) -> float:
    return sum(a) / len(a)

class ChainDA:
    """
    DA that does local adjustments based on a globally synchronized epoch.
    
    This is a legacy DA that was used on mainnet before the transition
    to the twenty chain graph.
    """
    def __init__(self, ctx):
        self.ctx = ctx
        self.env = self.ctx.env
        self.conf = self.ctx.conf
        
    def isEpochStart(self, parent : Block) -> bool:
        if parent is None:
            return True
        else:
            return (parent.height + 1) % self.conf.EPOCH == 0

    def run(self, parent : Block, parents : list[Block]) -> tuple[float, float]:
        return self.runChain(parent)
    
    def runChain(self, parent : Block):
        if parent is None:
            return self.env.now, self.conf.MEAN_BLOCK_TIME
        if self.isEpochStart(parent):
            epochTime = parent.time
            target = parent.target * (self.conf.MEAN_BLOCK_TIME * self.conf.EPOCH) / (parent.time - parent.epochTime)
        else:
            epochTime = parent.epochTime
            target = parent.target
        return epochTime, target

class AvgDA(ChainDA):
    """
    DA that is based on globally synchronized epoch. It performs
    chainDa and takes the average for the chain along with all it's
    adjacent chains.
    
    This is what is currently implemented on mainnet.
    """
    
    def __init__(self, env):
        super().__init__(env)

    def run(self, parent : Block, parents : list[Block]) -> tuple[float, float]:
        if parent is None:
            return self.runChain(parent)
        if self.isEpochStart(parent):
            ps = list(parents)
            ps.append(parent)
            epochTimes, targets = zip(*[self.runChain(p) for p in ps])
            epochTime = avg(epochTimes)
            target = avg(targets)
        else:
            epochTime = parent.epochTime
            target = parent.target
        return epochTime, target

  
class LocalDA(ChainDA):
    """
    A DA algorithm that adjusts difficutly on a per chain basis based on the
    solve time for that chain.
    """
    def __init__(self, env):
        super().__init__(env)

    def run(self, parent : Block, parents : list[Block]) -> tuple[float, float]:
        if parent is None:
            return self.runChain(parent)
        if self.isEpochStart(parent):
            return self.runChain(parent)
        
        ps = list(parents)
        ps.append(parent)
        penalty = avg([p.time for p in ps]) - parent.time # approximation of wait time
        epochTime = parent.epochTime + penalty
        target = parent.target
        return epochTime, target
