import numpy as np
from src.entities.figure import *

class ChessRangerBoard(Board): 
    pass
    
class ChessMeleeBoard(Board):
    def __init__(self, board: list[list[int]] = [[0 for _ in range(8)] for _ in range(8)]) -> None:
        super().__init__(board)
        self.waiting_turn: bool = True

    def is_valid_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        if not super().is_valid_move(from_pos, to_pos):
            return False
        piece = self.board[from_pos[0]][from_pos[1]]
        target = self.board[to_pos[0]][to_pos[1]]
        if piece.get_color() == target.get_color():
            return False
        return True

    def move_piece(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        piece = self.board[from_pos[0]][from_pos[1]]
        if piece is None: return False

        if self.waiting_turn != piece.get_color():
            return False

        if self.is_valid_move(from_pos, to_pos):
            self.waiting_turn = not self.waiting_turn    
            self.board[to_pos[0]][to_pos[1]] = self.board[from_pos[0]][from_pos[1]]
            self.board[from_pos[0]][from_pos[1]] = None
            return True
            
        return False

    def get_all_valid_moves(self, specific_pos=None):
        moves = []
        
        def scan_moves(r, c):
            piece = self.board[r][c]
            if piece is not None and piece.get_color() == self.waiting_turn:
                 for tr in range(8):
                    for tc in range(8):
                        if self.is_valid_move((r, c), (tr, tc)):
                            moves.append((r, c, tr, tc))

        if specific_pos:
            scan_moves(specific_pos[0], specific_pos[1])
        else:
            for r in range(8):
                for c in range(8):
                    scan_moves(r, c)
                    
        return moves


class ChessSoloBoard(Board):
    def __init__(self, board: list[list[int]] = [[0 for _ in range(8)] for _ in range(8)]) -> None:
        super().__init__(board)
        
        self.move_count: dict[tuple[int, int], int] = {}
        
        self._initialize_move_count()
        
    def get_piece_move_count(self, pos: tuple[int, int]) -> int:
        """Lấy số lần đã di chuyển của quân tại vị trí pos"""
        return self.move_count.get(pos, 0)

    def _initialize_move_count(self) -> None:
        self.move_count = {}
        for r in range(8):
            for c in range(8):
                if self.board[r][c] is not None:
                    self.move_count[(r, c)] = 0

    def import_board(self, board: list[list[int]]) -> None:
        super().import_board(board)
        self._initialize_move_count()
    def is_valid_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        r1, c1 = from_pos
        r2, c2 = to_pos
        
     
        if not (0 <= r1 < 8 and 0 <= c1 < 8 and 0 <= r2 < 8 and 0 <= c2 < 8):
            return False
        
        piece = self.board[r1][c1]
        target = self.board[r2][c2]
        
    
        if piece is None or target is None:
            return False
   
        if piece_to_int[type(target)] == 6: 
            return False  
        
        
        if self.move_count.get(from_pos, 0) >= 2:

            return False
        
        move_delta = (r2 - r1, c2 - c1)

        if not piece.is_legal_move(move_delta):
            return False

        if not self.is_path_clear(from_pos, to_pos):
            return False
        
        return True
    def get_all_valid_moves(self, specific_pos: tuple[int, int] | None = None) -> list[tuple[int, int, int, int]]:
        moves = []
        
        if specific_pos:
            r, c = specific_pos
            if self.board[r][c] is not None:
                for tr in range(8):
                    for tc in range(8):
                        if self.is_valid_move((r, c), (tr, tc)):
                            moves.append((r, c, tr, tc))
            return moves
        
        for r in range(8):
            for c in range(8):
                if self.board[r][c] is not None:
                    for tr in range(8):
                        for tc in range(8):
                            if self.is_valid_move((r, c), (tr, tc)):
                                moves.append((r, c, tr, tc))
        return moves
    
    def move_piece(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        print(f"\n=== MOVE PIECE DEBUG ===")
        print(f"From: {from_pos}, To: {to_pos}")
        print(f"move_count before anything: {dict(self.move_count)}")
        
        if not self.is_valid_move(from_pos, to_pos):
            print("Invalid move!")
            return False
        
        print(f"Move is valid!")
        if not self.is_valid_move(from_pos, to_pos):
            return False
        
        r1, c1 = from_pos
        r2, c2 = to_pos
        self.move_count[from_pos] = self.move_count.get(from_pos, 0) + 1
        print(self.move_count.get(from_pos, 0))
       
        self.board[r2][c2] = self.board[r1][c1]
        self.board[r1][c1] = None
        self.move_count[(r2, c2)] = self.move_count.pop(from_pos)
        print(self.move_count[(r2, c2)])
        
        
        return True


MODE={
    "ranger": {
        "class":ChessRangerBoard,
        "default_board": [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 4, 0, 0, 3, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 3, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    },
    "melee": {
        "class":ChessMeleeBoard,
        "default_board": [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 4, -5, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, -3, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    },
    "solo":{
        "class":ChessSoloBoard,
        "default_board": [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 4, 0, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 6, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
    }
} 
 
class ChessPuzzle:
    def __init__(self, mode, board_layout: list[list[int]] | dict | None = None):
        super().__init__()
        if mode not in MODE:
            mode = "ranger"

        layout = None
        turn = None
        count = None
        if isinstance(board_layout, dict):
            layout = board_layout["board"]
            turn = board_layout.get("turn")
            count= board_layout.get("move_count")
            self.initial_board_layout = board_layout
        else:
            if board_layout is None:
                board_layout = MODE[mode]["default_board"]
            layout = board_layout
            self.initial_board_layout = board_layout

        self.board = MODE[mode]["class"](layout)

        if turn is not None and hasattr(self.board, "waiting_turn"):
            self.board.waiting_turn = turn
        if count is not None and hasattr(self.board, "move_count"):
            self.board.move_count = count
    def step(self, action: tuple[int, int, int, int]):
        success = self.board.move_piece((action[0], action[1]), (action[2], action[3]))
        
        reward = 0
        done = False
        info = {}
        if not success:
            reward = -10
        else:
            reward = 1
            piece_count = self.board.count_pieces()
            
            if piece_count == 1:
                
                reward = 100
                done = True
                info['msg'] = "Solved!"
            elif piece_count > 1:
                all_moves = self.board.get_all_valid_moves()
                
                if len(all_moves) == 0:
                    reward = -50
                    done = True
                    info['msg'] = "Dead End"    
        return self.get_observation(), reward, done, info

    def reset(self, board_layout: list[list[int]] | dict | None = None):
        if board_layout is None:
            board_layout = self.initial_board_layout
            
        layout = board_layout
        turn = None
        count = None

        if isinstance(board_layout, dict):
            layout = board_layout["board"]
            turn = board_layout.get("turn")
            count = board_layout.get("move_count")
        self.board.import_board(layout)
        
        if turn is not None and hasattr(self.board, "waiting_turn"):
            self.board.waiting_turn = turn
        elif hasattr(self.board, "waiting_turn"):
            self.board.waiting_turn = True
        if count is not None and hasattr(self.board, "move_count"):
            self.board.move_count = count
    def get_observation(self):
        return np.array(self.board.export_board(), dtype=np.int8)
    
    def export_board_string(self):
        return self.board.export_board_string()

    def get_state(self):
        return {
            "board": self.board.export_board(),
            "turn": getattr(self.board, "waiting_turn", None),
            "move_count": getattr(self.board, "move_count", None)
        }

    def set_state(self, state):
        self.board.import_board(state["board"])
        if state["turn"] is not None and hasattr(self.board, "waiting_turn"):
            self.board.waiting_turn = state["turn"]
        if state["move_count"] is not None and hasattr(self.board, "move_count"):
            self.board.move_count = state["move_count"]
    def calculate_heuristic(self, state=None) -> int:
        # pieces_count = self.board.count_pieces()
        # if pieces_count <= 1: return 0
        
        # # Reuse your valid moves logic to build the connectivity graph
        # # This is the "Island Detection" logic we discussed
        # valid_moves = self.board.get_all_valid_moves()
        # pieces_positions = []
        
        # # Get all piece locations
        # grid = self.board.get_board()
        # for r in range(8):
        #     for c in range(8):
        #         if grid[r][c] is not None:
        #             pieces_positions.append((r,c))

        # # Build Graph
        # adj = {pos: set() for pos in pieces_positions}
        # for r1, c1, r2, c2 in valid_moves:
        #     if (r1, c1) in adj and (r2, c2) in adj:
        #         adj[(r1, c1)].add((r2, c2))
        #         adj[(r2, c2)].add((r1, c1)) # Undirected

        # # Count Islands
        # visited = set()
        # islands = 0
        # for p in pieces_positions:
        #     if p not in visited:
        #         islands += 1
        #         stack = [p]
        #         visited.add(p)
        #         while stack:
        #             curr = stack.pop()
        #             for neighbor in adj[curr]:
        #                 if neighbor not in visited:
        #                     visited.add(neighbor)
        #                     stack.append(neighbor)

        # # SCORING: 
        # # Base cost = Number of pieces left
        # # Penalty = If >1 island, massive penalty (unsolvable)
        # if islands > 1:
        #     return 1000 + pieces_count 
        
        # return pieces_count

        pieces_count = self.board.count_pieces()
        if pieces_count <= 1: 
            return 0
            
        return pieces_count - 1