from . import loader

MAX_MODS = 8
MAX_CAPACITY = 83
AURA_SLOT_FREE = True
EXILUS_SLOT_FREE = True

# Stats we want to achieve. EDIT THIS
goal_stats = {
    "Range": 2.6,
    "Strength": 2.0,
    "Duration": 1.54,
    "Efficiency": 0.7,
    "Sprint Speed": 1.0,
}

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


#sum the standard polarities
POLARITY_NUMBER = sum([POLARITIES[0][polarity] for polarity in POLARITIES[0]])

# Base stats on which calculations are performed. EDIT THIS IF USING ARCHON SHARDS
base_stats = {
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
mod_database = loader.get_mods()

# Remove mods that do not have any of the goal stats
mod_database = [mod for mod in mod_database if any(mod[stat] > 0.0 for stat in goal_stats) or mod["type"] == 1]

# Minimum needed goal stats.
min_goal_stats = {
    stat: max(goal_stats[stat], base_stats[stat]) for stat in goal_stats
}

unique_mod_names = ["Continuity", "Flow", "Stretch", "Vitality", "Vigor", "Fiber", "Intensify", "Anguish", "Hatred"]