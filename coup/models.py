# coup/models.py
import random
import time

DEFAULT_COINS = 2
AVAILABLE_ACTIONS = ["income", "foreign_aid", "tax", "assassinate", "exchange", "steal", "coup"]
TARGETLESS_ACTIONS = ["income", "foreign_aid", "tax", "exchange"]
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
        print('self.players', self.players)
        self.dead_players = []

        #List of all cards in the game
        self.deck = ["contessa", "duke", "captain", "ambassador", "assassin"] * 3

        # Shuffle the deck before dealing
        self.shuffle_deck()

        # Index of the current player in the players list
        self.current_player_index = 0  
        
        #Set current player
        self.current_player = self.players[self.current_player_index]

        # Deal two cards to each player
        for player in self.players:
            player.cards.extend([self.deal_card(), self.deal_card()])
        
        #Store current actions being performed
        self.current_turn_actions = []


    #Reset all available actions to empty
    def reset_available_actions(self, player):
        player.available_actions = []
    
    #Get all alive players
    def get_alive_players(self):
        return [player for player in self.players if player not in self.dead_players]

    #Get next player. If current player is last player, return first player
    def get_next_player(self):
        if self.current_player_index == len(self.players) - 1:
            return self.players[0]
        else:
            return self.players[self.current_player_index + 1]
        
    def check_if_must_coup(self, actor, action, target):
        #If actor has over 10 coins, they must coup
        if actor.coins >= 10:
            #If action wasn't already coup, return and prompt actor to coup
            if action != "coup":
                print(f"{actor.name} has over 10 coins. They must coup.")
                return True
            action = "coup"
            #If actor is human player, attempt to convert target to Player object
            if actor == self.human_player:
                target = self.get_player_by_name(target)
                #If target is None, target is not a valid player
                if target == None:
                    print("Invalid target. Please try again.")
                    return True
                
            self.coup(actor, target)
            return True
        
    def handle_actions(self, actor, action, target):

        if action in TARGETLESS_ACTIONS:
            print(f"{actor.name} is performing {action}.")
        else:
            print(f"{actor.name} is performing {action} on {target}.")

        if (self.check_if_must_coup(actor, action, target)):
            return

        #Handle all incoming actions
        if action == "income":
            self.income(actor)
            
        elif action == "foreign_aid":
            if (self.check_if_player_blocks_foreign_aid(actor, action)):
                return
            self.foreign_aid(actor)
            
        elif action == "coup":
            #If target is already type Player, no need to get player by name
            if isinstance(target, Player):
                self.coup(actor, target)
            else:
                #Else target is a string, get player by name
                target = self.get_player_by_name(target)
                #If target is None, target is not a valid player
                if target == None:
                    print("Invalid target. Please try again.")
                    return
            self.coup(actor, target)
            return

        elif action == "tax":
            victor = self.check_challenge(target=actor, action='tax')
            #Challenge was successful, tax
            if victor == None or victor == actor:
                self.tax(actor)
            else:
                self.handle_next_turn()
                return

        elif action == "assassinate":
            self.assassinate(actor, target)
        elif action == "exchange":
            self.exchange(actor)
        elif action == "steal":
            self.steal(actor, target)
        
        else:
            print("Invalid action. Please try again.")
            return
        self.current_turn_actions.append(action)


    #Return True if player blocks foreign aid, False otherwise. Also checks any challenges to the block
    def check_if_player_blocks_foreign_aid(self, actor, action):

        # If the actor(the player performing the block) is the human player, skip the input for human player
        if actor != self.human_player:
            #Prompt human player to block or allow foreign aid
            block_decision = input("Do you want to block the action? Enter 'Block' or 'Allow': ")
            if block_decision.lower() == "block":
                victor = self.check_challenge(target=self.human_player, action='block_foreign_aid')
                #Challenge was successful, block foreign aid
                #If victor is None, no one challenged the block
                if victor == None or victor == self.human_player:
                    self.block_foreign_aid(self.human_player, actor)
                    return True
                
        else:
            #Ask AI players if they want to block foreign aid
            #Look for first AI player to block foreign aid, then break
            for player in self.AI_players:
                #Make sure AI player is not dead and is not the actor
                if player not in self.dead_players and player != actor:
                    #Shuffle randomly between blocking and allowing
                    block_decision = random.choice(["block", "allow"])
                    if block_decision == "block":
                        victor = self.check_challenge(target=player, action='block_foreign_aid')
                        #Challenge was successful, block foreign aid
                        if victor == None or victor == player:
                            self.block_foreign_aid(player, actor)
                            return True
                    else:
                        continue
        return False

    #Prompt human player to challenge or allow the action. If challenge, return victor of challenge
    def check_challenge(self, target, action):
        #Create a challenge prompt for the human player if they aren't the target
        if target != self.human_player:
            #Prompt human player to challenge
            challenge_decision = input("Do you want to challenge the '{action}' action on {target.name}? Enter 'Challenge' or 'Allow': ".format(action=action, target=target))

            if challenge_decision.lower() == "challenge":
                victor = self.challenge(self.human_player, target, action)
                return victor
        else:
            #Ask AI players if they want to challenge
            #Look for first AI player to challenge
            for player in self.AI_players:
                #Make sure AI player is not dead and is not the target
                if player not in self.dead_players and player != target:
                    #Shuffle randomly between challenging and allowing
                    challenge_decision = random.choice(["challenge", "allow"])
                    if challenge_decision == "challenge":
                        print(f"{player.name} challenged {target.name}'s {action}.\n")
                        victor = self.challenge(player, target, action)
                        return victor
                    else:
                        continue
        return None


    def add_player_available_actions(self, player, actions):
        player.available_actions.extend(actions)
    
    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None
    
    def set_player_available_actions(self, player, actions):
        player.available_actions = actions

    def return_to_deck(self, card):
        self.deck.append(card)
    
    def return_to_deck_and_deal_a_card(self, target, card):
        self.return_to_deck(card)
        target.cards.remove(card)
        target.cards.append(self.deal_card())

    def deal_card(self):
        return self.deck.pop(0)
    
    def shuffle_deck(self):
        random.shuffle(self.deck)

    def get_current_player(self):
        return self.players[self.current_player_index]
    
    #Check if player is eliminated
    def is_eliminated(self, player):
        return not player.cards

    #Get Player Object by name
    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None  # Player not found
        

    #Basic Actions: income, foreign aid, coup
    def income(self, player):
        player.coins += 1
        print(f"{player.name} took income. \n")
        self.handle_next_turn()


    def foreign_aid(self, player):
        player.coins += 2
        print(f"{player.name} took foreign aid. \n")
        self.handle_next_turn()

    def coup(self, actor, target_player):
        if actor.coins >= 7:
            actor.coins -= 7
            self.lose_influence(target_player) 
            
            self.handle_next_turn()
        else:
            print(f"{actor.name} does not have enough coins to coup. \n")
            return


            
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
    def block_foreign_aid(self, target, actor):
        print(f"{target.name} blocked {actor.name}'s foreign aid.\n")
        self.handle_next_turn()
        return
    
    def block_steal(self, player):
        return
    
    def block_assassinate(self, player):
        return
    
    def challenge(self, challenger, target, action):
    # If target is human player, prompt human player to reveal a card
        victor = None
        if target == self.human_player:
            victor = self.handle_human_challenge(challenger, target, action)
        else:
            victor = self.handle_AI_challenge(challenger, target, action)
        return victor

    #Return the victor of the challenge
    def handle_human_challenge(self, challenger, target, action):
        # Prompt human player to choose a card to reveal
        print(f"Which card do you want to reveal? {target.cards} \n")
        revealed_card = ""
        card_to_reveal = self.get_card_for_challenge(target, action)
        while revealed_card not in target.cards:
            revealed_card = input("Enter a card to reveal: \n")
            if revealed_card not in target.cards:
                print("That card is not in your hand. Please try again.\n")

        if revealed_card == card_to_reveal:
            print(f"{target.name} revealed a {revealed_card}.\n")
            #Return card to deck, remove from target's cards, and deal a new card to target
            self.return_to_deck_and_deal_a_card(target, revealed_card)
            #Challenger loses influence
            self.lose_influence(challenger)
            #Return the victor of the challenge
            return target
        else:
            print(f"{self.human_player.name} did not have a {card_to_reveal}. \n")
            #Target loses influence
            self.lose_influence(target)
            return target


    #Return the victor of the challenge
    def handle_AI_challenge(self, challenger, target, action):
        # Check if target has the card to perform the action
        card_to_reveal = self.get_card_for_challenge(target, action)
        revealed_card = self.reveal_card(target, card_to_reveal)

        if revealed_card:
            print(f"{target.name} revealed a {card_to_reveal}.\n")
            self.return_to_deck_and_deal_a_card(target, revealed_card)
            #Challenger loses influence
            self.lose_influence(challenger)
            #Return the victor of the challenge
            return target
        else:
            print(f"{target.name} did not have a {card_to_reveal}.\n")
            #Target loses influence
            self.lose_influence(target)
            #Return the victor of the challenge
            return challenger

    def get_card_for_challenge(self, target, action):
        # Determine the card the AI player should reveal based on the action
        if action == "block_foreign_aid":
            return "duke"
        elif action == "block_steal":
            return "captain" if "captain" in target.cards else "ambassador"
        elif action == "block_assassinate":
            return "contessa"
        elif action == "exchange":
            return "ambassador"
        else:
            return None


    def eliminate_player(self, player):
        # Eliminate a player from the game
        player_index = self.players.index(player)
        self.players.remove(player)
        self.dead_players.append(player)

        # Redistribute their cards or coins if needed
        for card in player.cards:
            self.deck.append(card)

        # Check if the game has ended after elimination
        if self.check_end_of_game():
            self.reset_game()

        # Update current player index if necessary.
        # If the eliminated player is before the current player, decrement the current player index
        if self.current_player_index > player_index:
            self.current_player_index -= 1


    def reveal_card(self, player, card):
        # Reveal a card belonging to a player
        if card in player.cards:
            return card
        return None  # Card not found

    #Player should be a Player object
    def lose_influence(self, player):
        # Lose one influence (remove one card)

        #If human player is losing influence, prompt them to choose which card to lose(if they have more than one)
        if player == self.human_player:
            if len(player.cards) > 1:
                print(f"Which card do you want to lose? {player.cards}")
                lost_card = input("Enter a card to lose: ")
                player.cards.remove(lost_card)
                # Redistribute the lost card back to the deck
                self.deck.append(lost_card)
            else:
                lost_card = player.cards[0]
                player.cards.remove(lost_card)
                # Redistribute the lost card back to the deck
                self.deck.append(lost_card)

            print(f"{self.human_player.name} lost a {lost_card}. \n")
        else:
            lost_card = random.choice(player.cards)
            player.cards.remove(lost_card)

            print(f"{player.name} lost a {lost_card}. \n")
            # Redistribute the lost card back to the deck
            self.deck.append(lost_card)

            # Check if the player has lost all influence
            if not player.cards:
                self.eliminate_player(player)
            return lost_card
        
        #Lazy check on all players and eliminate any players with no cards
        for player in self.players:
            if not player.cards:
                self.eliminate_player(player)

        return None  # No influence to lose

    def check_end_of_game(self):
        # Check if the game has ended
        return len(self.players) == 1

    def reset_game(self):
        # Reset the game state for a new round
        self.deck = ["contessa", "duke", "captain", "ambassador", "assassin"] * 3
        self.shuffle_deck()
        self.current_set_actions = []
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

    def handle_next_turn(self):
        # Handle the next turn
        # Check if the game has ended
        if self.check_end_of_game():
            self.reset_game()
            return

        #Reset all players' available actions
        for player in self.players:
            player.available_actions = AVAILABLE_ACTIONS
        # Set current player index to next player
        self.set_next_player_turn()

        # If player has over 10 coins, they must coup
        #Set available actions to only coup
        if self.get_current_player().coins >= 10:
            self.set_player_available_actions(self.current_player, ['coup'])
            return


        
    def make_random_AI_move(self):
        # Make a random AI move
        current_player = self.get_current_player()
        action = "income"
        target = None
        self.handle_actions(current_player, action, target)



    def set_next_player_turn(self):
        # Set the next player's turn
        if self.current_player_index == len(self.players) - 1:
            self.current_player_index = 0
            self.current_player = self.players[0]
        else:
            self.current_player_index += 1
            self.current_player = self.players[self.current_player_index]

        
        