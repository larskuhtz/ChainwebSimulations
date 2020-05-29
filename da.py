import igraph

from simpy import *
from simpy.events import AnyOf, AllOf, Event
from simpy.resources.store import *

import math

import numpy as np
from numpy.random import default_rng, RandomState

from scipy.stats import fisk # log-logistic distribution

# plot
import matplotlib.pyplot as plt

# Model
#
# The chain graph is encoded as a directed graph that is symmmetric and reflexive.
#
# Each node in graph represents a chain process and each edge represents
# a network link between chains through which newly mined blocks are
# published to adjancent chains.
#

# ############################################################################ #
# Configuration

RNG_SEED = 17
MEAN_BLOCK_TIME = 30
EPOCH = 120

# block latencies (validation + network + validation + new block)
MEDIAN_LOCAL_BLOCK_LATENCY = 0.1
MEDIAN_REMOTE_BLOCK_LATENCY = 1
SD_BLOCK_LATENCY_FACTOR = 1
MEAN_PACT_DELAY = 0.1

# Initialize random number generator
prng = default_rng(RNG_SEED)
prng_ = RandomState(RNG_SEED) # scipy uses the legacy generator

# ############################################################################ #
# Graphs

def peterson():
    graph = igraph.Graph(directed=True)
    graph.add_vertices(10)
    graph.add_edges(
        [ (0, 0), (0, 2), (0, 3), (0, 5)
        , (1, 1), (1, 3), (1, 4), (1, 6)
        , (2, 2), (2, 0), (2, 4), (2, 7)
        , (3, 3), (3, 0), (3, 1), (3, 8)
        , (4, 4), (4, 1), (4, 2), (4, 9)
        , (5, 5), (5, 0), (5, 6), (5, 9)
        , (6, 6), (6, 1), (6, 5), (6, 7)
        , (7, 7), (7, 2), (7, 6), (7, 8)
        , (8, 8), (8, 3), (8, 7), (8, 9)
        , (9, 9), (9, 4), (9, 5), (9, 8)
        ]
    )
    return(graph)

def twenty():
    graph = igraph.Graph(directed=True)
    graph.add_vertices(20)
    graph.add_edges(
        [ (0, 0), (0, 10), (0,15), (0,5)
        , (1, 1), (1, 11), (1,16), (1,6)
        , (2, 2), (2, 12), (2,17), (2,7)
        , (3, 3), (3, 13), (3,18), (3,8)
        , (4, 4), (4, 14), (4,19), (4,9)
        , (5, 5), (5, 0), (5,7), (5,8)
        , (6, 6), (6, 1), (6,8), (6,9)
        , (7, 7), (7, 2), (7,5), (7,9)
        , (8, 8), (8, 3), (8,5), (8,6)
        , (9, 9), (9, 4), (9,6), (9,7)
        , (10, 10), (10, 0), (10,11), (10,19)
        , (11, 11), (11, 1), (11,10), (11,12)
        , (12, 12), (12, 11), (12,13), (12,2)
        , (13, 13), (13, 12), (13,14), (13,3)
        , (14, 14), (14, 13), (14,15), (14,4)
        , (15, 15), (15, 0), (15,14), (15,16)
        , (16, 16), (16, 1), (16,15), (16,17)
        , (17, 17), (17, 16), (17,18), (17,2)
        , (18, 18), (18, 17), (18,19), (18,3)
        , (19, 19), (19, 10), (19,18), (19,4)
        ]
    )
    return (graph)

# ############################################################################ #
# Quick and Dirty Linear Histogram

# TODO: there are probably some good libraries with support for this
#
class Histogram:

    def __init__(self, binSize):
        self.bins = {}
        self.binSize = binSize

    def sample(self, x):
        i = math.floor(x / self.binSize)
        if i in self.bins:
            self.bins[i] += 1
        else:
            self.bins[i] = 1

    def append(self, h):
        if h.binSize == self.binSize:
            for i in h.bins:
                if i in self.bins:
                    self.bins[i] += h.bins[i]
                else:
                    self.bins[i] = h.bins[i]
        else:
            throw("merging histograms with different bin sizes isn't yet implemented")

    def result(self):
        imin = min(self.bins.keys())
        imax = max(self.bins.keys())
        a = [0] * (imax - imin + 1)
        b = [self.binSize * k for k in range(imin, imax + 1)]
        for i in range(imin, imax + 1):
            if i in self.bins:
                a[i - imin] = self.bins[i]
        return a, b

