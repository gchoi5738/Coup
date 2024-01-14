# Coup
names have to be unique
one playable character

Player is allowed to challenge before the AI do

HAVE TO COUP IF IT IS YOUR TURN AND YOU HAVE 10 or more coins


Determining Action Options

    - After a challengable action is declared, the person declaring the action cannot challenge

    - A target has the ability to block an action from an actor if no challenges present
    - If it is your turn and you have more than 10 coins, only option is to coup
    - If a challenge occurs, one player will lose an influence. The defender must produce the 
            right influence card for their action, else they lose an influence of their choice

        - essentially, options are to reveal relevant card or lose one for defender
        - challenger's only options are to choose a card to lose if the challenge is defended

Block has to be an action

Challenges:
    - You can't block an action that was challenged unsuccessfully
    - four actions can be challenged(influence cards), blocks can be challenged
    - Player can challenge first

Income:
    - Options for other players: None
    - easy

Block:
    - Options for other players: Challenge

Foreign Aid:
    - Options for other players: Block

    - You can't block your own foreign aid
    - You can challenge someone else's block

    P1, P2, P3

        P1 chooses to foreign aid
            CoupGame:
                current_turn_actions = ['foreign_aid']
            P1:
                actions = ['Nothing']
            P2:
                actions = ['Block']
            P3:
                actions = ['Block']
            Action:
                name = 'foreign_aid'
                actor = P1
                target = None
                benefit = 2 coins
                cost = None
        
        P2 chooses to block P1
            CoupGame:
                current_turn_actions = ['foreign_aid', 'block']
            P1:
                actions = ['Challenge', 'Allow']
            P2:
                actions = ['Nothing']
            P3:
                actions = ['Challenge', 'Allow']
            Action:
                name = 'block'
                actor = P2
                target = P1
                benefit = Delete foreign aid
                cost = None
        
        P1 chooses to challenge P2
            CoupGame:
                    current_turn_actions = ['foreign_aid', 'block', 'challenge']
            P1:
                actions = ['Nothing']
            P2:
                actions = ['Show challenged card', 'Allow']
            P3:
                actions = ['Nothing']
            Action:
                name = 'challenge'
                actor = P1
                target = P2
                benefit = P2 loses influence
                cost = P1 loses influence

            IF CHALLENGE IS SUCCESSFUL
                CoupGame:
                    current_turn_actions = ['foreign_aid', 'block', 'challenge', 'allow']
                P1:
                    actions = ['Nothing']
                P2:
                    actions = ['Choose Influence to Lose']
                P3:
                    actions = ['Nothing']
            
            IF CHALLENGE IS UNSUCCESSFUL
                CoupGame:
                    current_turn_actions = ['foreign_aid', 'block', 'challenge', 'challenge defended']
                P1:
                    actions = ['Choose Influence to Lose']
                P2:
                    actions = ['Nothing']
                P3:
                    actions = ['Nothing']
        
        Next Turn is calculated
            IF CHALLENGE IS SUCCESSFUL, foreign aid is executed
                CoupGame:
                    current_turn_actions = ['foreign_aid']
                exec foreign_aid logic
                next_turn()

            IF CHALLENGE IS UNSUCCESSFUL, foreign aid is blocked
                CoupGame:
                    current_turn_actions = ['foreign_aid', 'block']
                    exec block logic:
                        (execute cost of blocked action)
                    next_turn()



P1: Human, P2: AI, P3: AI
P2 foreign aid
    CoupGame:
        current_turn_actions = [{action: 'foreign_aid', actor: 'P2', target: 'None'}]
    P1:
        actions = ['block_foreign_aid', 'allow']
    P2:
        actions = ['nothing']
    P3:
        actions = ['block_foreign_aid', 'allow']

P3 blocks foreign aid of P2
    CoupGame:
        current_turn_actions = [{action: 'foreign_aid', actor: 'P2', target: 'None'}, {action: 'block_foreign_aid', actor: P3, target: P2}]
    P1:
        actions = ['challenge', 'allow']
    P2:
        actions = ['challenge', 'allow']
    P3:
        actions = ['nothing']
        
P1 challenges P3's block foreign aid of P2
    CoupGame:
        current_turn_actions = [{action: 'foreign_aid', actor: 'P2', target: 'None'}, {action: 'block_foreign_aid', actor: P3, target: P2},
                                {action: 'challenge', actor:'P1', target: P3}]
    






    class Action:
       def  __init__(name):
            self.name = name
            #Player Objects
            self.actor = actor
            self.target = target
            ##################
            




WHAT DOES HUMAN PLAYER NEED TO DO:
    - ON CURRENT TURN:
        ["income", "foreign_aid", "tax", "assassinate", "exchange", "steal"] including 'coup' if 7 coins or more
    - IF CURRENT TURN IS NOT HUMAN PLAYER
        - Check for any moves available to the player
            -Challenges, allow, block
    - Else, keep doing AI moves