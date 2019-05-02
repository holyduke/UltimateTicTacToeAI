#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  --------------------------------
# |  0  1  2 | 9  10 11 | 18 19 20 |
# |  3  4  5 | 12 13 14 | 21 22 23 |
# |  6  7  8 | 15 16 17 | 24 25 26 |
#  --------------------------------
# | 27 28 29 | 36 37 38 | 45 46 47 |
# | 30 31 32 | 39 40 41 | 48 49 50 |
# | 33 34 35 | 42 43 44 | 51 52 53 |
#  --------------------------------
# | 54 55 56 | 63 64 65 | 72 73 74 |
# | 57 58 59 | 66 67 68 | 75 76 77 |
# | 60 61 62 | 69 70 71 | 78 79 80 |
#  --------------------------------


from math import inf
from collections import Counter
import itertools
from time import time
import os
import readchar

# clear console
clear = lambda: os.system('cls')

TIME_LIMIT = 5


def index(x, y):
    x -= 1
    y -= 1
    return ((x//3)*27) + ((x % 3)*3) + ((y//3)*9) + (y % 3)


def box(x, y):
    return index(x, y) // 9


def next_box(i):
    return i % 9


def indices_of_box(b):
    return list(range(b*9, b*9 + 9))


def print_board(state):
    clear()
    for row in range(1, 10):
        row_str = ["|"]
        for col in range(1, 10):
            row_str += [state[index(row, col)]]
            if (col) % 3 == 0:
                row_str += ["|"]
        if (row-1) % 3 == 0:
            print("-"*(len(row_str)*2-1))
        print(" ".join(row_str))
    print("-"*(len(row_str)*2-1))


def add_piece(state, move, player):
    if not isinstance(move, int):
        move = index(move[0], move[1])
    return state[: move] + player + state[move+1:]


def update_box_won(state):
    # update large total box as a single box
    temp_box_win = ["."] * 9
    for b in range(9):
        idxs_box = indices_of_box(b)
        box_str = state[idxs_box[0]: idxs_box[-1]+1]
        temp_box_win[b] = check_small_box(box_str)
    return temp_box_win


def check_small_box(box_str):
    global possible_goals
    for idxs in possible_goals:
        (x, y, z) = idxs
        if (box_str[x] == box_str[y] == box_str[z]) and box_str[x] != ".":
            return box_str[x]
    return "."

def substitute_box(state):
    for b in range(9):
        idxs_box = indices_of_box(b)
        box_str = state[idxs_box[0]: idxs_box[-1] + 1]
        won = check_small_box(box_str)
        if won == "X":
            state = state[:idxs_box[0]] + "XXXXXXXXX" + state[idxs_box[-1]+1:]
        elif won == "O":
            state = state[:idxs_box[0]] + "OOOOOOOOO" + state[idxs_box[-1]+1:]
    return state




def possible_moves(last_move):
    global box_won
    if not isinstance(last_move, int):
        last_move = index(last_move[0], last_move[1])
    box_to_play = next_box(last_move)
    idxs = indices_of_box(box_to_play)
    if box_won[box_to_play] != ".":
        pi_2d = [indices_of_box(b) for b in range(9) if box_won[b] == "."]
        possible_indices = list(itertools.chain.from_iterable(pi_2d))
    else:
        possible_indices = idxs
    return possible_indices


def successors(state, player, last_move):
    succ = []
    moves_idx = []
    possible_indexes = possible_moves(last_move)
    for idx in possible_indexes:
        if state[idx] == ".":
            moves_idx.append(idx)
            succ.append(add_piece(state, idx, player))
    return zip(succ, moves_idx)


def print_successors(state, player, last_move):
    for st in successors(state, player, last_move):
        print_board(st[0])


def opponent(p):
    return "O" if p == "X" else "X"


def evaluate_small_box(box_str, player):
    global possible_goals
    score = 0
    three = Counter(player * 3)
    two = Counter(player * 2 + ".")
    one = Counter(player * 1 + "." * 2)
    three_opponent = Counter(opponent(player) * 3)
    two_opponent = Counter(opponent(player) * 2 + ".")
    one_opponent = Counter(opponent(player) * 1 + "." * 2)

    for idxs in possible_goals:
        (x, y, z) = idxs
        current = Counter([box_str[x], box_str[y], box_str[z]])

        if current == three:
            score += 100
        elif current == two:
            score += 10
        elif current == one:
            score += 1
        elif current == three_opponent:
            score -= 100
            return score
        elif current == two_opponent:
            score -= 10
        elif current == one_opponent:
            score -= 1

    return score


def evaluate(state, last_move, player):
    global box_won
    score = 0
    score += evaluate_small_box(box_won, player) * 200
    for b in range(9):
        idxs = indices_of_box(b)
        box_str = state[idxs[0]: idxs[-1]+1]
        score += evaluate_small_box(box_str, player)
    return score


def minimax(state, last_move, player, depth, s_time):
    succ = successors(state, player, last_move)
    if succ is None:    # Konec hry
        return (state,last_move)
    else:
        best_move = (-inf, None)
        for s in succ:
            val = min_turn(s[0], s[1], opponent(player), depth-1, s_time,
                           -inf, inf)
            if val > best_move[0]:
                best_move = (val, s)
    #        print("val = ", val)
    #        print_board(s[0])
        return best_move[1]


def min_turn(state, last_move, player, depth, s_time, alpha, beta):
    global box_won
    if depth <= 0 or check_small_box(box_won) != ".":# or time() - s_time >= 10:
        return evaluate(state, last_move, opponent(player))
    succ = successors(state, player, last_move)
    for s in succ:
        val = max_turn(s[0], s[1], opponent(player), depth-1, s_time,
                       alpha, beta)
        if val < beta:
            beta = val
        if alpha >= beta:
            break
    return beta


def max_turn(state, last_move, player, depth, s_time, alpha, beta):
    global box_won
    if depth <= 0 or check_small_box(box_won) != ".":# or time() - s_time >= 20:
        return evaluate(state, last_move, player)
    succ = successors(state, player, last_move)
    for s in succ:
        val = min_turn(s[0], s[1], opponent(player), depth-1, s_time,
                       alpha, beta)
        if alpha < val:
            alpha = val
        if alpha >= beta:
            break
    return alpha


def valid_input(state, move):
    global box_won
    if not (0 < move[0] < 10 and 0 < move[1] < 10):
        return False
    if box_won[box(move[0], move[1])] != ".":
        return False
    if state[index(move[0], move[1])] != ".":
        return False
    return True


def move_cursor(state, pos):
    user_state = add_piece(state, pos, "_")
    print_board(user_state)
    # print(pos)


def take_input2(state, bot_move):
    all_open_flag = False
    posx = 1
    posy = 1
    move_cursor(state, (posy, posx))

    if bot_move == -1 or len(possible_moves(bot_move)) > 9:
        all_open_flag = True
    if all_open_flag:
        # clear()
        print("Play anywhere you want!")
    else:
        box_dict = {0: "Upper Left", 1: "Upper Center", 2: "Upper Right",
                    3: "Center Left", 4: "Center", 5: "Center Right",
                    6: "Bottom Left", 7: "Bottom Center", 8: "Bottom Right"}
        print("Where would you like to place 'X' in ~"
              + box_dict[next_box(bot_move)] + "~ box?")

    while True:
        key = readchar.readkey()
        if key == '\x1b[C':  # doprava
            posx += 1
        elif key == '\x1b[D':  # doleva
            posx -= 1
        elif key == '\x1b[B':  # dolu
            posy += 1
        elif key == '\x1b[A':  # nahoru
            posy -= 1

        # Check border positions
        if posx == 10:
            posx = 1
        elif posx == 0:
            posx = 9
        elif posy == 10:
            posy = 1
        elif posy == 0:
            posy = 9

        move_cursor(state, (posy, posx))

        if bot_move == -1 or len(possible_moves(bot_move)) > 9:
            all_open_flag = True
        if all_open_flag:
            # clear()
            print("Play anywhere you want!")
        else:
            box_dict = {0: "Upper Left", 1: "Upper Center", 2: "Upper Right",
                        3: "Center Left", 4: "Center", 5: "Center Right",
                        6: "Bottom Left", 7: "Bottom Center", 8: "Bottom Right"}
            print("Where would you like to place 'X' in ~"
                  + box_dict[next_box(bot_move)] + "~ box?")

        # Enter pressed
        if key == '\r':  # enter
            break

    if bot_move != -1 and index(posy, posx) not in possible_moves(bot_move):
        raise ValueError
    if not valid_input(state, (posy, posx)):
        raise ValueError
    return (posy, posx)


def game(state="." * 81, depth=5):
    global box_won, possible_goals
    possible_goals = [(0, 4, 8), (2, 4, 6)]
    possible_goals += [(i, i+3, i+6) for i in range(3)]
    possible_goals += [(3*i, 3*i+1, 3*i+2) for i in range(3)]
    box_won = update_box_won(state)
    # print_board(state)
    bot_move = -1

    while True:
        # PLAYER MOVE
        try:
            user_move = take_input2(state, bot_move)
        except ValueError:
            print("Invalid input or move not possible!")
            print_board(state)
            continue
        except SystemError:
            print("Game Stopped!")
            break

        # Update piece
        user_state = add_piece(state, user_move, "X")

        # Substitute matrix if won
        user_state = substitute_box(user_state)
        print_board(user_state)

        # Check for end game
        box_won = update_box_won(user_state)
        game_won = check_small_box(box_won)
        if game_won != ".":
            state = user_state
            break

        # BOT MOVE
        print("Please wait, Bot is thinking...")
        s_time = time()
        bot_state, bot_move = minimax(user_state, user_move, "O", depth,
                                      s_time)

        print("#" * 40)
        print("Bot placed 'O' on", bot_move, "\n")
        bot_state = substitute_box(bot_state)  # substitute if box won
        print_board(bot_state)

        # Check for end game
        state = bot_state
        box_won = update_box_won(bot_state)
        game_won = check_small_box(box_won)
        if game_won != ".":
            break

    if game_won == "X":
        print("$$$$$ Congratulations YOU WIN! $$$$$")
    else:
        print("~~~~~ YOU LOSE! ~~~~~")

    return state


if __name__ == "__main__":
    INITIAL_STATE = "." * 81
    final_state = game(INITIAL_STATE, depth=5)
