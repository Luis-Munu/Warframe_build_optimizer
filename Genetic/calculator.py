import cProfile
import warnings
warnings.filterwarnings("ignore")

from .genetics import GeneticAlgorithm
from .build import Build

class genetic_calculator:
    def __init__(self, loader=None, config=None):
        self.loader = loader
        self.config = config
    
    def main(self):
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
    gc = genetic_calculator()
    profiler.disable()
    profiler.print_stats(sort='cumtime')
    profiler.dump_stats("profile.prof")
