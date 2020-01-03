#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction
from hlt.positionals import Position

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("K.Bot v.2")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

'''  Breakdown:
if is full: move towards shipyard or dropoff avoiding collision
if is too close to shipyard and is not full and square that its on is < 200 halite: move away
if is too close to shipyard and is not full and square is >= 200: stay and collect
if away from shipyard and is not full and square is >= 50 stay and collect
if away from shipyard and is not full and square is < 50: move to the place one square away from current location that has the highest difference in values

if can create ship: create the fucking ship
'''

stop_time = 280
stop_ship_num = 1000

while True:
    rand_move_num = 0
    # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
    #   running update_frame().
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []

    ship_num = 0

    for ship in me.get_ships():
        # rand_move_num += 1
        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.

        close_drop = me.shipyard
        for drop in me.get_dropoffs():  # sets close_drop to the closest dropoff location
            if game_map.calculate_distance(ship.position, drop.position) < game_map.calculate_distance(ship.position, close_drop.position):
                close_drop = drop


        if ship.halite_amount > 900 or (ship.halite_amount >= 300+(game_map.calculate_distance(ship.position, close_drop.position)*20)+(game.turn_number) #+(10**(1+game.turn_number//100))
                                        and game_map[ship.position].halite_amount <= 600):
            if ship.position == close_drop.position:
                command_queue.append(ship.stay_still())
            else:
                dir = game_map.naive_navigate(ship, close_drop.position)
                command_queue.append(ship.move(dir))
        elif ship.halite_amount >= 300+(game_map.calculate_distance(ship.position, close_drop.position)*20)+(game.turn_number*2) and game_map[ship.position].halite_amount > 600:
                command_queue.append(ship.stay_still())
        else:
            shipyard_dist = int(2+game.turn_number//150)   #**
            if game.turn_number == 100 and shipyard_dist == 3:
                shipyard_dist += 1

            dist = game_map.calculate_distance(ship.position, close_drop.position)
            if dist < shipyard_dist:
                rand_move = rand_move_num%4  #random.randInt(0,3)rand_move_num%4
                if ship.position == close_drop.position:
                    # rand_move_num += random.randint(0,4)
                    dir = Direction.get_all_cardinals()[random.randint(0,3)]
                    if game_map[ship.position.directional_offset(dir)].is_occupied or game_map[
                        ship.position.directional_offset(dir)].has_structure:
                        dir = game_map.naive_navigate(ship, ship.position.directional_offset(dir))
                    command_queue.append(ship.move(dir))
                else:
                    if game_map[ship.position].halite_amount > 700:
                        command_queue.append(ship.stay_still())
                    else:
                        dir = game_map.naive_navigate(ship, close_drop.position)
                        orig_dir = dir
                        if dir == Direction.North:
                            dir = Direction.South
                        elif dir == Direction.South:
                            dir = Direction.North
                        elif dir == Direction.East:
                            dir = Direction.West
                        elif dir == Direction.West:
                            dir = Direction.East
                        else:
                            rand_move_num += random.randint(0,3)
                            dir = Direction.get_all_cardinals()[rand_move]  #game.turn_number%4, ship_num%4
                        while dir is not orig_dir and (game_map[ship.position.directional_offset(dir)].is_occupied or game_map[ship.position.directional_offset(dir)].has_structure):
                            dir = random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])
                        # if game_map[ship.position.directional_offset(dir)].is_occupied or game_map[ship.position.directional_offset(dir)].has_structure:
                        #     dir = game_map.naive_navigate(ship, ship.position.directional_offset(dir))
                        command_queue.append(ship.move(dir))
            else: #ship is furth-enough away from shipyard and is collecting
                # if game_map.calculate_distance(ship.position, close_drop.position) > (shipyard_dist+2) and (len(me.get_ships()) / (len(me.get_dropoffs())+1)) >= 5 and me.halite_amount > 4500:
                #     furthest_ship = me.get_ships()[0]
                #     for ship2 in me.get_ships():
                #         if game_map.calculate_distance(ship2.position, close_drop.position) > game_map.calculate_distance(furthest_ship.position, close_drop.position):
                #             furthest_ship = ship2
                #     command_queue.append(ship.make_dropoff())
                #     # print("drop happened")   --> rework later

                if game_map[ship.position].halite_amount <= 30+(game.turn_number/7.5):
                    good_moves = []
                    for width in range(game_map.width):
                        for height in range(game_map.height):
                            pos = Position(width, height)
                            if game_map.calculate_distance(pos, close_drop.position) < (shipyard_dist+1):
                                pass
                            else:
                                if game_map[pos].is_occupied or game_map[pos].has_structure: #init position filter
                                    pass
                                else:
                                    if game_map.calculate_distance(ship.position, pos) > (shipyard_dist*2.5): #used to be 4
                                        pass
                                    else: #not near shipyard, not too far
                                        good_moves.append(pos)
                    move = good_moves[0]
                    if len(good_moves) == 0:
                        move = Direction.get_all_cardinals()[ship_num % 4]
                    else:
                        for pos2 in good_moves:  #finding best move based on halite amount and distance from current ship
                            const1 = game_map[move].halite_amount / (game_map.calculate_distance(ship.position, move) * 0.75)
                            const2 = game_map[pos2].halite_amount / (game_map.calculate_distance(ship.position, pos2) * 0.75)
                            if const2 > const1:
                                move = pos2
                    if game_map[move].halite_amount*.5 > game_map[ship.position].halite_amount:
                        command_queue.append(ship.move(game_map.naive_navigate(ship, move)))
                    else:
                        command_queue.append(ship.stay_still())
                else:
                    command_queue.append(ship.stay_still())
                # halite_curr = game_map[ship.position].halite_amount
                # if halite_curr <= 50:
                #     dir = Direction.North
                #     for direct in Direction.get_all_cardinals():
                #         halite_diff = game_map[ship.position.directional_offset(direct)].halite_amount - halite_curr
                #         halite_compare = game_map[ship.position.directional_offset(dir)].halite_amount - halite_curr
                #         if halite_curr > halite_compare:
                #             dir = direct
                #     command_queue.append(ship.move(dir))
                # else:
                #     command_queue.append(ship.stay_still())

        ship_num += 1

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if game.turn_number == stop_time:
        stop_ship_num = len(me.get_ships())

    if len(me.get_ships()) < stop_ship_num and me.halite_amount-constants.SHIP_COST > (game.turn_number*3) and \
            game.turn_number < stop_time and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
