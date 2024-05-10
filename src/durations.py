def gamma5(prng, mean : float) -> float:
    return prng.gamma(shape=5, scale=mean/5)

# latency: validation + network + validation
def latencyDelay(ctx) -> float:
    """
    We use the generic term $\text{latency}$ to summarize the duration of the
    validation of a block after it is discovered and before it is published,
    the network latency, and the validation after it is received. In case a
    block is discovered on the same node the network latency and one validation
    step are omitted. This is modeled by using a Bernoulli distribution to
    estimate the chance that a block is mined locally and a reduced latency is
    used.

    """
    is_local = ctx.prng.binomial(n=1, p = 1 / ctx.conf.NUMBER_OF_MINING_NODES)
    if is_local:
        return gamma5(ctx.prng, ctx.conf.LOCAL_BLOCK_LATENCY)
    else:
        return gamma5(ctx.prng, ctx.conf.REMOTE_BLOCK_LATENCY)

# Pact new block
def pactDelay(ctx) -> float:
    """
    Pact new block validation is modeled separately from other latencies
    because, depending on the mining framework that is used, it is applied after
    a chain becomes unblocked.
    """
    return gamma5(ctx.prng, ctx.conf.PACT_NEW_BLOCK_TIME)

def miningDelay(ctx, target : float) -> float:
    """
    Mining is exponentialy distributed with the target being the mean.
    
    This uses the effective target, which is the product of the target, the
    target multiplier, and the hash power factor.
    """
    return ctx.prng.exponential(target)
