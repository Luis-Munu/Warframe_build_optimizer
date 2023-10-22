import cProfile
from .greedy import GreedyAlgorithm
from .greedybuild import GreedyBuild

class greedy_calculator:
    def __init__(self, loader=None, config=None):
        self.loader = loader
        self.config = config
        
    def main(self):
        best_builds = None
        bestie = None
        scored = 0
        stuck = 0
        while not best_builds and stuck < 100:
            greedy_algorithm = GreedyAlgorithm(config=self.config)
            initial_build = greedy_algorithm.create_initial_build()
            remaining_mods = [mod for mod in self.config.mod_database if mod['type'] == 0]
            last_build, best_result, best_builds = greedy_algorithm.backtrack(initial_build, remaining_mods, self.config.MAX_CAPACITY - initial_build.capacity, 0, [], 0.1)
            best_builds = [build for build in best_builds if greedy_algorithm.is_build_valid(build)]
            if best_result > scored:
                bestie = GreedyBuild(config=self.config)
                [bestie.add_mod(modx) for modx in last_build.used_mods]
                scored = best_result 
            if not best_builds:
                stuck += 1
        
        if stuck == 100:
            best_builds = [bestie]
            print(f" Unable to find a build with the desired stats, here is the best build I could find:")
    
        best_builds = sorted(best_builds, key=lambda build: build.sdnumber, reverse=False)
        print(f"Best builds:")
        for i, build in enumerate(best_builds):
            print(f"GreedyBuild {i+1}:")
            if build.used_aura:
                # find the aura mod
                aura = [mod for mod in build.used_mods if mod["type"] == 1][0]
                print(f"  Exilus: {aura['name']}")
            if build.used_exilus:
                exilus = [mod for mod in build.used_mods if mod["type"] == 2][0]
                print(f"  Exilus: {exilus['name']}")
            print("  Mods:")
        
            slots = [slot for slot in build.slots if slot.mod]
            for slot in slots:
                pol = " " + slot.polarity.capitalize() if slot.polarity else "n unpolarized"
                print(f"    {slot.mod['name']} ({slot.cost} capacity on a{pol} slot)")  
            #for mod in build.used_mods:
            #    print(f"    {mod['name']} ({mod['actualDrain']} capacity)")
            print(f"  Capacity with polarities: {build.capacity}")
            print(f"  Stats: {build.stats}")
            print(f"  Mods usados: {build.sdnumber}")
            print(f"  Score: {build.calculate_score()}")
            print()
            return build.calculate_score()
            
if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    gc = greedy_calculator()
    profiler.disable()
    profiler.print_stats(sort='cumtime')
    profiler.dump_stats("profile.prof")
