# Coup/coup/app.py
from flask import Flask, render_template, request, redirect, url_for

from . import app  # Adjust the import statement
from .models import CoupGame, Player

game = CoupGame([Player("Player1"), Player("AI1"), Player("AI2")])
action_log = []

@app.route('/')
def index():
    current_player = game.get_current_player()
    players = game.players
    return render_template('index.html', current_player=current_player, players=players, action_log=action_log)

@app.route('/perform_action', methods=['POST'])
def perform_action():
    action = request.form.get('action')
    target = request.form.get('target')
    current_player = game.get_current_player()

    if action:
        if target:
            target_player = game.get_player_by_name(target)
            game.perform_action(current_player, target_player, action)
            action_log.append(f"{current_player.name} chose to {action} {target_player.name}")
        else:
            game.perform_action(current_player, None, action)
            action_log.append(f"{current_player.name} chose to {action}")

    game.next_turn()
    return redirect(url_for('index'))

@app.route('/reset_game', methods=['GET'])
def reset_game():
    global game, action_log
    game.reset_game()
    action_log = []  # Clear the action log
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