# TODO: implement more general WithStatistics class
class HistogramSample:
    def __init__(self, histogram, clock):
        self.histogram = histogram
        self.clock = clock
    def __enter__(self):
        self.start = self.clock.now
        return self.start
    def __exit__(self, type, value, traceback):
        self.histogram.sample(self.clock.now - self.start)
        return None # rethrow

# ############################################################################ #
# Model

# We use the log-logistic distribution with shape parameter 8 to model latencies.
#
def latencyDelay(graph, edge):
    median = MEDIAN_LOCAL_BLOCK_LATENCY if edge.target == edge.source else MEDIAN_REMOTE_BLOCK_LATENCY

    # It seems that fisk.median(c=c, loc=a) == a+1, for all c
    return fisk.rvs(c=8, loc=max(0,median - 1), random_state=prng_)

def pactDelay():
    # It seems that fisk.median(c=c, loc=a) == a+1, for all c
    return fisk.rvs(c=8, loc=max(0,MEAN_PACT_DELAY - 1), random_state=prng_)

# A single Block
#
class Block:
    def __init__(self, chainId : int, height : int, time : float, epochTime : float, target : float):
        self.chainId = chainId
        self.height = height
        self.time = time

        # For Da
        self.epochTime = epochTime
        self.target = target

        def __lt__(self, other):
            self.height < other.height

# Chain Process
#
class Chain:
    def __init__(self, env : Environment, chainId : int, graph, logTags : [str] = []):
        # Config
        self.logTags = logTags

        # Context
        self.env = env
        self.graph = graph
        self.chain = chainId

        # State
        self.currentBlock = None

        # Monitors and Statistics
        self.isBlocked = False
        self.blockedTime = 0
        self.blockedHist = Histogram(1)
        self.cycleHist = Histogram(1)
        self.miningHist = Histogram(1)

        # start chain process
        self.action = env.process(self.run())

    # #################################### #
    # Main Loop

    def run(self):
        t=None
        while True:
            with HistogramSample(self.cycleHist, self.env):

                # await parents for new block
                if self.currentBlock:
                    self.logg("net", "await parents at height %d" % self.currentBlock.height)
                with HistogramSample(self.blockedHist, self.env):
                    t0 = self.env.now
                    self.isBlocked = True
                    parents = yield self.env.process(self.awaitParents())
                    self.isBlocked = False
                    self.blockedTime += self.env.now - t0

                # pact new block (TODO: do we call this here? There should
                # no reason to wait for *all* adjacents for calling new block)
                yield self.env.timeout(pactDelay())

                # mine
                if self.currentBlock:
                    self.logg("mine", "mine and publish block at height %d" % self.currentBlock.height)
                with HistogramSample(self.miningHist, self.env):
                    block = yield self.env.process(self.mineBlock(parents))

                # publish block asynchronously
                self.publishBlock(block)

    # #################################### #
    # Produce blocks

    def awaitParents(self):
        # No parents for the genesis block
        if self.currentBlock == None: return []
        h = self.currentBlock.height
        edges = self.graph.vs[self.chain].in_edges()
        f = lambda b: b.height == h
        results = yield AllOf(self.env, [ FilterStoreGet(e["link"], f) for e in edges ])
        parents = list(results.values())
        assert all(h == b.height for b in parents), ("[chain %d] not all parents have height %d: " % (self.chain, h)) + str([ (b.chainId, b.height) for b in parents])
        self.logg("await", "got all parents at height %d" % h)
        return parents

    def mineBlock(self, parents):

        parent = self.currentBlock

        # adjust difficulty
        epochTime, target = self.chainDa(parent)
        # epochTime, target = self.avgDa(parent, parents)
        height = 0 if parent == None else parent.height + 1

        # mine
        newTime = self.env.now # current behavior
        solveTime = prng.exponential(target)
        self.logg("mine", "start mining with solve time %f" % solveTime)
        yield self.env.timeout(solveTime)

        # create new block
        # newTime = self.env.now # proposed behavior
        block = Block(
                chainId = self.chain,
                height = height,
                time = newTime,
                epochTime = epochTime,
                target = target
            )
        self.logg("mine", 'created block %i with t=%f' % (block.height, block.time))
        self.currentBlock = block
        return block

    # asynchronously publish block to each adjacent chain
    def publishBlock(self, block):
        def publishToChain(e):
            self.logg("net", "publish height %i to %i" % (block.height, e.tuple[1]))

            # apply latency delay
            yield self.env.timeout(latencyDelay(self.graph, e))

            # Make block available for use on target chain
            yield StorePut(e["link"], block)

        for e in self.graph.vs[self.chain].out_edges():
            self.env.process(publishToChain(e))

    # #################################### #
    # DA

    # DA that does local adjustments based on a globally
    # synchronized epoch.
    #
    # This is what is currently implemented on mainnet.
    #
    def chainDa(self, parent):
        if parent == None:
            return self.env.now, MEAN_BLOCK_TIME
        if (parent.height + 1) % EPOCH == 0:
            epochTime = parent.time
            target = parent.target * (MEAN_BLOCK_TIME * EPOCH) / (parent.time - parent.epochTime)
            self.logg("da", "adjusted target from %f to %f" % (parent.target, target))
        else:
            epochTime = parent.epochTime
            target = parent.target
        return epochTime, target

    # DA that is based on globally synchronized epoch. It performs
    # chainDa and takes the average for the chain along with all it's
    # adjacent chains.
    #
    def avgDa(self, parent, parents):
        def avg(a): return sum(a) / len(a)

        if parent == None:
            return self.env.now, MEAN_BLOCK_TIME
        parents.append(parent)
        epochTimes, targets = zip(*[self.chainDa(p) for p in parents])
        epochTime = avg(epochTimes)
        target = avg(targets)
        self.logg("da", "adjusted target from %f to %f" % (parent.target, target))
        return epochTime, target

    # #################################### #
    # Utils

    def getChain(self, vertexId):
        return self.graph.vs[vertexId]["chain"]

    def logg(self, tag, msg):
        if tag in self.logTags:
            print("[%d][chain %i] %s" % (self.env.now, self.chain, msg))

