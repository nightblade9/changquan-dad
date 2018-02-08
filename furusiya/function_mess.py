import shelve
from random import randint

import tdl

import colors
import config
from constants import *
from main_interface import Game, menu, message
from model.components.ai.base import AI
from model.components.fighter import Fighter
from model.item import Item
from model.maps.area_map import AreaMap
from model.maps.generators.forest_generator import ForestGenerator
from model.party.player import Player
from model.party.stallion import Stallion
from model.weapons import Bow
from view.renderer import render_all


def player_move_or_attack(dx, dy):

    # the coordinates the player is moving to/attacking
    x = Game.player.x + dx
    y = Game.player.y + dy

    # try to find an attackable object there
    Game.target = None
    for obj in Game.area_map.entities:
        if obj.get_component(Fighter) and obj.x == x and obj.y == y:
            Game.target = obj
            break

    # attack if target found, move otherwise
    if Game.target is not None:
        Game.player.get_component(Fighter).attack(Game.target)
    else:
        Game.player.move(dx, dy)
        Game.fov_recompute = True


def inventory_menu(header):
    # show a menu with each item of the inventory as an option
    if len(Game.inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = [item.name for item in Game.inventory]

    index = menu(header, options, INVENTORY_WIDTH)

    # if an item was chosen, return it
    if index is None or len(Game.inventory) == 0:
        return None
    return Game.inventory[index].get_component(Item)


def msgbox(text, width=50):
    menu(text, [], width)  # use menu() as a sort of "message box"


def handle_keys():
    keypress = False
    user_input = None
    while user_input is None:
        # Synchronously wait
        for event in tdl.event.get():
            if event is not None:
                user_input = event

    if event.type == 'KEYDOWN':
        user_input = event
        keypress = True
    if event.type == 'MOUSEMOTION':
        Game.mouse_coord = event.cell

    if not keypress:
        return 'didnt-take-turn'

    if user_input.key == 'ENTER' and user_input.alt:
        # Alt+Enter: toggle fullscreen
        tdl.set_fullscreen(not tdl.get_fullscreen())

    elif user_input.key == 'ESCAPE':
        return 'exit'  # exit game

    if Game.game_state == 'playing':
        # movement keys
        if user_input.key == 'UP':
            player_move_or_attack(0, -1)

        elif user_input.key == 'DOWN':
            player_move_or_attack(0, 1)

        elif user_input.key == 'LEFT':
            player_move_or_attack(-1, 0)

        elif user_input.key == 'RIGHT':
            player_move_or_attack(1, 0)
        else:
            # test for other keys
            if user_input.text == 'g':
                # pick up an item
                for obj in Game.area_map.entities:  # look for an item in the player's tile
                    obj_item = obj.get_component(Item)
                    if obj.x == Game.player.x and obj.y == Game.player.y and obj_item:
                        obj_item.pick_up()
                        break

            if user_input.text == 'i':
                # show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to ' +
                                             'use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()

            if user_input.text == 'd':
                # show the inventory; if an item is selected, drop it
                chosen_item = inventory_menu('Press the key next to an item to' +
                                             'drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()

            if user_input.text == 'f' and isinstance(Game.player.get_component(Fighter).weapon, Bow):
                # Unlimited arrows, or limited but we have arrows
                if not config.data.features.limitedArrows or \
                        (config.data.features.limitedArrows and Game.player.arrows > 0):
                    is_fired = False
                    is_cancelled = False
                    Game.draw_bowsight = True
                    Game.auto_target = True
                    render_all()  # show default targetting
                    while not is_fired and not is_cancelled:
                        for event in tdl.event.get():
                            if event.type == 'MOUSEMOTION':
                                Game.mouse_coord = event.cell
                                Game.auto_target = False
                                render_all()
                            elif event.type == 'KEYDOWN':
                                if event.key == 'ESCAPE':
                                    Game.draw_bowsight = False
                                    is_cancelled = True
                                elif event.char == 'f':
                                    if Game.target and Game.target.get_component(Fighter):
                                        is_critical = False
                                        damage_multiplier = config.data.weapons.arrowDamageMultiplier
                                        if config.data.features.bowCrits and randint(0,
                                                                                     100) <= config.data.weapons.bowCriticalProbability:
                                            damage_multiplier *= (1 + config.data.weapons.bowCriticalDamageMultiplier)
                                            if config.data.features.bowCritsStack:
                                                target_fighter = Game.target.get_component(Fighter)
                                                damage_multiplier += (
                                                    config.data.weapons.bowCriticalDamageMultiplier * target_fighter.bow_crits)
                                                target_fighter.bow_crits += 1
                                            is_critical = True
                                        Game.player.get_component(Fighter).attack(Game.target, damage_multiplier=damage_multiplier,
                                                              is_critical=is_critical)
                                        Game.player.arrows -= 1
                                        is_fired = True
                                        Game.draw_bowsight = False
                                        return ""

            return 'didnt-take-turn'


def save_game():
    # open a new empty shelve (possibly overwriting an old one) to write the game data
    with shelve.open('savegame', 'n') as savefile:
        savefile['tiles'] = Game.area_map.tiles
        savefile['entities'] = Game.area_map.entities
        savefile['player_index'] = Game.area_map.entities.index(Game.player)  # index of player in entities list
        savefile['inventory'] = Game.inventory
        savefile['game_msgs'] = Game.game_msgs
        savefile['game_state'] = Game.game_state


def load_game():
    # open the previously saved shelve and load the game data

    with shelve.open('savegame', 'r') as savefile:
        Game.area_map.tiles = savefile['tiles']
        Game.area_map.width = len(Game.area_map.tiles)
        Game.area_map.height = len(Game.area_map.tiles[0])
        Game.area_map.entities = savefile['entities']
        Game.player = Game.area_map.entities[savefile['player_index']]  # get index of player in objects list and access it
        Game.inventory = savefile['inventory']
        Game.game_msgs = savefile['game_msgs']
        Game.game_state = savefile['game_state']


def new_game():

    Game.area_map = AreaMap(MAP_WIDTH, MAP_HEIGHT)
    Game.player = Player()
    Game.stallion = Stallion(Game.player)

    # generate map (at this point it's not drawn to the screen)
    ForestGenerator(MAP_WIDTH, MAP_HEIGHT, Game.area_map)

    Game.area_map.place_on_random_ground(Game.player)
    # TODO: what if we spawned in a wall? :/
    Game.stallion.x = Game.player.x + 1
    Game.stallion.y = Game.player.y + 1
    Game.area_map.entities.append(Game.stallion)

    Game.game_state = 'playing'
    Game.inventory = []

    # create the list of game messages and their colors, starts empty
    Game.game_msgs = []

    # a warm welcoming message!
    message('Another brave knight yearns to bring peace to the land.', colors.red)

    # Gain four levels
    Game.player.gain_xp(40 + 80 + 160 + 320)


def play_game():

    player_action = None
    Game.mouse_coord = (0, 0)
    Game.fov_recompute = True
    Game.con.clear()  # unexplored areas start black (which is the default background color)

    while not tdl.event.is_window_closed():

        # draw all objects in the list
        render_all()

        # erase all objects at their old locations, before they move
        for obj in Game.area_map.entities:
            obj.clear()

        # handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            break

        # let monsters take their turn
        if Game.game_state == 'playing' and player_action != 'didnt-take-turn':
            for obj in Game.area_map.entities:
                obj_ai = obj.get_component(AI)
                if obj_ai:
                    obj_ai.take_turn()