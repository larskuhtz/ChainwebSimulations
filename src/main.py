from simpy import Environment
import pandas as pd

from . chainweb import Chainweb
from . ctx import Ctx
from . mine import Mine

def blocked_part(chainweb : Chainweb):
    """
    Return the fraction of blocked chains
    """
    cur = [ i.is_blocked for i in chainweb.graph.vs["chain"] ]
    return sum(cur)/len(cur)

def monitor(env, chainweb, n):
    """
    Monitor the value of variables at fixed intervals
    """
    blocked = []
    while True:
        yield env.timeout(n)
        cur = [ i.is_blocked for i in chainweb.graph.vs["chain"] ]
        blocked.append(sum(cur)/ len(cur))
        print(f"[{env.now}][MONITOR] {100 * sum(cur) / len(cur)} % blocked")

def main(conf, n):
    """
    Run a Chainweb Simulation
    """
    env = Environment()
    ctx = Ctx(env = env, conf = conf)
    cw = Chainweb(ctx)
    Mine.reset()
    env.process(monitor(env, cw, n/10))
    env.run(until=n)
    return cw

def get_data(cw):
    """
    Collect Timeing data from the simulation
    """
    chains = cw.chains
    cs = pd.DataFrame()
    cs["cycle times"] = pd.DataFrame({c.chain:pd.Series(c.cycle_times) for c in chains}).stack()
    cs["blocked times"] = pd.DataFrame({c.chain:pd.Series(c.blocked_times) for c in chains}).stack()
    cs["targets"] = pd.DataFrame({c.chain:pd.Series(c.targets) for c in chains}).stack()
    cs["new block times"] = pd.DataFrame({c.chain:pd.Series(c.new_block_times) for c in chains}).stack()
    cs["mine times"] = pd.DataFrame({c.chain:pd.Series(c.mine_times) for c in chains}).stack()
    cs["hash power factors"] = pd.DataFrame({c.chain:pd.Series(c.hash_power_factors) for c in chains}).stack()
    cs.index.names = ["height", "chain"]
    return cs