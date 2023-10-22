class GreedySlot:
    """
    A class representing a slot in a greedy algorithm for natural language understanding.

    Attributes:
    -----------
    polarity : str
        The polarity of the slot, either "positive" or "negative".
    slot_type : str
        The type of the slot, such as "date", "time", "location", etc.
    slot_modifier : str
        The modifier of the slot, such as "next", "last", "before", etc.
    cost : int
        The cost of the slot, initially set to 0.
    slot_id : int
        The unique identifier of the slot.
    """
    def __init__(self, polarity, slot_type, id):
        self.polarity = polarity
        self.type = slot_type
        self.mod = None
        self.cost = 0
        self.id = id