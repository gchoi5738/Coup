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
    def __init__(self, players):
        self.players = players
        self.deck = ["contessa", "duke", "captain", "ambassador", "assassin"] * 3
        self.shuffle_deck()
        self.current_player_index = 0  # Index of the current player in the players list

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def get_current_player(self):
        return self.players[self.current_player_index]

    def get_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        return None  # Player not found

    def perform_action(self, actor, target, action):
        if action == "income":
            self.income(actor)
        elif action == "foreign_aid":
            self.foreign_aid(actor)
        elif action == "coup":
            self.coup(actor, target)
        elif action == "tax":
            self.tax(actor)
        elif action == "assassinate":
            self.assassinate(actor, target)
        elif action == "exchange":
            self.exchange(actor)
        elif action == "steal":
            self.steal(actor, target)

    def income(self, player):
        player.coins += 1

    def foreign_aid(self, player):
        player.coins += 2

    def coup(self, actor, target):
        if actor.coins >= 7:
            actor.coins -= 7
            self.eliminate_player(target)

    def tax(self, player):
        player.coins += 3

    def assassinate(self, actor, target):
        if actor.coins >= 3:
            actor.coins -= 3
            self.eliminate_player(target)

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
        # You might want to add additional logic for handling stealing cards, if applicable

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
            return lost_card
        return None  # No influence to lose

    def block_action(self, blocker, actor, claimed_action):
        actual_action = self.get_actual_action(actor, claimed_action)
        if actual_action and actual_action == claimed_action:
            self.eliminate_player(blocker)

    def get_actual_action(self, player, claimed_action):
        # Check if the claimed action can be challenged or blocked
        if claimed_action in ["tax", "assassinate", "steal"]:
            return self.challenge_or_block(player, claimed_action)
        return claimed_action

    def challenge_or_block(self, player, claimed_action):
        # Simulate a challenge or block
        challenge_target = random.choice(self.players)
        if challenge_target == player:
            challenge_target = self.get_other_player(player)
        if random.choice([True, False]):  # Randomly decide if it's challenged or blocked
            return self.challenge(player, challenge_target, claimed_action)
        else:
            return self.block_action(player, challenge_target, claimed_action)
        
    def get_other_player(self, player):
        # Get another player that is not the specified player
        for other_player in self.players:
            if other_player != player:
                return other_player
        return None

    def check_end_of_game(self):
        # Check if the game has ended
        return len(self.players) == 1

    def reset_game(self):
        # Reset the game state for a new round
        self.shuffle_deck()
        for player in self.players:
            player.coins = 2
            player.cards = []

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

# ... (other methods and game logic)
