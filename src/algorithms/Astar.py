import heapq
import copy

from src.entities.chess import ChessPuzzle
from src.algorithms.algorithm import ChessSolver

class AStarNode:
    def __init__(self, state, g, h, parent=None, action=None):
        self.state = {
            "board": [row[:] for row in state["board"]],
            "turn": state["turn"],
            "move_count": state["move_count"].copy() if state["move_count"] else None
        }
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent
        self.action = action

    def __lt__(self, other):
        if self.f == other.f:
            return self.g > other.g
        return self.f < other.f

class AStarSolver(ChessSolver):
    def __init__(self, env: ChessPuzzle):
        super().__init__(env)

        start_state = env.get_state()
        env.set_state(start_state)
        start_h = env.calculate_heuristic()
        start_node = AStarNode(start_state, 0, start_h)
        self.pq = []
        heapq.heappush(self.pq, start_node)
        self.visited = set()
        self.visited.add(self.hash_state(start_state))
        
        self.current_parent_node = None 
        self.pending_moves = []       
        self.solution_found = False
        self.final_node = None

    # def hash_state(self, state):
    #     board_tuple = tuple(tuple(row) for row in state["board"])
    #     turn = state["turn"]
        
    #     move_items = None
    #     if state.get("move_count") is not None:
    #         move_items = tuple(sorted(
    #             (f"{k[0]},{k[1]}", v) for k, v in state.get("move_count").items()
    #         ))
        
    #     return (board_tuple, turn, move_items)

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
        if self.solution_found or (not self.pq and not self.pending_moves and not self.current_parent_node):
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
                child_h = self.env.calculate_heuristic()
                
                child_node = AStarNode(
                    child_state, 
                    g=self.current_parent_node.g + 1, 
                    h=child_h, 
                    parent=self.current_parent_node, 
                    action=move
                )
                
                heapq.heappush(self.pq, child_node)
                self.visited.add(child_hash)
                return state_before_move, move
            if not self.pq:
                return None, None
            best_node = heapq.heappop(self.pq)
            if best_node.h == 0:
                print("Solution Found!")
                self.solution_found = True
                self.final_node = best_node
                return None, None 

            self.current_parent_node = best_node
            self.env.set_state(best_node.state)
            self.pending_moves = self.env.board.get_all_valid_moves()
            