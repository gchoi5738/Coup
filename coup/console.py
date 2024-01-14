from coup.models import CoupGame, Player
import random
import time
#make initial game settings that can easily be changed
def start_game():
   # Initialize the game
   game = CoupGame(human_player=Player("Gordon"), AI_players=[Player("AI_Bob"), Player("AI_Annie")])
   
   # Main game loop
   while not game.check_end_of_game():
       # Print the current game state
       print_game_state(game)
       if game.human_player in game.dead_players:
            print("You are dead!")
            restart = input('Do you want to play again? (yes/no) ')
            if restart.lower() == 'no':
                break
            else:
                game = CoupGame(human_player=Player("Gordon"), AI_players=[Player("AI_Bob"), Player("AI_Annie")])
              
      
       # Get the current player
       current_player = game.get_current_player()

       # If the current player is a human player, get the action from the user
       if current_player == game.human_player:
           action = input("Enter an action: ")
           target = input("Enter a target (if applicable): ")


       else:
           # Otherwise, generate a random action for the AI
           #FOR TESTING REASONS, REFERENCE ACTION LIST FOR COMPLETED AND IN PROGRESS ACTIONS
           action_list = ['income', 'foreign_aid', 'coup', 'tax', 'assassinate']
           action = random.choice(action_list)
           # Any player not in game.dead_players and not the current player
           #Remove current player from list of targets
           target = random.choice([player for player in game.players if player != current_player and player not in game.dead_players])

       # Execute the action
       game.handle_actions(actor=current_player, action=action, target=target)

        # Check if the game has ended
       if game.check_end_of_game():
            print("Game over!")
            restart = input('Do you want to play again? (yes/no) ')
            if restart.lower() == 'no':
                break
            else:
                game = CoupGame(human_player=Player("Gordon"), AI_players=[Player("AI_Bob"), Player("AI_Annie")])



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
    print(f"\nCurrent player: {game.get_current_player().name}")

    # Print the human player's information
    human_player = game.human_player
    print(f"You({human_player.name}) have {human_player.coins}{RESET} coins.")

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

    # Print the coins and number of cards of other alive players
    for player in game.players:
        if player != human_player and player not in game.dead_players:
            print(f"{player.name}'s coins: {GRAY}{player.coins}{RESET}")
            num_cards = len(player.cards)
            print(f"{player.name}'s number of cards: {num_cards}\n")

    # Print the available actions for the current player
    current_player = game.get_current_player()
    if current_player == human_player:
        print(f"Available actions for {current_player.name}: {', '.join(current_player.available_actions)}")




if __name__ == "__main__":
   start_game()
