# coup/models.py
import random
import time

DEFAULT_COINS = 2
AVAILABLE_ACTIONS = ["income", "foreign_aid", "tax", "exchange", "steal"]
TARGETLESS_ACTIONS = ["income", "foreign_aid", "tax", "exchange"]

#COSTS
INCOME_GAIN = 1
FOREIGN_AID_GAIN = 2
TAX_GAIN = 3
STEAL_GAIN = 2

ASSASSIN_COST = 3
COUP_COST = 7

COUP_LIMIT = 10

class Player:

    def __init__(self, name):
        self.name = name
        self.coins = DEFAULT_COINS
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


    #Reset all available actions to empty of player
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
        #If actor has over COUP LIMIT coins, they must coup
        if actor.coins >= COUP_LIMIT:
            #If action wasn't already coup, return and prompt actor to coup
            if action != "coup":
                print(f"{actor.name} has over 10 coins. They must coup.")
                return True
            action = "coup"
            #If actor is human player, attempt to convert target to Player object

            target = self.get_target_player(target)
            if target == None:
                return True
                
            self.coup(actor, target)
            return True
        
    def get_target_player(self, target):
        # If target is already a Player instance, return it directly
        if isinstance(target, Player):
            return target
        else:
            # If target is a string, get player by name
            target_player = self.get_player_by_name(target)
            # If target_player is None, target is not a valid player
            if target_player is None:
                print("Invalid target. Please try again.")
                return None
            return target_player
        
    #Handle all incoming Actions
    def handle_actions(self, actor, action, target):

        if action in TARGETLESS_ACTIONS:
            print(f"{actor.name} is performing {action}.")
        else:
            print(f"{actor.name} is performing {action} on {target}.")

        if (self.check_if_must_coup(actor, action, target)):
            return
        
        elif action == "income":
            self.income(actor)
            return

        elif action == "foreign_aid":
            if (self.check_if_player_blocks_foreign_aid(actor, action)):
                return
            else:
                self.foreign_aid(actor)
                return
            
        elif action == "coup":
            if actor.coins < COUP_COST:
                print("You do not have enough coins to coup. Please try again.")
                return
            #Handle different target types(target can be a string if human types, and a Player object if AI)
            target = self.get_target_player(target)
            if target == None:
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
            if actor.coins < ASSASSIN_COST:
                print("You do not have enough coins to assassinate. Please try again.")
                return
            #Handle different target types(target can be a string if human types, and a Player object if AI)
            target = self.get_target_player(target)
            if target == None:
                return

            #Actor cannot challenge their own assassination attempt
            victor = self.check_challenge(target=actor, action='assassinate')
            #Challenge was successful or no one challenged, check if any people block
            if victor == None or victor == actor:
                if (self.check_if_target_blocks(actor, target, "assassinate", self.block_assassinate)):
                    self.handle_next_turn()
                    return
                else:
                    self.assassinate(actor, target)
                    return

        elif action == "exchange":
            victor = self.check_challenge(target=actor, action='exchange')
            #Challenge was successful, exchange
            print(victor == None or victor == actor)
            print(victor)
            print(actor)
            if victor == None or victor == actor:
                self.exchange(actor)
            else:
                self.handle_next_turn()
                
            return
            
        elif action == "steal":
            self.steal(actor, target)
        
        else:
            print("Invalid action. Please try again.")
            return
        self.current_turn_actions.append(action)


    def check_if_target_blocks(self, actor, target, action, block_action):
        #If target is human player, prompt them to block
        if target == self.human_player:
            block_decision = input("Do you want to block the action? Enter 'Block' or 'Allow': ")
            if block_decision.lower() == "block":
                victor = self.check_challenge(target=self.human_player, action="block_" + action)
                #Challenge was successful, block
                if victor == None or victor == self.human_player:
                    block_action(actor, target)
                    return True
        else:
            #Check if the AI player blocks, The AI Player is the target
            block_decision = random.choice(["block", "allow"])
            if block_decision == "block":
                victor = self.check_challenge(target=target, action="block_" + action)
                #Challenge was successful, block
                if victor == None or victor == target:
                    block_action(actor, target)
                    return True

        return False




    #Return True if player blocks foreign aid, False otherwise. Also checks any challenges to the block
        #handled differently from block_steal and block_assassinate because foreign aid is a targetless action
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
                        break
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
        player.coins += INCOME_GAIN
        print(f"{player.name} took income. \n")
        self.handle_next_turn()


    def foreign_aid(self, player):
        player.coins += FOREIGN_AID_GAIN
        print(f"{player.name} took foreign aid. \n")
        self.handle_next_turn()

    def coup(self, actor, target_player):
        actor.coins -= COUP_COST
        self.lose_influence(target_player) 
        print(f"{actor.name} couped {target_player.name}. \n")
        self.handle_next_turn()


            
    #Influence Actions: tax, assassinate, exchange, steal
    def tax(self, player):
        player.coins += TAX_GAIN
        print(f"{player.name} took tax. \n")
        self.handle_next_turn()

    def assassinate(self, actor, target):
        if actor.coins >= ASSASSIN_COST:
            actor.coins -= ASSASSIN_COST
            self.lose_influence(target)
            print(f"{actor.name} assassinated {target.name}. \n")
            self.handle_next_turn()

    def exchange(self, player):
        # If player is human, prompt them to choose two cards to exchange
        if player == self.human_player:
            print(f"Which two cards do you want to exchange? {player.cards} \n")
            card1 = input("Enter the first card to exchange: \n")
            while card1 not in player.cards:
                print("That card is not in your hand. Please try again.\n")
                card1 = input("Enter the first card to exchange: \n")
            card2 = input("Enter the second card to exchange: \n")
            while card2 not in player.cards or card2 == card1:
                print("That card is not in your hand or you entered the same card twice. Please try again.\n")
                card2 = input("Enter the second card to exchange: \n")
            keep_card = input(f"Which card do you want to keep? {card1} or {card2}: \n")
            while keep_card not in [card1, card2]:
                print("Invalid choice. Please choose either {card1} or {card2}.\n")
                keep_card = input(f"Which card do you want to keep? {card1} or {card2}: \n")

            player.cards.remove(keep_card)
            discarded_card = card1 if keep_card == card2 else card2
            # Redistribute the discarded card back to the deck
            self.return_to_deck(discarded_card)
            new_card = self.deal_card()
            player.cards.append(new_card)
            print(f"{self.human_player.name} exchanged a {discarded_card} for a new card from the deck. \n")
        else:
            # If player is AI, select two cards to exchange randomly
            card_to_exchange = random.sample(player.cards, 2)
            keep_card = random.choice(card_to_exchange)
            card_to_exchange.remove(keep_card)
            discarded_card = card_to_exchange[0]
            for card in card_to_exchange:
                player.cards.remove(card)
            # Redistribute the discarded card back to the deck
            self.return_to_deck(discarded_card)
            new_card = self.deal_card()
            player.cards.append(new_card)
            print(f"{player.name} exchanged a {discarded_card} for a new card from the deck. \n")

        self.handle_next_turn()


    def steal(self, actor, target):
        if target.coins >= STEAL_GAIN:
            actor.coins += STEAL_GAIN
            target.coins -= STEAL_GAIN
        else:
            target.coins = 0
            actor.coins += target.coins
    
    #Blockable Actions: foreign aid, steal, assassinate
    def block_foreign_aid(self, target, actor):
        print(f"{target.name} blocked {actor.name}'s foreign aid.\n")
        self.handle_next_turn()
        return
    
    def block_steal(self, actor, target):

        return
    
    def block_assassinate(self, actor, target):
        #Can't go to negative coins
        print(f"{target.name} blocked {actor.name}'s assassination attempt.\n")
        if actor.coins >= ASSASSIN_COST:
            actor.coins -= ASSASSIN_COST
        else:
            actor.coins = 0
        self.handle_next_turn()
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
            return challenger


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
        # Determine the right card to reveal challenge
        if action == "block_foreign_aid" or action == "tax":
            return "duke"
        elif action == "block_steal":
            return "captain" if "captain" in target.cards else "ambassador"
        elif action == "steal":
            return "captain" 
        elif action == "assassinate":
            return "assassin"
        elif action == "exchange":
            return "ambassador"
        elif action == "block_assassinate":
            return "contessa"
        
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
        # Reset the players 
        for player in self.players:
            player.coins = DEFAULT_COINS
            player.cards = []
            # Deal two cards to each player
            player.cards.extend([self.deal_card(), self.deal_card()])

        # Reset the current player index
        self.current_player_index = 0

        # Join the dead players back to the game
        self.players.extend(self.dead_players)

        # Reset all available actions
        self.reset_alive_players_available_actions()

        
    def reset_alive_players_available_actions(self):
        #Reset all alive players' available actions
        for player in self.get_alive_players():
            player.available_actions = AVAILABLE_ACTIONS

    def handle_next_turn(self):
        # Handle the next turn
        # Check if the game has ended
        if self.check_end_of_game():
            self.reset_game()
            return

        # Reset all available actions for all players
        self.reset_alive_players_available_actions()

        # Set current player index to next player
        self.set_next_player_turn()

        #Allow assassinate if player has ASSASSIN COST coins
        current_player_num_coins = self.get_current_player().coins
        if current_player_num_coins >= ASSASSIN_COST:
            #Check if greater than COUP_COST, if so, allow coup
            if current_player_num_coins >= COUP_COST:
                self.set_player_available_actions(self.current_player, AVAILABLE_ACTIONS  + ['assassinate'])
            else:
                self.set_player_available_actions(self.current_player, AVAILABLE_ACTIONS + ['assassinate', 'coup'])


        # If player has over COUP LIMIT coins, they must coup
        #Set available actions to only coup
        if self.get_current_player().coins >= COUP_LIMIT:
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

        
        