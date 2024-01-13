# coup/models.py
import random

class Player:

    def __init__(self, name):
        self.name = name
        self.coins = 2
        self.cards = []

    def __str__(self):
        return f"{self.name}"

class CoupGame:
    def __init__(self, human_player, AI_players):
        #Both human_player and AI_players are Player objects
        self.human_player = human_player
        self.AI_players = AI_players

        #List of all players
        self.players = [human_player] + AI_players

        #List of all cards in the game
        self.deck = ["contessa", "duke", "captain", "ambassador", "assassin"] * 3

        # Shuffle the deck before dealing
        self.shuffle_deck()

        # Index of the current player in the players list
        self.current_player_index = 0  

        # Deal two cards to each player
        for player in self.players:
            player.cards.extend([self.deal_card(), self.deal_card()])
    
    def deal_card(self):
        return self.deck.pop(0)
    
    def shuffle_deck(self):
        random.shuffle(self.deck)

    def get_current_player(self):
        return self.players[self.current_player_index]
    
    #Check if player is eliminated
    def is_eliminated(self, player):
        return not player.cards

    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None  # Player not found
        

    def perform_action(self, actor, target, action):
        # Basic actions
        if action == "income":
            self.income(actor)
        elif action == "foreign_aid":
            self.foreign_aid(actor)
        elif action == "coup":
            self.coup(actor, target)

        #Influence actions
        elif action == "tax":
            self.tax(actor)
        elif action == "assassinate":
            self.assassinate(actor, target)
        elif action == "exchange":
            self.exchange(actor)
        elif action == "steal":
            self.steal(actor, target)
        
        #Counteractions, challenges, and allow
        elif action == "challenge":
            self.challenge(actor, target, action)
        elif action == "block":
            self.block_action(actor, target, action)
        elif action == "allow":
            self.allow_action(actor, action)
        
        # Check if the game has ended
        if self.check_end_of_game():
            self.reset_game()

    #Basic Actions: income, foreign aid, coup
    def income(self, player):
        player.coins += 1

    def foreign_aid(self, player):
        player.coins += 2

    def coup(self, actor, target):
        if actor.coins >= 7:
            actor.coins -= 7
            self.lose_influence(target) 
            #Check if target is eliminated

            
    #Influence Actions: tax, assassinate, exchange, steal
    def tax(self, player):
        player.coins += 3

    def assassinate(self, actor, target):
        if actor.coins >= 3:
            actor.coins -= 3
            self.lose_influence(target)

    def exchange(self, player):
        self.shuffle_deck()
        revealed_cards = self.deck[:2]
        del self.deck[:2]
        # Simulate the player choosing which cards to keep (for simplicity, keeping both)
        player.cards.extend(revealed_cards)

    def steal(self, actor, target):
        if target.coins >= 2:
            actor.coins += 2
            target.coins -= 2
        else:
            target.coins = 0
            actor.coins += target.coins
            

    def block_action(self, blocker, actor, claimed_action):
        actual_action = self.get_actual_action(actor, claimed_action)
        if actual_action and actual_action == claimed_action:
            self.eliminate_player(blocker)

    def eliminate_player(self, player):
        # Eliminate a player from the game
        self.players.remove(player)
        # Redistribute their cards or coins if needed
        for card in player.cards:
            self.deck.append(card)
        # Check if the game has ended after elimination
        if self.check_end_of_game():
            self.reset_game()

    def reveal_card(self, player, card):
        # Reveal a card belonging to a player
        if card in player.cards:
            player.cards.remove(card)
            return card
        return None  # Card not found

    def challenge(self, challenger, target, claimed_action):
        actual_action = self.get_actual_action(target, claimed_action)
        if actual_action and actual_action != claimed_action:
            self.lose_influence(target)
            return f"{challenger} successfully challenged {target}'s {claimed_action}. {target} loses 1 influence."
        return None  # No challenge resolution if actual action is not determined or challenge failed

    def lose_influence(self, player):
        # Lose one influence (remove one card)
        if player.cards:
            lost_card = random.choice(player.cards)
            player.cards.remove(lost_card)
            # Redistribute the lost card back to the deck
            self.deck.append(lost_card)

            # Check if the player has lost all influence
            if not player.cards:
                self.eliminate_player(player)
            return lost_card
        return None  # No influence to lose

    def get_actual_action(self, player, claimed_action):
        # Check if the claimed action can be challenged or blocked
        if claimed_action in ["tax", "assassinate", "steal"]:
            return self.challenge_or_block(player, claimed_action)
        return claimed_action

    def check_end_of_game(self):
        # Check if the game has ended
        return len(self.players) == 1

    def reset_game(self):
        # Reset the game state for a new round
        self.deck = ["contessa", "duke", "captain", "ambassador", "assassin"] * 3
        self.shuffle_deck()
        # Reset the players
        for player in self.players:
            player.coins = 2
            player.cards = []
            # Deal two cards to each player
            player.cards.extend([self.deal_card(), self.deal_card()])

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

# ... (other methods and game logic)
