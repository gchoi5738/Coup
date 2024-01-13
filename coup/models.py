# coup/models.py
import random


DEFAULT_COINS = 2
AVAILABLE_ACTIONS = ["income", "foreign_aid", "tax", "assassinate", "exchange", "steal"]
class Player:

    def __init__(self, name):
        self.name = name
        self.coins = 2
        self.cards = []
        self.available_actions = AVAILABLE_ACTIONS

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
        
        #Store current actions being performed
        self.current_turn_actions = []

    #Reset all available actions to empty
    def reset_available_actions(self, player):
        player.available_actions = []

    #Get next player. If current player is last player, return first player
    def get_next_player(self):
        if self.current_player_index == len(self.players) - 1:
            return self.players[0]
        else:
            return self.players[self.current_player_index + 1]
        
    #Handles all incoming actions
    def handle_actions(self, action, target):

        if action == "income":
            self.income(self.get_current_player())
            #Reset all players' available actions
            for player in self.players:
                player.available_actions = AVAILABLE_ACTIONS
            
            #Set next player's available actions to available actions
            self.set_player_available_actions(self.get_next_player(), AVAILABLE_ACTIONS)

            #Check if coup is available as an option
            if self.get_current_player().coins >= 7:
                self.add_player_available_actions(self.get_current_player(), ["coup"])
            

        #Check if action is challengeable. This takes precedence over blocking
        challengable_actions = ["tax", "assassinate", "steal", "exchange", "block_foreign_aid", "block_steal", "block_assassinate"]
        #If challengeable, change player's available actions to challenge
        if action in challengable_actions:
            #Current player can't challenge their own action
            self.reset_available_actions(self.get_current_player())
            #Set all other players available actions to challenge
            for player in self.players:
                if player != self.get_current_player():
                    self.set_player_available_actions(player, ["challenge", "allow"])
            
            #Append action to current turn actions
            self.current_turn_actions.append(action)

        #Check if action is blockable
        blockable_actions = ["foreign_aid", "steal", "assassinate"]
        #If blockable, change player's available actions to block
        if action in blockable_actions:
            #Current player can't block their own action
            self.reset_available_actions(self.get_current_player())
            #Set all other players to block
            for player in self.players:
                if player != self.get_current_player():
                    self.set_player_available_actions(player, ["block_" + action , "allow"])
            
            #Append action to current turn actions
            self.current_turn_actions.append(action)

        #Check if action is allow
        if action == "allow":
            #Reset all players' available actions
            for player in self.players:
                player.available_actions = AVAILABLE_ACTIONS
            
            #Set next player's available actions to available actions
            self.set_player_available_actions(self.get_next_player(), AVAILABLE_ACTIONS)

            #Check if coup is available as an option
            if self.get_current_player().coins >= 7:
                self.add_player_available_actions(self.get_current_player(), ["coup"])




        self.next_turn()
        return
    
    def add_player_available_actions(self, player, actions):
        player.available_actions.extend(actions)
    
    def set_player_available_actions(self, player, actions):
        player.available_actions = actions

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
        

    #Basic Actions: income, foreign aid, coup
    def income(self, player):
        player.coins += 1

    def foreign_aid(self, player):
        player.coins += 2

    def coup(self, actor, target):
        if actor.coins >= 7:
            actor.coins -= 7
            self.lose_influence(target) 

            
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
    
    #Blockable Actions: foreign aid, steal, assassinate
    def block_foreign_aid(self, player):
        return
    
    def block_steal(self, player):
        return
    
    def block_assassinate(self, player):
        return
    

            
    def map_available_actions(self):
        
        return

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

    def check_end_of_game(self):
        # Check if the game has ended
        return len(self.players) == 1

    def reset_game(self):
        # Reset the game state for a new round
        self.deck = ["contessa", "duke", "captain", "ambassador", "assassin"] * 3
        self.shuffle_deck()
        self.current_action = None
        # Reset the players 
        for player in self.players:
            player.coins = 2
            player.cards = []
            # Deal two cards to each player
            player.cards.extend([self.deal_card(), self.deal_card()])

        # Reset the current player index
        self.current_player_index = 0
        #Reset all players' available actions
        for player in self.players:
            player.available_actions = AVAILABLE_ACTIONS
    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
