from . import loader
import numpy as np

# Maximum number of mods that can be equipped
MAX_MODS = 8

# Maximum capacity of the modding system
MAX_CAPACITY = 83

# Whether the aura slot is free or not
AURA_SLOT_FREE = True

# Whether the exilus slot is free or not
EXILUS_SLOT_FREE = True

# Stats we want to achieve. Edit this dictionary to set your desired values
GOAL_STATS = {
    "Range": 2.6,
    "Strength": 2.0,
    "Duration": 1.54,
    "Efficiency": 0.7,
    "Sprint Speed": 1.0,
}

# Polarities of the mod slots
POLARITIES = {
    0: {
        "vazarin": 2,
        "madurai": 1,
        "naramon": 0,
        "zenurik": 1,
        "umbra": 0
    },
    1: {
        "vazarin": 0,
        "madurai": 1,
        "naramon": 0,
        "zenurik": 0,
        "umbra": 0
    },
    2: {
        "vazarin": 1,
        "madurai": 0,
        "naramon": 0,
        "zenurik": 0,
        "umbra": 0
    }
}

# Total number of polarities
POLARITY_NUMBER = sum([POLARITIES[0][polarity] for polarity in POLARITIES[0]])

# Base stats on which calculations are performed. Edit this dictionary to set your desired values
BASE_STATS = {
    "Range": 1.0,
    "Duration": 1.0,
    "Efficiency": 1.0,
    "Strength": 1.0,
    "Health": 1.0,
    "Shield": 1.0,
    "Armor": 1.0,
    "Energy": 1.0,
    "Sprint Speed": 1.0,
    "Mobility": 1.0
}

# Mods are in a dictionary format, the calculations will be performed in numpy.
MOD_DATABASE = loader.get_mods()

# Remove mods that do not have any of the goal stats
MOD_DATABASE = [mod for mod in MOD_DATABASE if any(mod[stat] > 0.0 for stat in GOAL_STATS) or mod["type"] == 1]

# Minimum needed goal stats.
MIN_GOAL_STATS = {
    stat: max(GOAL_STATS[stat], BASE_STATS[stat]) for stat in GOAL_STATS
}

# List of unique mod names
UNIQUE_MOD_NAMES = ["Continuity", "Flow", "Stretch", "Vitality", "Vigor", "Fiber", "Intensify", "Anguish", "Hatred"]

def calculate_mod_stats(mods):
    """
    Calculates the stats of the given mods.

    Args:
        mods (list): List of mods to calculate stats for.

    Returns:
        dict: Dictionary containing the calculated stats.
    """
    mod_stats = BASE_STATS.copy()
    for mod in mods:
        for stat in mod:
            if stat in mod_stats:
                mod_stats[stat] += mod[stat]
    return mod_stats

def get_best_mods():
    """
    Returns the best mods to achieve the desired stats.

    Returns:
        list: List of best mods.
    """
    best_mods = []
    for i in range(len(MOD_DATABASE)):
        for j in range(i+1, len(MOD_DATABASE)):
            for k in range(j+1, len(MOD_DATABASE)):
                for l in range(k+1, len(MOD_DATABASE)):
                    mods = [MOD_DATABASE[i], MOD_DATABASE[j], MOD_DATABASE[k], MOD_DATABASE[l]]
                    mod_stats = calculate_mod_stats(mods)
                    if all(mod_stats[stat] >= MIN_GOAL_STATS[stat] for stat in MIN_GOAL_STATS):
                        best_mods.append(mods)
    return best_mods