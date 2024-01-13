# Coup/coup/app.py
from flask import Flask, render_template, request, redirect, url_for

from . import app
from .models import CoupGame, Player

#Initialize game
    #Please Note: Only one player can be playable at a time
game = CoupGame(human_player = Player("Player"), 
                AI_players = [Player("AI_Bob"), Player("AI_Annie")])

action_log = []

@app.route('/')
def index():
    current_player = game.get_current_player()
    human_player = game.human_player
    AI_players = game.AI_players
    return render_template('index.html', human_player=human_player,
                                         AI_players=AI_players,
                                         current_player=current_player, 
                                         action_log=action_log)

@app.route('/perform_action', methods=['POST'])
def perform_action():
    action = request.form.get('action')
    target = request.form.get('target')
    current_player = game.get_current_player()



    #Handle all incoming actions
    game.handle_actions(action, target)
    
    #Actions should be determined to be challenged before any blocking occurs
        #Challengable actions are: Tax, Assassinate, Steal, Exchange, blockable actions

    return redirect(url_for('index'))

@app.route('/reset_game', methods=['GET'])
def reset_game():
    global game, action_log
    game.reset_game()
    action_log = []  # Clear the action log
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
