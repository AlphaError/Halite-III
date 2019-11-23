#!/usr/bin/env python3
# Python 3.6
# Product of Kora S. Hughes

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
game.ready("K.Bot v.1")

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

# Kora's Stuff
def find_best_move(move_list):
    curr_move = moves[0]
    for move in moves:
        if curr_move[1] < move[1]:
            curr_move = move
    good_moves = []
    for move in moves:
        if curr_move[1] == move[1]:
            good_moves.append(move)
    curr_move = good_moves[random.randint(0, len(good_moves)-1)]
    return curr_move[0]

def add_move_affinity(move_list, possibility, amt):
    for move in move_list:
        if move[0] == possibility:
            move[1] += amt

while True:
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
    game_area = game_map.height * game_map.width
    for ship in me.get_ships():
        hasCommand = False
        ship_num += 1
        #moves is an array of all possible moves of a ship where the second index of each nested array is a value of affinity of said ship to do that move
        moves = [ [ship.move(Direction.North), 0], [ship.move(Direction.South), 0], [ship.move(Direction.East), 0], [ship.move(Direction.West), 0], [ship.stay_still(), 0], [ship.make_dropoff(), -5] ]

        # ship_move = random.choice([ ship.move(Direction.North), ship.move(Direction.South), ship.move(Direction.East), ship.move(Direction.West), ship.stay_still() ])

        '''for direct in Direction.get_all_cardinals(): #reduces chances of running into each other :)
            for ship2 in me.get_ships():
                if ship.position.directional_offset(direct) is ship2.position:
                    add_move_affinity(moves, direct, -20)

        # For each of your ships, move randomly if the ship is on a low halite location
        # if the ship is full go back to the dropoff
        #   Else, collect halite aka standing still
        if ship.is_full:
            close_drop = None
            for drop in me.get_dropoffs():  # sets close_drop to the closest dropoff location
                if close_drop is None:
                    close_drop = drop
                elif game_map.calculate_distance(ship.position, drop) < game_map.calculate_distance(ship.position,
                                                                                                    close_drop):
                    close_drop = drop
            add_move_affinity(moves, game_map.naive_navigate(ship, close_drop),
                              10)  # plus 10% chance to move to the navigated location
        elif game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 and not ship.is_full:
            # command_queue.append( ship.move( random.choice([ Direction.North, Direction.South, Direction.East, Direction.West ])))
            for direct in Direction.get_all_cardinals():
                add_move_affinity(moves, direct, 10)
        else:
            add_move_affinity(moves, ship.stay_still(), 20)'''

        if game.turn_number <= 15:
            if ship_num == 1:
                add_move_affinity(moves, Direction.North, 40)
            if ship_num == 2:
                add_move_affinity(moves, Direction.South, 40)
            if ship_num == 3:
                add_move_affinity(moves, Direction.East, 40)
            if ship_num == 4:
                add_move_affinity(moves, Direction.West, 40)

        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        for direct in Direction.get_all_cardinals():  # reduces chances of running into each other :)
            pos = ship.position.directional_offset(direct)
            if game_map[pos].is_occupied:
                add_move_affinity(moves, direct, -10000)

        if me.halite_amount > 4000 and 1 < len(me.get_ships()) < 5 and len(me.get_dropoffs()) / len(me.get_ships()) <= .5:
            add_move_affinity(moves, ship.make_dropoff(), 40)

        if ship.halite_amount >= 500:
            close_drop = me.shipyard
            # for drop in me.get_dropoffs():  # sets close_drop to the closest dropoff location
            #     if game_map.calculate_distance(ship.position, drop.position) < game_map.calculate_distance(ship.position, close_drop.position):
            #         close_drop = drop
            # if close_drop.position is ship.position:
            #     add_move_affinity(moves, ship.stay_still(), 30)
            # else:
            add_move_affinity(moves, game_map.naive_navigate(ship, close_drop.position), 600)  # plus 10% chance to move to the navigated location
            # command_queue.append(ship.stay_still())
            # hasCommand = True
        else:
            if game_map.calculate_distance(ship.position, me.shipyard.position) <= 2:
                for direct in Direction.get_all_cardinals():
                    add_move_affinity(moves, ship.move(direct), 80)

            if game_map[ship.position].halite_amount > 50:
                add_move_affinity(moves, ship.stay_still(), 300)

            for width in range(game_map.width):
                for height in range(game_map.height):
                    pos = Position(width, height)
                    if not game_map[pos].is_occupied and not game_map[pos].has_structure:
                        ratio = game_map[pos].halite_amount / constants.MAX_HALITE
                        dist = game_map.calculate_distance(ship.position, pos)
                        if dist < 10:
                            add_move_affinity(moves, game_map.naive_navigate(ship, pos), 25*ratio + 6*(1 - (dist / (game_map.height + game_map.width))))

            max_dir = Direction.North
            for direct in Direction.get_all_cardinals():
                pos1 = ship.position.directional_offset(direct)
                pos2 = ship.position.directional_offset(max_dir)
                if game_map[pos1].halite_amount > game_map[pos2].halite_amount:
                    max_dir = direct
            add_move_affinity(moves, ship.move(max_dir), 30)

            if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10:
                ratio = game_map[ship.position].halite_amount / constants.MAX_HALITE
                inverse_r = 1 - ratio
                for direct in Direction.get_all_cardinals():
                    add_move_affinity(moves, direct, 4*inverse_r)
            else:
                add_move_affinity(moves, ship.stay_still(), 10)
        if not hasCommand:
            command_queue.append(find_best_move(moves))

    # If the game is in the first 200 turns and you have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
    if me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

