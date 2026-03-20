import collections
import copy

from src.entities.chess import ChessPuzzle
from src.algorithms.algorithm import ChessSolver

class BFSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = copy.deepcopy(state)
        self.parent = parent
        self.action = action

class BFSSolver(ChessSolver):
    def __init__(self, env: ChessPuzzle):
        super().__init__(env)

        start_state = env.get_state()
        env.set_state(start_state)
        
        start_node = BFSNode(start_state)
        self.queue = collections.deque([start_node])
        self.visited = set()
        
        self.visited.add(self.hash_state(start_state))
        
        self.current_parent_node = None 
        self.pending_moves = []       
        self.solution_found = False
        self.final_node = None

        if self.env.calculate_heuristic(start_state) == 0:
            self.solution_found = True
            self.final_node = start_node

    def hash_state(self, state):
        flat_board = tuple(item for row in state["board"] for item in row)
        
        turn = state["turn"]
        move_items = None
        if state.get("move_count") is not None:
            move_items = frozenset(
                (k, v) for k, v in state["move_count"].items() if v > 0
            )
            
        return (flat_board, turn, move_items)
    
    def take_action(self):
        if self.solution_found or (not self.queue and not self.pending_moves and not self.current_parent_node):
            return None, None 

        while True:
            if self.current_parent_node and self.pending_moves:
                move = self.pending_moves.pop(0)

                self.env.set_state(self.current_parent_node.state)
                state_before_move = self.env.get_state()
                self.env.step(move)
                
                child_state = self.env.get_state()
                child_hash = self.hash_state(child_state)
                
                if child_hash in self.visited:
                    continue
                
                self.visited.add(child_hash)
                child_node = BFSNode(
                    child_state, 
                    parent=self.current_parent_node, 
                    action=move
                )
                self.queue.append(child_node)
                if self.env.calculate_heuristic(child_state) == 0:
                    print("Solution Found!")
                    self.solution_found = True
                    self.final_node = child_node
                    return state_before_move, move

                return state_before_move, move
            if not self.queue:
                return None, None 
            best_node = self.queue.popleft()
            
            self.current_parent_node = best_node
            self.env.set_state(best_node.state)
            self.pending_moves = self.env.board.get_all_valid_moves()