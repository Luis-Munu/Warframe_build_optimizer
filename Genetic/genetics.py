import random
import numpy as np
from .build import Build

class GeneticAlgorithm:
    """
    A class that implements a genetic algorithm to find the best build for a given Warframe and weapon.
    """

    def __init__(self, config=None):
        """
        Initializes the GeneticAlgorithm class by generating a population of random builds.
        """

        self.config = config
        self.POPULATION_SIZE = 300
        self.MAX_GENERATIONS = 100
        self.MUTATION_RATE = 0.6
        self.MAX_STANDARD_MODS = config.MAX_MODS
        self.MAX_AURA_MODS = config.AURA_SLOT_FREE
        self.MAX_EXILUS_MODS = config.EXILUS_SLOT_FREE
        self.minimum_used_mods = config.MAX_MODS
        self.best_builds = []
        self.population = [self.generate_random_build() for _ in range(self.POPULATION_SIZE)]
    
    def generate_random_build(self):
        """
        Generates a random build by selecting mods from the mod database based on their compatibility with the Warframe and weapon.
        """
        build = Build(self.config)
        available_mods = [mod for mod in self.config.mod_database if not mod["type"] or mod["type"] == 1]
        goal_norm = {stat: self.config.goal_stats[stat] - 1 for stat in self.config.goal_stats}

        if not available_mods:
            return build

        standard_mods_sample = self.select_standard_mods(available_mods, goal_norm)
        aura_mods_sample = self.select_aura_mods(available_mods) if self.MAX_AURA_MODS > 0 else []
        exilus_mods_sample = self.select_exilus_mods(available_mods) if self.MAX_EXILUS_MODS > 0 else []
        mods_sample = standard_mods_sample + aura_mods_sample + exilus_mods_sample

        for mod in mods_sample:
            build.add_mod(mod)
            if build.stat_distance == 0:
                break

        return build


    def select_standard_mods(self, available_mods, goal_norm):
        """
        Selects standard mods from the available mods based on their compatibility with the Warframe and weapon.
        """
        multiplier_sums = []
        for mod in available_mods:
            multiplier_sum = sum([min(goal_norm[stat], mod[stat]) for stat in goal_norm])
            multiplier_sums.append(multiplier_sum)
        total_multiplier_sum = sum(multiplier_sums)
        if total_multiplier_sum == 0:
            return []

        multiplier_probs = [min(multiplier_sum / total_multiplier_sum, 0.1) for multiplier_sum in multiplier_sums]
        return random.choices(available_mods, weights=multiplier_probs, k=self.minimum_used_mods)


    def select_aura_mods(self, available_mods):
        """
        Selects aura mods from the available mods based on their compatibility with the Warframe and weapon.
        """
        aura_mods = [mod for mod in available_mods if mod["type"] == 1]
        aura_mods_sample = []
        weights = [-mod["actualDrain"] for mod in aura_mods]
        for j, mod in enumerate(aura_mods):
            if self.config.POLARITIES[1][mod["polarity"]]:
                weights[j] *= 10
        aura_mods_sample = random.choices(aura_mods, weights=weights, k=self.MAX_AURA_MODS)
        return aura_mods_sample


    def select_exilus_mods(self, available_mods):
        """
        Selects exilus mods from the available mods based on their compatibility with the Warframe and weapon.
        """
        exilus_mods = [mod for mod in available_mods if mod["type"] == 2]
        if not exilus_mods:
            return []
        exilus_mods_sample = random.choices(exilus_mods, k=self.MAX_EXILUS_MODS)
        return exilus_mods_sample
    
    def evaluate_build(self, build):
        """
        Evaluates a build by calculating its distance from the goal stats.
        """
        return build.stat_distance

    def crossover(self, parent1, parent2):
        """
        Performs crossover between two parents to generate two children.
        """
        child1 = Build(self.config)
        child2 = Build(self.config)
        parent1_mods = parent1.mods
        parent2_mods = parent2.mods

        common_mods = [mod for mod in parent1_mods if mod in parent2_mods]

        for mod in common_mods:
            if random.choice([True, False]):
                child1.add_mod(mod)
            else:
                child2.add_mod(mod)
        
        for mod in parent1_mods:
            if mod not in common_mods:
                child1.add_mod(mod)
        
        for mod in parent2_mods:
            if mod not in common_mods:
                child2.add_mod(mod)
        
        return child1, child2
    
    def mutate(self, build):
        """
        Mutates a build by randomly adding a mod from the mod pool.
        """
        available_mods = build.mod_pool
        if not available_mods:
            return build
        while random.random() > self.MUTATION_RATE:
            if random.choice([True, False]):
                build.add_mod(random.choice(available_mods))
            else:
                if build.mods:
                    build.remove_mod(random.choice(build.mods))
        return build

    def select_parents(self, fitness_scores):
        """
        Selects parents for the next generation based on their fitness scores.
        """
        total_fitness = sum(fitness_scores)
        if total_fitness == 0:
            parents = self.population
        else: 
            inverse_fitness_scores = [1 / score if score != 0 else 1e-999 for score in fitness_scores]
            total_inverse_fitness = sum(inverse_fitness_scores)
            probabilities = [score / total_inverse_fitness for score in inverse_fitness_scores]
            parents = np.random.choice(self.population, size=self.POPULATION_SIZE, p=probabilities)
        return parents
    
    def update_best_builds(self):
        """
        Updates the list of best builds found so far.
        """
        self.best_builds.extend([build for build in self.population if build.stat_distance < 0.001])

        # Remove duplicates of the best builds where ALL the mods used are the same
        unique_builds = []
        for build in self.best_builds:
            if not any(build.mods == b.mods for b in unique_builds):
                unique_builds.append(build)

        self.best_builds = unique_builds

        # Update the minimum number of used mods
        if self.best_builds:
            self.minimum_used_mods = min([build.total_used_mods for build in self.best_builds])

    def run_genetic_algorithm(self):
        """
        Runs the genetic algorithm to find the best build for the given Warframe and weapon.
            
        Returns:
        The best build found by the genetic algorithm.
        """
        stuck_counter = 0
        previous_score = 0
        
        for gen in range(self.MAX_GENERATIONS):
            fitness_scores = self.evaluate_population_fitness()
            self.update_best_builds()
            parents = self.select_parents(fitness_scores)
            new_population = self.create_new_population(parents)
            self.population = new_population
            self.update_best_builds()
            stuck_counter, previous_score = self.update_stuck_counter(stuck_counter, previous_score)
            if (len(self.best_builds) - stuck_counter) > 100 or stuck_counter > 15:
                break
        
        best_builds = self.get_best_builds()
        best_build = self.get_best_build(best_builds)
        return best_build
    
    def get_best_builds(self):
        # Get the best 10 builds with the lowest number of used mods
        builds_len = min(len(self.best_builds), 10)
        best_builds = sorted(self.best_builds, key=lambda build: build.total_used_mods)[:builds_len]
        
        # Sort the builds by penalizing them for having stats below the base stats and used capacity
        best_builds = sorted(best_builds, key=lambda build: (build.used_capacity, sum([max(0, self.config.base_stats[stat] - build.modded_stats.get(stat, 0)) for stat in self.config.base_stats])))
        
        return best_builds

    def get_best_build(self, best_builds):
        if best_builds:
            best_build = best_builds[0]
        else:
            best_build = Build(self.config)
        return best_build

    def evaluate_population_fitness(self):
        return [self.evaluate_build(build) for build in self.population]

    def create_new_population(self, parents):
        new_population = []
        for _ in range(self.POPULATION_SIZE // 2):
            parent1, parent2 = np.random.choice(parents, size=2, replace=False)
            child1, child2 = self.crossover(parent1, parent2)
            new_population.extend([self.mutate(child1), self.mutate(child2)])
        return new_population

    def update_stuck_counter(self, stuck_counter, previous_score):
        stuck_counter = stuck_counter + 1 if len(self.best_builds) == previous_score else 0
        previous_score = len(self.best_builds)
        return stuck_counter, previous_score