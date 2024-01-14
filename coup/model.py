#Action class for Coup game

#These include: Income, Foreign Aid, Coup, Tax, Assassinate, Exchange, Steal, Challenge, Block Foreign Aid, Block Assassinate, Block Steal
#Actions have a name, a target, and a cost
#Actions can be challenged
#Actions can be blocked

class Action:
    def __init__(self):
        self.name = None
        self.target = None
        self.cost = None
        self.challengeable = False
        self.blockable = False
        self.blocked = False
        self.challenged = False
        self.challenger = None
        self.challenge_result = None
        self.blocker = None
        self.block_result = None
        self.successful = False
