import cProfile
from .greedy import GreedyAlgorithm
from .greedybuild import GreedyBuild

class GreedyCalculator:
    """
    A class that calculates the best build for a given configuration using the Greedy Algorithm.
    """
    def __init__(self, loader=None, config=None):
        """
        Initializes the GreedyCalculator with a mod loader and a configuration.

        Args:
        - loader: a loader for the mods to be used in the build
        - config: a configuration object with the build parameters
        """
        self.loader = loader
        self.config = config
        
    def optimize_build(self):
        """
        Calculates the best build for the given configuration using the Greedy Algorithm.

        Returns:
        - The best build found
        """
        best_builds = None
        best_build = None
        best_score = 0
        stuck = 0
        while not best_builds and stuck < 100:
            greedy_algorithm = GreedyAlgorithm(config=self.config)
            initial_build = greedy_algorithm.create_initial_build()
            remaining_mods = [mod for mod in self.config.MOD_DATABASE if mod['type'] == 0]
            last_build, best_result, best_builds = greedy_algorithm.backtrack(initial_build, remaining_mods, self.config.MAX_CAPACITY - initial_build.capacity, 0, [], 0.1)
            best_builds = [build for build in best_builds if greedy_algorithm.is_build_valid(build)]
            if best_result > best_score:
                best_build = GreedyBuild(config=self.config)
                [best_build.add_mod(modx) for modx in last_build.used_mods]
                best_score = best_result 
            if not best_builds:
                stuck += 1
        
        if stuck == 100:
            best_builds = [best_build]
            print(f" Unable to find a build with the desired stats, here is the best build I could find:")
    
        best_builds = sorted(best_builds, key=lambda build: build.sdnumber, reverse=False)
        print(f"Best builds:")
        for i, build in enumerate(best_builds):
            print(f"GreedyBuild {i+1}:")
            if build.used_aura:
                # find the aura mod
                aura = [mod for mod in build.used_mods if mod["type"] == 1][0]
                print(f"  Aura: {aura['name']}")
            if build.used_exilus:
                exilus = [mod for mod in build.used_mods if mod["type"] == 2][0]
                print(f"  Exilus: {exilus['name']}")
            print("  Mods:")
        
            slots = [slot for slot in build.slots if slot.mod]
            for slot in slots:
                polarity = " " + slot.polarity.capitalize() if slot.polarity else "n unpolarized"
                print(f"    {slot.mod['name']} ({slot.cost} capacity on a{polarity} slot)")  
            print(f"  Capacity with polarities: {build.capacity}")
            print(f"  Stats: {build.stats}")
            print(f"  Mods used: {build.sdnumber}")
            print(f"  Score: {build.calculate_score()}")
            print()
            return build.calculate_score()
            
if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    gc = GreedyCalculator()
    gc.optimize_build()
    profiler.disable()
    profiler.print_stats(sort='cumtime')
    profiler.dump_stats("profile.prof")