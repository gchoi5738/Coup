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
    
    def get_alive_players(self):
        ''' Returns:
                List of Player objects that are not dead
        '''
        return [player for player in self.players if player not in self.dead_players]
 
    def check_if_must_coup(self, actor, action, target):
        ''' Check if actor must coup. If so, coup and return True.
            Parameters:
                actor: Player object
                action: String
                target: Player object or String
            Returns:
                True if actor must coup
        '''
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
        ''' Get target player by name. If target is already a Player object, return it directly.
            Parameters:
                target: Player object or String
            Returns:
                Player object if target is valid, None otherwise
        '''
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
        
    def handle_actions(self, actor, action, target):
        ''' Handles all game logic for incoming actions from players.
            Parameters:
                actor: Player object
                action: String
                target: Player object or String
        '''

        if action in TARGETLESS_ACTIONS:
            print(f"{actor.name} is performing {action}.")
        else:
            print(f"{actor.name} is performing {action} on {target}.")

        if (self.check_if_must_coup(actor, action, target)):
            return
        
        #Basic actions
        elif action == "income":
            self.income(actor)
            return

        elif action == "foreign_aid":
            #Before performing foreign aid, check if any players block. Also handles challenges to the block
            if (self.check_if_player_blocks_foreign_aid(actor, action)):
                return
            else:
                #No one blocked, foreign aid
                self.foreign_aid(actor)
                return
            
        elif action == "coup":
            #Check if actor has enough coins to coup
            if actor.coins < COUP_COST:
                print("You do not have enough coins to coup. Please try again.")
                return
            #Handle different target types(target can be a string if human types, and a Player object if AI)
            target = self.get_target_player(target)
            if target == None:
                return
            #Coups are not blockable, so no need to check if any players block
            self.coup(actor, target)
            return
        
        #Influence actions
        elif action == "tax":
            #Check if any players challenge
            victor = self.check_challenge(target=actor, action='tax')
            #If there is no victor, no one challenged. If victor is actor, challenge was successful
            if victor == None or victor == actor:
                #Challenge was successful, tax
                self.tax(actor)
            else:
                #Challenge was unsuccessful, action is cancelled
                self.handle_next_turn()
                return

        elif action == "assassinate":
            #Check if actor has enough coins to assassinate
            if actor.coins < ASSASSIN_COST:
                print("You do not have enough coins to assassinate. Please try again.")
                return
            #Handle different target types(target can be a string if human types, and a Player object if AI)
            target = self.get_target_player(target)
            if target == None:
                return

            #Check if any players challenge before checking blocks
            victor = self.check_challenge(target=actor, action='assassinate')
            #If there is no victor, no one challenged. If victor is actor, challenge was successful
            if victor == None or victor == actor:
                #Check if any players block
                if (self.check_if_target_blocks(actor, target, "assassinate", self.block_assassinate)):
                    self.handle_next_turn()
                    return
                else:
                    #No one blocked, assassinate
                    self.assassinate(actor, target)
                    return
            self.handle_next_turn()
            return

        elif action == "exchange":
            #Check if any players challenge
            victor = self.check_challenge(target=actor, action='exchange')
            #If there is no victor, no one challenged. If victor is actor, challenge was successful
            if victor == None or victor == actor:
                #Challenge was successful, exchange
                self.exchange(actor)
            else:
                #Challenge was unsuccessful, action is cancelled
                self.handle_next_turn()
            return
            
        elif action == "steal":
            #Handle different target types(target can be a string if human types, and a Player object if AI)
            target = self.get_target_player(target)
            if target == None:
                return

            #Actor cannot steal from themselves
            victor = self.check_challenge(target=actor, action='steal')
            #Challenge was successful or no one challenged, check if any people block
            if victor == None or victor == actor:
                #Check if any players block
                if (self.check_if_target_blocks(actor, target, "steal", self.block_steal)):
                    self.handle_next_turn()
                    return
                else:
                    #No one blocked, steal
                    self.steal(actor, target)
                    return
            self.handle_next_turn()
            return
        
        else:
            print("Invalid action. Please try again.")
            return
        self.current_turn_actions.append(action)


    def check_if_target_blocks(self, actor, target, action, block_action):
        ''' Check if target blocks the action. If so, block the action and return True.
            Parameters:
                actor: Player object
                target: Player object
                action: String
                block_action: Function
            Returns:
                True if target blocks the action
                False otherwise
        '''
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
        ''' Check if any players block foreign aid. If so, block foreign aid and return True.
            Parameters:
                actor: Player object
                action: String
            Returns:
                True if any player blocks foreign aid
                False otherwise
        '''
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

    def check_challenge(self, target, action):
        ''' Check if any players challenge the action. If so, challenge the action and return the victor of the challenge.
            Parameters:
                target: Player object
                action: String
            Returns:
                Player object of the challenge victor if the action was challenged
                None if no one challenged the action
        '''
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

    def get_player_by_name(self, name):
        ''' Get player by name.
            Parameters:
                name: String
            Returns:
                Player object if player is found
                None otherwise
        '''
        for player in self.players:
            if player.name == name:
                return player
        return None
    
    def set_player_available_actions(self, player, actions):
        ''' Set the available actions for a player.
            Parameters:
                player: Player object
                actions: List of Strings
        '''
        player.available_actions = actions

    def return_to_deck(self, card):
        ''' Return a card to the deck.
            Parameters:
                card: String
        '''
        self.deck.append(card)
    
    def return_to_deck_and_deal_a_card(self, target, card):
        ''' Return a card to the deck and deal a new card to the target.
            Parameters:
                target: Player object
                card: String
        '''
        self.return_to_deck(card)
        target.cards.remove(card)
        target.cards.append(self.deal_card())
        print(f"{target.name} lost a {card} and drew a new card from the deck. \n")

    def deal_card(self):
        ''' Deal a card from the deck.
            Returns:
                String representing the card dealt
        '''
        return self.deck.pop(0)
    
    def shuffle_deck(self):
        ''' Shuffle the deck.
        '''
        random.shuffle(self.deck)

    def get_current_player(self):
        ''' Get the current player.
            Returns:
                Player object
        '''
        return self.players[self.current_player_index]
    
    #Check if player is eliminated
    def is_eliminated(self, player):
        ''' Check if a player is eliminated.
            Parameters:
                player: Player object
            Returns:
                True if player is eliminated
                False otherwise
        '''
        return not player.cards

    #Basic Actions: income, foreign aid, coup
    def income(self, player):
        ''' Perform the income action.
            Parameters:
                player: Player object
        '''
        player.coins += INCOME_GAIN
        print(f"{player.name} took income. \n")
        self.handle_next_turn()

    def foreign_aid(self, player):
        ''' Perform the foreign aid action.
            Parameters:
                player: Player object
        '''
        player.coins += FOREIGN_AID_GAIN
        print(f"{player.name} took foreign aid. \n")
        self.handle_next_turn()

    def coup(self, actor, target_player):
        ''' Perform the coup action.
            Parameters:
                actor: Player object
                target_player: Player object
        '''
        actor.coins -= COUP_COST
        self.lose_influence(target_player) 
        print(f"{actor.name} couped {target_player.name}. \n")
        self.handle_next_turn()

    #Influence Actions: tax, assassinate, exchange, steal
    def tax(self, player):
        ''' Perform the tax action.
            Parameters:
                player: Player object
        '''
        player.coins += TAX_GAIN
        print(f"{player.name} took tax. \n")
        self.handle_next_turn()

    def assassinate(self, actor, target):
        ''' Perform the assassinate action.
            Parameters:
                actor: Player object
                target: Player object
        '''
        if actor.coins >= ASSASSIN_COST:
            actor.coins -= ASSASSIN_COST
            self.lose_influence(target)
            print(f"{actor.name} assassinated {target.name}. \n")
            self.handle_next_turn()

    def exchange(self, player):
        ''' Perform the exchange action.
            Parameters:
                player: Player object
        '''
        # If player is human, prompt them to choose cards to exchange
        if player == self.human_player:
            # First, draw two new cards from the deck
            new_cards = [self.deal_card(), self.deal_card()]

            # Prompt the user for the number of cards they want to exchange
            num_cards_to_exchange = -1  # Initialize with an invalid value
            while num_cards_to_exchange < 0 or num_cards_to_exchange > len(player.cards):
                num_cards_to_exchange = int(input("How many cards do you want to exchange? (0, 1, or 2): "))
                if num_cards_to_exchange < 0 or num_cards_to_exchange > len(player.cards):
                    print("Invalid number of cards. Please try again.")
                    return

            # If the player chooses to exchange cards, handle the exchange
            if num_cards_to_exchange > 0:
                for _ in range(num_cards_to_exchange):
                    card_to_exchange = input(f"Choose a card to exchange ({player.cards}): ")
                    while card_to_exchange not in player.cards:
                        print("That card is not in your hand. Please try again.")
                        card_to_exchange = input(f"Choose a card to exchange ({player.cards}): ")
                    player.cards.remove(card_to_exchange)
                    self.return_to_deck(card_to_exchange)

                # Add the new cards to the player's hand
                player.cards.extend(new_cards[:num_cards_to_exchange])

                # Return any extra new cards to the deck
                for card in new_cards[num_cards_to_exchange:]:
                    self.return_to_deck(card)

            print(f"{player.name} exchanged {num_cards_to_exchange} card(s).")
            print(f"Your new hand is: {player.cards}")

        # If player is AI, randomly decide to swap both, one, or keep both
        else:
            # For AI, randomly decide to swap both, one, or keep both
            decision = random.choice(['swap_both', 'swap_one', 'keep_both'])

            if decision == 'swap_both' and len(player.cards) >= 2:
                cards_to_exchange = random.sample(player.cards, 2)
                for card in cards_to_exchange:
                    player.cards.remove(card)
                    self.return_to_deck(card)
                new_cards = [self.deal_card(), self.deal_card()]
                player.cards.extend(new_cards)
                print(f"{player.name} exchanged both cards for new cards from the deck.\n")

            elif decision == 'swap_one' and len(player.cards) >= 1:
                card_to_exchange = random.choice(player.cards)
                player.cards.remove(card_to_exchange)
                self.return_to_deck(card_to_exchange)
                new_card = self.deal_card()
                player.cards.append(new_card)
                print(f"{player.name} exchanged one card for a new card from the deck.\n")

            else:
                print(f"{player.name} decided to keep both cards.\n")

        self.handle_next_turn()
        return

    def steal(self, actor, target):
        ''' Perform the steal action.
            Parameters:
                actor: Player object
                target: Player object
        '''
        if target.coins >= STEAL_GAIN:
            actor.coins += STEAL_GAIN
            target.coins -= STEAL_GAIN
        else:
            target.coins = 0
            actor.coins += target.coins

        print(f"{actor.name} stole {STEAL_GAIN} coins from {target.name}. \n")
        self.handle_next_turn()
        return
    
    #Blockable Actions: foreign aid, steal, assassinate
    def block_foreign_aid(self, target, actor):
        ''' Block the foreign aid action.
            Parameters:
                target: Player object
                actor: Player object
        '''
        print(f"{target.name} blocked {actor.name}'s foreign aid.\n")
        self.handle_next_turn()
        return
    
    def block_steal(self, actor, target):
        ''' Block the steal action.
            Parameters:
                actor: Player object
                target: Player object
        '''
        #Can't go to negative coins
        print(f"{target.name} blocked {actor.name}'s steal attempt.\n")
        self.handle_next_turn()
        return
    
    def block_assassinate(self, actor, target):
        ''' Block the assassinate action.
            Parameters:
                actor: Player object
                target: Player object
        '''
        #Can't go to negative coins
        print(f"{target.name} blocked {actor.name}'s assassination attempt.\n")
        if actor.coins >= ASSASSIN_COST:
            actor.coins -= ASSASSIN_COST
        else:
            actor.coins = 0
        self.handle_next_turn()
        return
    
    def challenge(self, challenger, target, action):
        ''' Handle a challenge for a human player or AI.
            Parameters:
                challenger: Player object
                target: Player object
                action: String
            Returns:
                Player object of the victor of the challenge
        '''
        # If target is human player, need to prompt human player to reveal a card
        victor = None
        if target == self.human_player:
            victor = self.handle_human_challenge(challenger, target, action)
        else:
            victor = self.handle_AI_challenge(challenger, target, action)
        return victor

    def handle_human_challenge(self, challenger, target, action):
        ''' Handle a challenge for a human player.
            Parameters:
                challenger: Player object
                target: Player object
                action: String
            Returns:
                Player object of the victor of the challenge
        '''
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


    def handle_AI_challenge(self, challenger, target, action):
        ''' Handle a challenge for an AI player.
            Parameters:
                challenger: Player object
                target: Player object
                action: String
            Returns:
                Player object of the victor of the challenge
        '''
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
        ''' Get the card to reveal for a challenge.
            Parameters:
                target: Player object
                action: String
            Returns:
                String representing the card to reveal
        '''
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
        ''' Eliminate a player from the game.
            Parameters:
                player: Player object
        '''
        # Remove the player from the game
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
        ''' Reveal a card belonging to a player.
            Parameters:
                player: Player object
                card: String
            Returns:
                String representing the card revealed
                None if the card was not found
        '''
        if card in player.cards:
            return card
        return None  # Card not found

    #Player should be a Player object
    def lose_influence(self, player):
        ''' Lose influence for a player.
            Parameters:
                player: Player object
            Returns:
                String representing the card lost'''

        #If human player is losing influence, prompt them to choose which card to lose(if they have more than one)
        if player == self.human_player:
            if len(player.cards) > 1:
                print(f"Which card do you want to lose? {player.cards}")
                lost_card = input("Enter a card to lose: ")
                while lost_card not in player.cards:
                    print("That card is not in your hand. Please try again.")
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

        #If AI player is losing influence, randomly choose a card to lose
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

    def is_human_player_last(self):
        ''' Check if the human player is the last player remaining.
            Returns:
                True if the human player is the last player remaining
                False otherwise
            '''
        alive_players = self.get_alive_players()
        return len(alive_players) == 1 and alive_players[0] == self.human_player

    def check_end_of_game(self):
        ''' Check if the game has ended.
            Returns:
                True if the game has ended
                False otherwise
        '''
        return self.human_player not in self.players or self.is_human_player_last()

    def reset_game(self):
        ''' Reset the game.
        '''
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
        ''' Reset the available actions for all alive players.
        '''
        for player in self.get_alive_players():
            player.available_actions = AVAILABLE_ACTIONS

    def handle_next_turn(self):
        ''' Handle the next turn.
        '''

        # Check if the game has ended
        if self.check_end_of_game():
            self.reset_game()
            return

        # Reset all available actions for all players
        self.reset_alive_players_available_actions()

        #Make sure any players who are dead cannot perform actions
        for player in self.dead_players:
            self.set_player_available_actions(player, [])

        # Set current player index to next player
        self.set_next_player_turn()

        #Allow assassinate if player has ASSASSIN COST coins
        current_player_num_coins = self.get_current_player().coins
        if current_player_num_coins >= ASSASSIN_COST:
            #Check if greater than COUP_COST, if so, allow coup
            if current_player_num_coins < COUP_COST:
                self.set_player_available_actions(self.current_player, AVAILABLE_ACTIONS  + ['assassinate'])
            else:
                self.set_player_available_actions(self.current_player, AVAILABLE_ACTIONS + ['assassinate', 'coup'])


        # If player has over COUP LIMIT coins, they must coup
        #Set available actions to only coup
        if self.get_current_player().coins >= COUP_LIMIT:
            self.set_player_available_actions(self.current_player, ['coup'])
            return
        
    def set_next_player_turn(self):
        ''' Set the next player's turn.
        '''
        if self.current_player_index == len(self.players) - 1:
            self.current_player_index = 0
            self.current_player = self.players[0]
        else:
            self.current_player_index += 1
            self.current_player = self.players[self.current_player_index]

        
        