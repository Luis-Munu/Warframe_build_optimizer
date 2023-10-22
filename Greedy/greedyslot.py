class GreedySlot:
    def __init__(self, polarity, slot_type, id):
        self.polarity = polarity
        self.type = slot_type
        self.mod = None
        self.cost = 0
        self.id = id