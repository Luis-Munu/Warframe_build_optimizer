import cProfile
import warnings

from .genetics import GeneticAlgorithm
from .build import Build


class GeneticCalculator:
    """
    A class that represents a genetic calculator for optimizing builds in a game.
    """

    def __init__(self, loader=None, config=None):
        """
        Initializes a new instance of the GeneticCalculator class.

        :param loader: An optional loader object.
        :param config: An optional configuration object.
        """
        self.loader = loader
        self.config = config

    def optimize_build(self):
        """
        Optimizes the build using a genetic algorithm.
        """
        best_build = Build(self.config)
        while best_build.stat_distance > 0.1:
            genetic_algorithm = GeneticAlgorithm(self.config)
            best_build = genetic_algorithm.run_genetic_algorithm()

        print(f"Used Aura: {best_build.used_aura}, Used Exilus: {best_build.used_exilus}, Used Standard Mods: {best_build.used_mods}")
        print(f"Modded Stats: {best_build.modded_stats}")
        print(f"Mods: {[mod['name'] for mod in best_build.mods]}")
        print(f"Used Capacity: {best_build.used_capacity}")

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    gc = GeneticCalculator()
    gc.optimize_build()
    profiler.disable()
    profiler.print_stats(sort='cumtime')
    profiler.dump_stats("profile.prof")