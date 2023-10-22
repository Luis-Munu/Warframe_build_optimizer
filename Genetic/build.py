import math

capacity_cache = {}
pool_cache = {}

class Build:
    """
    A class representing a Warframe build.

    Attributes:
    - used_mods (int): The number of regular mods used in the build.
    - total_used_mods (int): The total number of mods used in the build.
    - used_aura (bool): Whether an aura mod has been used in the build.
    - used_exilus (bool): Whether an exilus mod has been used in the build.
    - mods (list): A list of mods used in the build.
    - mod_pool (list): A list of mods that can still be used in the build.
    - aura (dict): The aura mod used in the build.
    - exilus (dict): The exilus mod used in the build.
    - modded_stats (dict): The stats of the Warframe after applying mods.
    - stat_distance (int): The difference between the modded stats and the goal stats.
    """

    def __init__(self, config=None):
        """
        Initializes a new Build object with default values.
        """
        self.mods = []
        self.mod_pool = config.MOD_DATABASE.copy()
        self.unique_mod_names = {key: False for key in config.UNIQUE_MOD_NAMES}
        
        self.used_mods = 0
        self.total_used_mods = 0
        self.used_aura = not config.AURA_SLOT_FREE
        self.used_exilus = not config.EXILUS_SLOT_FREE
        self.used_capacity = 0
        self.modded_stats = {}
        self.stat_distance = 99999
        self.config = config
    
    def update_modded_stats(self):
        """
        Updates the modded stats of the Warframe after applying mods.

        Returns:
        - modded_stats (dict): The updated modded stats of the Warframe.
        """
        modded_stats = {stat: self.config.BASE_STATS[stat] for stat in self.config.BASE_STATS}
        for mod in self.mods:
            modded_stats = {stat: modded_stats[stat] + mod[stat] for stat in self.config.BASE_STATS}
        return modded_stats
    
    def evaluate_stats(self):
        """
        Evaluates the difference between the modded stats and the goal stats.

        Returns:
        - stat_distance (int): The difference between the modded stats and the goal stats.
        """
        return sum([max(0, self.config.GOAL_STATS[stat] - self.modded_stats[stat]) for stat in self.config.GOAL_STATS])
    
    def add_mod(self, mod):
        """
        Adds a mod to the build.

        Parameters:
        - mod (dict): The mod to be added.

        Returns:
        - None
        """
        if mod["type"] == 1 and self.used_aura:
            return
        elif mod["type"] == 2 and self.used_exilus:
            return
        elif self.used_mods == self.config.MAX_MODS:
            return        
        if any(modx["uniqueName"] == mod["uniqueName"] for modx in self.mods):
            return
        for word in mod["name"].split(" "):
            if word.capitalize() in self.unique_mod_names:
                if self.unique_mod_names[word.capitalize()]:
                    return
                else: 
                    self.unique_mod_names[word.capitalize()] = True
                    
        capacity = self.calculate_capacity(mod)
        if capacity > self.config.MAX_CAPACITY:
            return
    
        if mod["type"] == 1:
            self.used_aura = True
        elif mod["type"] == 2:
            self.used_exilus = True
        else:
            self.used_mods += 1
            
        self.mods.append(mod)
        self.used_capacity = capacity
        self.modded_stats = self.update_modded_stats()
        self.stat_distance = self.evaluate_stats()
        self.total_used_mods = len(self.mods)
        self.update_mod_pool()
    
    def remove_mod(self, mod):
        """
        Removes a mod from the build.

        Parameters:
        - mod (dict): The mod to be removed.

        Returns:
        - None
        """
        if mod["type"] == 1:
            cp = mod["actualDrain"] * 2 if self.config.POLARITIES[1][mod["polarity"]] else mod["actualDrain"]
            if self.used_capacity - cp > self.config.MAX_CAPACITY:
                return
            self.used_aura = False
        elif mod["type"] == 2:
            self.used_exilus = False
        else:
            self.used_mods -= 1
        
        self.mods = [modx for modx in self.mods if modx["uniqueName"] != mod["uniqueName"]]
        self.used_capacity = self.calculate_capacity(mod)
        self.modded_stats = self.update_modded_stats()
        self.stat_distance = self.evaluate_stats()
        self.total_used_mods = len(self.mods)
        self.update_mod_pool()
    
    def update_mod_pool(self):
        """
        Updates the mod pool based on the stats we want to achieve and the mods already used in the build.

        Returns:
        - None
        """
        
        global pool_cache
        
        if tuple([hash(mod["name"]) for mod in self.mods]) in pool_cache:
            self.mod_pool = pool_cache[tuple([hash(mod["name"]) for mod in self.mods])].copy()
            return
        
        total_mods = self.config.MOD_DATABASE.copy()
        self.mod_pool = []
        
        # based on the stats we want to achieve, remove all mods that are no longer useful (for example if a goal stat has already been achieved)
        for stat in self.config.GOAL_STATS:
            if self.modded_stats[stat] < self.config.GOAL_STATS[stat]:
                self.mod_pool.extend([mod for mod in total_mods if mod[stat] != 0.0 or mod["type"] == 1])
                
        # remove mods that are already in the build
        for mod in self.mods:
            self.mod_pool = [m for m in self.mod_pool if m["uniqueName"] != mod["uniqueName"]]
        if self.used_aura:
            self.mod_pool = [m for m in self.mod_pool if m["type"] != 1]
            
        pool_cache[tuple([hash(mod["name"]) for mod in self.mods])] = self.mod_pool.copy()
        
 
    def calculate_capacity(self, mod):
        """
        Calculates the capacity cost of a mod, considering the polarities of the build.

        Parameters:
        - mod (dict): The mod whose capacity cost is to be calculated within the build.

        Returns:
        - capacity_cost (int): The capacity cost of the mod.
        """
        global capacity_cache
        
        if tuple([hash(mod["name"]) for mod in self.mods]) in capacity_cache:
            return capacity_cache[tuple([hash(mod["name"]) for mod in self.mods])]
        
        
        # Iterate through each polarity in the build and get the most expensive mod that matches the polarity
        capacity_cost = 0
        mod_list = self.mods.copy()
        mod_list.append(mod)
        mod_list.sort(key=lambda mod: mod["actualDrain"], reverse=True)
        mod_list_cp = mod_list.copy()
        build_polarities = {1: self.config.POLARITIES[1].copy(), 2: self.config.POLARITIES[2].copy(), 0: self.config.POLARITIES[0].copy()}
        polarities = self.config.POLARITY_NUMBER
        used_sd = 0
        
        if len(mod_list) > 5:
            pass
        
        for mod in mod_list:
            if build_polarities[mod["type"]][mod["polarity"]]:
                build_polarities[mod["type"]][mod["polarity"]] -= 1
                polarities -= 1
                capacity_cost += math.ceil(mod["actualDrain"] / 2) if mod["type"] != 1 else math.ceil(mod["actualDrain"] * 2)
                mod_list_cp.remove(mod)
                if not mod["type"]: used_sd += 1
            elif mod["type"]:
                capacity_cost += mod["actualDrain"]
                mod_list_cp.remove(mod)
                
        free = self.config.MAX_MODS - used_sd - polarities
        
        # for standard mods that do not match any polarity
        for mod in mod_list_cp:
            if free == 0:
                capacity_cost += math.ceil(mod["actualDrain"] * 1.5)
            else:
                capacity_cost += mod["actualDrain"]
                free-=1
                
        # update the capacity cache dictionary with the names of the mods in the build + the parameter mod along with the capacity cost
        capacity_cache[tuple([hash(mod["name"]) for mod in mod_list])] = capacity_cost
        return capacity_cost
            
            