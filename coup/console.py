from coup.models import CoupGame, Player
import random
import time
def start_game():
   # Initialize the game
   game = CoupGame(human_player=Player("Gordon"), AI_players=[Player("AI_Bob"), Player("AI_Annie")])

   # Main game loop
   while not game.check_end_of_game():
       # Print the current game state
       print_game_state(game)

       # Get the current player
       current_player = game.get_current_player()

       # If the current player is a human player, get the action from the user
       if current_player == game.human_player:
           action = input("Enter an action: ")
           target = input("Enter a target (if applicable): ")
       else:
           # Otherwise, generate a random action for the AI
           action = random.choice(current_player.available_actions)
           target = random.choice(game.players)

       # Execute the action
       game.handle_actions(actor=current_player, action=action, target=target)

       # Wait for a second to simulate AI thinking
       time.sleep(1)

       # Make a random AI move
       game.make_random_AI_move()

def print_game_state(game):
 # Define color codes
 RED = "\033[91m"
 BLUE = "\033[94m"
 GREEN = "\033[92m"
 PURPLE = "\033[95m"
 BLACK = "\033[90m"
 GRAY = "\033[97m"
 RESET = "\033[0m"

 # Print the current player's turn
 print(f"\n\n\n\nCurrent player: {game.get_current_player().name}")

 # Print the human player's information
 human_player = game.human_player
 print(f"Human player ({human_player.name}) has {human_player.coins}{RESET} coins.")

 # Print the human player's cards
 print(f"{human_player.name}'s cards:")
 for card in human_player.cards:
    # Change the color of the card based on its type
    if card == "contessa":
        print(f"{RED}{card}{RESET}")
    elif card == "duke":
        print(f"{PURPLE}{card}{RESET}")
    elif card == "captain":
        print(f"{BLUE}{card}{RESET}")
    elif card == "ambassador":
        print(f"{GREEN}{card}{RESET}")
    elif card == "assassin":
        print(f"{BLACK}{card}{RESET}")

 # Print the coins of other players
 for player in game.players:
    if player != human_player:
        print(f"{player.name}'s coins: {GRAY}{player.coins}{RESET}")




if __name__ == "__main__":
   start_game()