# A Chainweb that runs a chain process for each vertex in the graph
#
class Chainweb:

    def __init__(self, env, graph, logTags = []):
        self.graph = graph
        self.env = env

        for i in self.graph.es:
            i["link"] = FilterStore(env)

        for i in self.graph.vs:
            print("chain %d" % i.index)
            chain = Chain(env, i.index, self.graph, logTags)
            i["chain"] = chain

# ############################################################################ #
# Report results

# Monitor the value of variables at fixed intervals
#
def monitor(env : Environment, chainweb : Chainweb, n : int):
    while True:
        yield env.timeout(n)
        blocked = [ i.isBlocked for i in chainweb.graph.vs["chain"] ]
        print("[%d][MONITOR] %d%% blocked" % (env.now, 100 * sum(blocked) / len(blocked)))

# Plot a histogram
#
def plotHist(hists : [Histogram], cols=1):
    fig = plt.figure()
    rows = math.floor(len(hists) / cols)
    for i,(t,h) in enumerate(hists.items()):
        p = fig.add_subplot(rows, cols, i+1)
        y,x = h.result()
        p.bar(x,y)
        p.set_xlabel("time")
        p.set_ylabel(t)
    return fig

# ############################################################################ #
# Main

def main(graph, n, logTags = []):
    env = Environment()
    cw = Chainweb(env, graph, logTags)
    m = env.process(monitor(env, cw, n/100))
    env.run(until=n)

    print([i.blockedTime for i in cw.graph.vs["chain"]])

    blockedHist = Histogram(1)
    for i in cw.graph.vs["chain"]:
        blockedHist.append(i.blockedHist)

    cycleHist = Histogram(1)
    for i in cw.graph.vs["chain"]:
        cycleHist.append(i.cycleHist)

    miningHist = Histogram(1)
    for i in cw.graph.vs["chain"]:
        miningHist.append(i.miningHist)

    return cw, {
            "wait time": blockedHist,
            "solve time": miningHist,
            "total block time": cycleHist
        }

