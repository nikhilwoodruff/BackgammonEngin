import random
import numpy as np
import copy

class State:
    def __init__(self, default=True):
        self.player = 1
        if default:
            self.checkers = self.default_checkers()
        else:
            self.checkers = None
        self.states = []
    
    def default_checkers(self):
        checkers = np.zeros((26))
        positions = [(1, 2), (12, 5), (17, 3), (19, 5)]
        for x, y in positions:
            checkers[x] = y
            checkers[25 - x] = -y
        return checkers
    
    def copy(self):
        state = State(default=False)
        state.player = self.player
        state.checkers = self.checkers.copy()
        state.states = copy.deepcopy(self.states)
        return state
    
    def render(self):
        num_top = '  '.join(map(str, range(13, 26)))
        num_bottom = '   '.join(map(str, range(12, -1, -1)))
        top_line = '  '.join(['\/'] * 6 +  ['|'] + ['\/'] * 6 + ['--'])
        bottom_line = '  '.join(['/\\'] * 6 + ['|'] + ['/\\'] * 6 + ['--'])
        top_row = ''
        bottom_row = ''
        for x in range(13, 26):
            top_row += str(int(self.checkers[x])) + '   '
            if x == 18:
                top_row += '|'
        for x in range(12, -1, -1):
            bottom_row += str(int(self.checkers[x])) + '   '
            if x == 7:
                bottom_row += '|'
        output = num_top + '\n' + top_line + '\n' + top_row + '\n' + bottom_row + '\n' + bottom_line + '\n' + num_bottom
        print(output)

class Engine:
    def __init__(self):
        self.gamma = 1e-1
        self.val = {}
    
    def eval(self, state):
        scores = [0, 0]
        for x in range(25):
            if state.checkers[x] > 0:
                scores[0] += x * state.checkers[x]
            else:
                scores[1] += (25 - x) * state.checkers[x]
        score = sum(scores) / 345 + self.terminal_check(state)
        return score
    
    def terminal_check(self, state):
        win = True
        for x in range(19):
            if state.checkers[x] > 0:
                win = False
        if win:
            return 2
        loss = True
        for x in range(25, 6, -1):
            if state.checkers[x] < 0:
                loss = False
        if loss:
            return -2
        return 0

    def moves(self, state, roll, swap=False,):
        states = []
        points = list(range(26))
        if state.checkers[25 * int(state.player < 0)] != 0:
            points = [25 * int(state.player < 0)]
        for x in points:
            if (state.checkers[x] > 0) == (state.player > 0) and (state.checkers[x] < 0) == (state.player < 0) and x + roll < 25 and x + roll > 0:
                if state.checkers[x + roll]  == state.player * abs(state.checkers[x + roll]) or state.checkers[x + roll] == 0:
                    if abs(state.checkers[x + roll]) < 5:
                        new_state = state.copy()
                        new_state.checkers[x] -= state.player
                        new_state.checkers[x + roll] += state.player
                        if swap:
                            new_state.player *= -1
                        states.append(new_state)
                else:
                    if abs(state.checkers[x + roll]) == 1:
                        new_state = state.copy()
                        new_state.checkers[x] -= state.player
                        new_state.checkers[x + roll] = state.player
                        new_state.checkers[25 * int(state.player > 0)] -= state.player
                        if swap:
                            new_state.player *= -1
                        states.append(new_state)
        if len(states) == 0:
            return [state]
        return states
                
    def roll_dice(self):
        return random.randint(1, 6)
    
    def next_states(self, state, verbose=False, roll1=None, roll2=None):
        states = []
        if roll1 == None:
            roll1 = self.roll_dice()
        if roll2 == None:
            roll2 = self.roll_dice()
        moves = self.moves(state, roll1 * state.player)
        if verbose:
            print('Rolled: ' + str(roll1) + ', ' + str(roll2), ', turn: ' + str(int(state.player)))
        for first_move in moves:
            for second_move in self.moves(first_move, roll2 * state.player, swap=True):
                states.append(second_move)
        return states
    
    def simulate_game(self, max_turns=128, verbose=False):
        state = State()
        if verbose:
            state.render()
        history = [(state, 0)]
        for x in range(max_turns):
            states = self.next_states(state, verbose)
            action = None
            for st in states:
                if st not in self.val:
                    self.val[st] = self.eval(st)
                if action == None:
                    action = (st, self.val[st])
                elif (self.val[st] - action[1]) * state.player > 0:
                    action = (st, self.val[st])
            state = action[0]
            history.append(action)
            if verbose:
                state.render()
            if abs(action[1]) > 1:
                x = max_turns
        history.reverse()
        for x in range(1, len(history)):
            val = history[x][1] * (1 - self.gamma) + history[x - 1][1] * self.gamma
            self.val[history[x][0]] = val
    
    def play_game_second(self, max_turns=int(1e+3)):
        state = State()
        state.render()
        history = [(state, 0)]
        for x in range(max_turns):
            states = self.next_states(state, False, roll1=int(input('Enter r1: ')), roll2=int(input('Enter r2: ')))
            action = None
            for st in states:
                if st not in self.val:
                    self.val[st] = self.eval(st)
                if action == None:
                    action = (st, self.val[st])
                elif (self.val[st] - action[1]) * state.player > 0:
                    action = (st, self.val[st])
            state = action[0]
            history.append(action)
            state.render()
            if abs(action[1]) > 1:
                print('You lose.')
                x = max_turns
            next_state = state.copy()
            next_state.checkers[int(input('Enter first move from: '))] += 1
            to_loc = int(input('Enter first move to: '))
            if next_state.checkers[to_loc] == 1:
                next_state.checkers[to_loc] = -1
                next_state.checkers[0] += 1
            else:
                next_state.checkers[to_loc] -= 1
            next_state.checkers[int(input('Enter first move from: '))] += 1
            to_loc = int(input('Enter first move to: '))
            if next_state.checkers[to_loc] == 1:
                next_state.checkers[to_loc] = -1
                next_state.checkers[0] += 1
            else:
                next_state.checkers[to_loc] -= 1
            state = next_state
            history.append((state, self.eval(state)))
            state.render()
            if abs(action[1]) > 1:
                print('You win.')
                x = max_turns
        history.reverse()
        for x in range(1, len(history)):
            val = history[x][1] * (1 - self.gamma) + history[x - 1][1] * self.gamma
            self.val[history[x][0]] = val

    def train(self):
        for y in range(2):
            self.simulate_game()
        print('Dataset size: ' + str(len(self.val)))
        self.play_game_second()

bkg = Engine()
bkg.train()