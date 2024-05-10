import math

# TODO: there are probably some good libraries with support for this
class Histogram:

    """
    Quick and Dirty Linear Histogram
    """

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
            raise NotImplementedError("merging histograms with different bin sizes isn't yet implemented")

    def result(self):
        imin = min(self.bins.keys())
        imax = max(self.bins.keys())
        a = [0] * (imax - imin + 1)
        b = [self.binSize * k for k in range(imin, imax + 1)]
        for i in range(imin, imax + 1):
            if i in self.bins:
                a[i - imin] = self.bins[i]
        return a, b

    def mean(self):
        a,b = self.result()
        return sum([a[i] * b[i] for i in range(len(a))]) / sum(a)


# TODO: implement more general WithStatistics class
class HistogramSample:
    def __init__(self, histogram, clock):
        self.histogram = histogram
        self.clock = clock
        self.start = None
    def __enter__(self):
        self.start = self.clock.now
        return self.start
    def __exit__(self, _type, value, traceback):
        self.histogram.sample(self.clock.now - self.start)
        return None # rethrow
