# profiler.py

"""
Profiling script used to test the performance of the module.
"""

import cProfile, pstats
import unittest
from pstats import SortKey
# from pyinstrument import Profiler
import timeit

# from test.performance.set_signal import main as test_main

def main():

    profiler = cProfile.Profile()
    # profiler = Profiler(interval=0.0001)

    test_loader = unittest.TestLoader()
    tests = test_loader.discover("test")
    test_runner = unittest.TextTestRunner()

    profiler.enable()
    # profiler.start()

    test_runner.run(tests)
    # start = timeit.default_timer()
    # test_main()
    # stop = timeit.default_timer()

    profiler.disable()
    # profiler.stop()

    stats = pstats.Stats(profiler).sort_stats(SortKey.PCALLS)
    stats.print_stats(0.1)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(0.1)
    # profiler.open_in_browser()
    # print(stop - start)


if __name__ == "__main__":
    main()