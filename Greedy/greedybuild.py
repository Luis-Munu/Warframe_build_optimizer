from .greedyslot import GreedySlot

class GreedyBuild:
    
    def __init__(self, config=None):
        self.slots = []
        self.config = config
        id = 0
        for slot_type in range(len(self.config.POLARITIES)):
            for polarity in self.config.POLARITIES[slot_type]:
                for i in range(self.config.POLARITIES[slot_type][polarity]):
                    self.slots.append(GreedySlot(polarity, slot_type, id))
                    id += 1
        sl = len([slot for slot in self.slots if slot.type == 0])
        while sl < self.config.MAX_MODS:
            self.slots.append(GreedySlot(None, 0, id))
            sl += 1
            id += 1
                     
        self.used_aura = not self.config.AURA_SLOT_FREE
        self.used_exilus = not self.config.EXILUS_SLOT_FREE
        self.unique_mod_names_used = {key: False for key in self.config.UNIQUE_MOD_NAMES}
        self.mod_names = []
        self.used_mods = []
        self.sdnumber = 0
        self.capacity = 0
        self.stats = self.config.BASE_STATS.copy()      
        
    def can_add_mod(self, mod):
        """
        Simple fast calculation to see if mod would fit if there was a free polarity slot.
        """
        if mod["type"] != 1:
            return (self.config.MAX_CAPACITY - self.calculate_capacity() - mod['actualDrain'] / 2 >= 0)
        return (self.config.MAX_CAPACITY - self.calculate_capacity() - mod['actualDrain'] * 2 >= 0)
    
    
    def add_mod(self, mod):
        """
        Adds a given mod to this build and returns the updated build.
        """
        if mod["type"] == 1 and self.used_aura or mod["type"] == 2 and self.used_exilus or self.sdnumber == self.config.MAX_MODS:
            return
        if mod['name'] in self.mod_names or not self.can_add_mod(mod):
            return
        for word in mod["name"].split(" "):
            if word.capitalize() in self.unique_mod_names_used:
                if self.unique_mod_names_used[word.capitalize()]:
                    return
                else: 
                    self.unique_mod_names_used[word.capitalize()] = True
        sl = self.optimize_capacity(mod)
        if not sl:
            return

        self.used_mods.append(mod)
        self.mod_names.append(mod['name'])
        self.slots = sl
        self.stats = self.calculate_modded_stats()
        self.capacity = self.calculate_capacity()
        if mod["type"] == 1:
            self.used_aura = True
        elif mod["type"] == 2:
            self.used_exilus = True
        else:
            self.sdnumber += 1
        
    def remove_mod_mod(self, mod):
        """
        Removes the given mod from this build and returns the updated build.
        """
        if mod["type"] == 1 and self.calculate_capacity() - mod["actualDrain"] * 2 < 0:
            return
        sl = self.optimize_capacity(mod, True)
        if not sl:
            return
        self.used_mods.remove(mod)
        self.mod_names.remove(mod['name'])
        self.slots = sl
        self.stats = self.calculate_modded_stats()
        self.capacity = self.calculate_capacity()
        if mod["type"] == 1:
            self.used_aura = False
        elif mod["type"] == 2:
            self.used_exilus = False
    
    
    def remove_mod(self, index):
        """
        Removes the mod at the given index from this build and returns the updated build.
        """
        if index < 0 or index >= len(self.used_mods):
            return
        if self.used_mods[index]["type"] == 1 and self.calculate_capacity() - self.used_mods[index]["actualDrain"] * 2 < 0:
            return
        sl = self.optimize_capacity(self.used_mods[index], True)
        if not sl:
            return
        self.used_mods.pop(index)
        self.mod_names.pop(index)
        self.slots = sl
        self.stats = self.calculate_modded_stats()
        self.capacity = self.calculate_capacity()
        if self.used_mods[index]["type"] == 1:
            self.used_aura = False
        elif self.used_mods[index]["type"] == 2:
            self.used_exilus = False
        else:
            self.sdnumber -= 1
            
    def calculate_score(self):
        sc = sum([max(0, self.config.GOAL_STATS[stat] - self.stats[stat]) for stat in self.config.GOAL_STATS])
        if sc != 0:
            return 1/sc
        else:
            return 9999
        
    def calculate_capacity(self):
        return sum(slot.cost for slot in self.slots)

    
    def reset_slots(self, slots):
        """
        Removes all mods from slots and resets their cost to 0.
        """
        for slot in slots:
            slot.mod = None
            slot.cost = 0

    def add_aura_and_exilus_mods(self, slots, aura_mods, exilus_mods):
        """
        Adds the aura and exilus mods to the appropriate slots, based on their polarities and the slots' polarities.
        """
        available_slots = slots.copy()
        aura_slot, exilus_slot = (next((s for s in slots if s.type == t), None) for t in [1, 2])
        for mod_type, mod_list, slot in [(1, aura_mods, aura_slot), (2, exilus_mods, exilus_slot)]:
            if slot:
                if mod_list:
                    mod = mod_list[0]
                    slot.mod = mod
                    available_slots.remove(slot)
                    if mod_type == 1:
                        slot.cost = mod["actualDrain"] * 2 if slot.polarity == mod["polarity"] else mod["actualDrain"] if slot.polarity == "None" else mod["actualDrain"] / 2
                    else: slot.cost = mod["actualDrain"] / 2 if slot.polarity == mod["polarity"] else mod["actualDrain"] if slot.polarity == "None" else mod["actualDrain"] * 2
                else:
                    available_slots.remove(slot)
        return available_slots


    def add_standard_mods(self, slots, standard_mods):
        """
        Adds the standard mods to the available slots, based on their polarities and the slots' polarities.
        """
        # get only slots of type 0
        slots = [slot for slot in slots if slot.type == 0]
        slots_by_polarity = {polarity: [slot for slot in slots if slot.polarity == polarity] for polarity in self.config.POLARITIES[0]}
        slots_by_polarity["None"] = [slot for slot in slots if not slot.polarity]
        available_slots = slots.copy()
        for mod in standard_mods:
            # good polarity
            slot = next((s for s in slots_by_polarity[mod["polarity"]] if s in available_slots), None)
            if not slot:
                # no polarity
                slot = next((s for s in slots_by_polarity["None"] if s in available_slots), None)
            if not slot:
                # bad polarity
                slot = next((s for s in slots if s.polarity != mod["polarity"] and s in available_slots), None)
            # if we found a slot, add the mod to it
            if slot:
                slot.mod = mod
                slot.cost = mod["actualDrain"] / (2 if slot.polarity == mod["polarity"] else 1 if slot.polarity == None else 0.5)
                available_slots.remove(slot)
        return available_slots


    def optimize_capacity(self, mod=None, remove=False):
        """
        Optimizes the capacity of this build by reordering the mods efficiently based on their polarities and the slots polarities.
        """
        slots = self.slots.copy()
        slots = [slot for slot in slots]
        self.reset_slots(slots)
        mods = self.used_mods.copy()
        if mod:
            if remove:
                mods.remove(mod)
            else:
                mods.append(mod)
        standard_mods, aura_mods, exilus_mods = [mod for mod in mods if mod["type"] == 0], [mod for mod in mods if mod["type"] == 1], [mod for mod in mods if mod["type"] == 2]
        available_slots = self.add_aura_and_exilus_mods(slots, aura_mods, exilus_mods)
        available_slots = self.add_standard_mods(available_slots, standard_mods)
        
        if (self.calculate_capacity()) > self.config.MAX_CAPACITY:
            return None
        else:
            return slots
    
    def calculate_modded_stats(self, modx=None):
        """
        Calculates the modded stats of this build based on its stats and the used mods multiplier.
        """
        modded_stats = {stat: self.config.BASE_STATS[stat] for stat in self.config.BASE_STATS}
        for mod in self.used_mods if modx == None else self.used_mods + [modx]:
            modded_stats = {stat: modded_stats[stat] + mod[stat] for stat in self.config.BASE_STATS}
        return modded_stats

                
    
    def __eq__(self, other):
        """
        Compares this build to another build for equality.
        """
        return sorted(self.mod_names) == sorted(other.mod_names)
    
    def __hash__(self):
        """
        Returns the hash value of this build based on its mod names, as the order must not matter we sort the mod names first.
        """
        return hash(tuple(sorted(self.mod_names)))