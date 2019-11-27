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
        top_line = '  '.join(['\/'] * 6 +  ['|'] + ['\/'] * 6)
        bottom_line = '  '.join(['/\\'] * 6 + ['|'] + ['/\\'] * 6)
        top_row = ''
        bottom_row = ''
        for x in range(13, 26):
            top_row += str(int(self.checkers[x])) + '   '
        for x in range(13, 0, -1):
            bottom_row += str(int(self.checkers[x])) + '   '
        output = top_line + '\n' + top_row + '\n' + bottom_row + '\n' + bottom_line
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
        score = sum(scores) / 345
        return score

    def moves(self, state, roll, swap=False,):
        states = []
        for x in range(0, 26):
            if (state.checkers[x] > 0) == (state.player > 0) and x + roll < 25 and x + roll > 0:
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
                        new_state.checkers[x + roll] = state.player
                        new_state.checkers[25 * int(state.player < 0)]
                        if swap:
                            new_state.player *= -1
                        states.append(new_state)
        if len(states) == 0:
            return [state]
        return states
                
    def roll_dice(self):
        return random.randint(1, 6)
    
    def next_states(self, state):
        states = []
        roll1 = self.roll_dice()
        roll2 = self.roll_dice()
        moves = self.moves(state, roll1)
        for first_move in moves:
            for second_move in self.moves(first_move, roll2, swap=True):
                states.append(second_move)
        return states
    
    def simulate_game(self, verbose=False):
        history = []
        state = State()
        for x in range(50):
            states = self.next_states(state)
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
        history.reverse()
        for x in range(1, len(history)):
            val = history[x][1] * (1 - self.gamma) + history[x - 1][1] * self.gamma
            self.val[history[x][0]] = val
        
    def train(self):
        for y in range(4):
            self.simulate_game()
        self.simulate_game(verbose=True)

bkg = Engine()
bkg.train()