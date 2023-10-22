
import random

from .greedybuild import GreedyBuild



class GreedyAlgorithm:
    def __init__(self, config=None):
        self.config = config

    def backtrack(self, current_build, remaining_mods, remaining_capacity, highest_score, best_builds, min_score):
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
        best_builds = []
        highest_score = 0
        initial_build = self.create_initial_build(self.config.POLARITY_NUMBER)
        remaining_mods = [mod for mod in self.config.mod_database if mod["type"] == 0]
        result, highest_score, best_builds = self.backtrack(initial_build, remaining_mods, self.config.MAX_CAPACITY - initial_build.capacity, self.config.base_stats, self.config.goal_stats, highest_score, best_builds)
        return best_builds

    def update_mod_pool(self, build, mods):
        # update the score of each mod in the pool
        for mod in mods:
            mod["score"] = self.update_mod_score(build, mod)

        return mods

    def update_mod_score(self, build, mod):
        # we are gonna base the score on this old formulae: mod["weight"] = sum([goal_stats[stat] - mod[stat] if mod[stat] < self.config.goal_stats[stat] else self.config.goal_stats[stat] for stat in self.config.goal_stats])
        # first, if the build cannot add the mod because of capacity, we set the score to 0
        if not build.can_add_mod(mod):
            return 0
        # now if we can add it, we calculate the score based on the stats it would add to the build
        modded_stats = build.calculate_modded_stats(mod)

        score = 0
        for stat in self.config.goal_stats:
            if mod[stat] != 0.0:
                score += mod[stat] if modded_stats[stat] < self.config.goal_stats[stat] else mod[stat] - (modded_stats[stat] - self.config.goal_stats[stat])

        # now reduce the score based on the cost of the mod, actualDrain * 0.1
        score -= mod["actualDrain"] * 0.005
        if score < 0:
            score = 0
        return score

    def create_initial_build(self):
        """
        Creates an initial build with the given number of self.config.POLARITIES.
        """
        build = GreedyBuild(config=self.config)
        if self.config.AURA_SLOT_FREE:
            aura_polarity = [polarity for polarity in self.config.POLARITIES[1] if self.config.POLARITIES[1][polarity]][0]
            aura_mods = [mod for mod in self.config.mod_database if mod["type"] == 1 and mod["polarity"] == aura_polarity]
            if aura_mods:
                weight_func = lambda mod: -mod["actualDrain"] * (4 if mod["polarity"] == aura_polarity else 1)
                build.add_mod(random.choices(aura_mods, weights=[weight_func(mod) for mod in aura_mods])[0])
        if self.config.EXILUS_SLOT_FREE:
            exilus_polarity = [polarity for polarity in self.config.POLARITIES[2] if self.config.POLARITIES[2][polarity]][0]
            exilus_mods = [mod for mod in self.config.mod_database if mod["type"] == 2 and mod["polarity"] == exilus_polarity]
            if exilus_mods:
                weight_func = lambda mod: -mod["actualDrain"] * (4 if mod["polarity"] == exilus_polarity else 1)
                build.add_mod(random.choices(exilus_mods, weights=[weight_func(mod) for mod in exilus_mods])[0])

        return build

    def is_build_valid(self, build):
        sc = sum([max(0, self.config.goal_stats[stat] - build.stats[stat]) for stat in self.config.goal_stats])
        if not sc:
            return True
        return False




    
    

