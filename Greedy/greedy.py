import random
from .greedybuild import GreedyBuild

class GreedyAlgorithm:
    """
    A class that implements the greedy algorithm for Warframe mod builds.
    """
    def __init__(self, config=None):
        """
        Initializes a new instance of the GreedyAlgorithm class.

        Args:
        - config: a dictionary containing the configuration parameters for the algorithm.
        """
        self.config = config

    def backtrack(self, current_build, remaining_mods, remaining_capacity, highest_score, best_builds, min_score):
        """
        Recursively searches for the best mod build.

        Args:
        - current_build: the current build being evaluated.
        - remaining_mods: the remaining mods that can be added to the build.
        - remaining_capacity: the remaining capacity of the build.
        - highest_score: the highest score found so far.
        - best_builds: a list of the best builds found so far.
        - min_score: the minimum score required to continue the search.

        Returns:
        - A tuple containing the best build found, the highest score found and a list of the best builds found.
        """
        score = current_build.calculate_score()
        if score > highest_score:
            highest_score = score
            if self.is_build_valid(current_build):
                best_builds.append(current_build)

        if not remaining_mods or remaining_capacity == 0:
            return current_build, highest_score, best_builds

        remaining_mods = self.update_mod_pool(current_build, remaining_mods)
        remaining_mods.sort(key=lambda mod: mod["score"], reverse=True)

        for mod in remaining_mods:
            if current_build.can_add_mod(mod):
                new_build = GreedyBuild(config=self.config)
                [new_build.add_mod(modx) for modx in current_build.used_mods]
                new_build.add_mod(mod)
                new_mods = remaining_mods.copy()
                new_mods.remove(mod)
                result, highest_score, best_builds = self.backtrack(new_build, new_mods, self.config.MAX_CAPACITY - new_build.capacity, highest_score, best_builds, min_score)
                if result:
                    return result, highest_score, best_builds

        return current_build, highest_score, best_builds

    def find_best_builds(self):
        """
        Finds the best mod builds.

        Returns:
        - A list of the best builds found.
        """
        best_builds = []
        highest_score = 0
        initial_build = self.create_initial_build(self.config.POLARITY_NUMBER)
        remaining_mods = [mod for mod in self.config.MOD_DATABASE if mod["type"] == 0]
        result, highest_score, best_builds = self.backtrack(initial_build, remaining_mods, self.config.MAX_CAPACITY - initial_build.capacity, self.config.BASE_STATS, self.config.GOAL_STATS, highest_score, best_builds)
        return best_builds

    def update_mod_pool(self, build, mods):
        """
        Updates the score of each mod in the pool.

        Args:
        - build: the current build being evaluated.
        - mods: the mods that can be added to the build.

        Returns:
        - A list of the updated mods.
        """
        for mod in mods:
            mod["score"] = self.update_mod_score(build, mod)

        return mods

    def update_mod_score(self, build, mod):
        """
        Updates the score of a mod.

        Args:
        - build: the current build being evaluated.
        - mod: the mod being evaluated.

        Returns:
        - The updated score of the mod.
        """
        if not build.can_add_mod(mod):
            return 0

        modded_stats = build.calculate_modded_stats(mod)

        score = 0
        for stat in self.config.GOAL_STATS:
            if mod[stat] != 0.0:
                score += mod[stat] if modded_stats[stat] < self.config.GOAL_STATS[stat] else mod[stat] - (modded_stats[stat] - self.config.GOAL_STATS[stat])

        score -= mod["actualDrain"] * 0.005
        if score < 0:
            score = 0
        return score

    def create_initial_build(self):
        """
        Creates an initial build with the given number of polarities.

        Returns:
        - The initial build.
        """
        build = GreedyBuild(config=self.config)
        if self.config.AURA_SLOT_FREE:
            aura_polarity = [polarity for polarity in self.config.POLARITIES[1] if self.config.POLARITIES[1][polarity]][0]
            aura_mods = [mod for mod in self.config.MOD_DATABASE if mod["type"] == 1 and mod["polarity"] == aura_polarity]
            if aura_mods:
                weight_func = lambda mod: -mod["actualDrain"] * (4 if mod["polarity"] == aura_polarity else 1)
                build.add_mod(random.choices(aura_mods, weights=[weight_func(mod) for mod in aura_mods])[0])
        if self.config.EXILUS_SLOT_FREE:
            exilus_polarity = [polarity for polarity in self.config.POLARITIES[2] if self.config.POLARITIES[2][polarity]][0]
            exilus_mods = [mod for mod in self.config.MOD_DATABASE if mod["type"] == 2 and mod["polarity"] == exilus_polarity]
            if exilus_mods:
                weight_func = lambda mod: -mod["actualDrain"] * (4 if mod["polarity"] == exilus_polarity else 1)
                build.add_mod(random.choices(exilus_mods, weights=[weight_func(mod) for mod in exilus_mods])[0])

        return build

    def is_build_valid(self, build):
        """
        Checks if a build is valid.

        Args:
        - build: the build being evaluated.

        Returns:
        - True if the build is valid, False otherwise.
        """
        sc = sum([max(0, self.config.GOAL_STATS[stat] - build.stats[stat]) for stat in self.config.GOAL_STATS])
        if not sc:
            return True
        return False