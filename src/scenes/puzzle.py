import pygame
import json
import random
import time
import copy
import os

from src.scenes.scene import Scene
import settings
from settings import *
from src.utils.asset_loading import load_images, get_puzzle_limits, colorize_image
from src.ui.element import *
from src.ui.algorithm_handler import AlgorithmHandler
from src.entities.chess import ChessPuzzle


class PuzzleLogic:
    def __init__(self, mode, square_size, board_layout: list[list[int]] | None = None):
        self.mode = mode
        self.puzzle = ChessPuzzle(mode, board_layout)

        self.MIN_NUM_PIECES, self.MAX_NUM_PIECES = get_puzzle_limits(mode)

        self.initial_board_layout = self.puzzle.get_state()
        self.images = load_images(square_size)
        self.current_num_of_pieces = self.puzzle.board.count_pieces()
    
    def step(self, action: tuple[int, int, int, int]):
        return self.puzzle.step(action)
    
    def change_num_of_pieces(self, num: int) -> bool:
        if num < self.MIN_NUM_PIECES or num > self.MAX_NUM_PIECES:
            return False
        self.current_num_of_pieces = num
        
        try:
            with open(DATA_URL + f'chess_{self.mode}/puzzle_map.json') as json_data:
                map_list = json.load(json_data).get(str(num), [])
            
            if not map_list:
                blank_board = [[0 for _ in range(8)] for _ in range(8)]
                self.puzzle.reset(blank_board)
                self.initial_board_layout = blank_board
                return True

            new_map = self.puzzle.board.export_board()
            if len(map_list) > 1:
                while new_map == self.puzzle.board.export_board():
                    new_map = random.choice(map_list)
            else:
                new_map = map_list[0]

            self.puzzle.reset(new_map)
            self.initial_board_layout = new_map
            return True
            
        except Exception as e:
            print(f"Error changing num pieces: {e}")
            return False

    def change_map(self):
        try:
            with open(DATA_URL + f'chess_{self.mode}/puzzle_map.json') as json_data:
                map_list = json.load(json_data).get(str(self.current_num_of_pieces), [])
            if not map_list: return
            new_map = self.puzzle.board.export_board()
            if len(map_list) == 1 and map_list[0] == new_map:
                return
            while new_map == self.puzzle.board.export_board():
                new_map = random.choice(map_list)
            self.puzzle.reset(new_map)
            self.initial_board_layout = copy.deepcopy(new_map)
        except Exception as e:
            print(f"Error changing map: {e}")

    def reset(self):
        self.puzzle.reset(self.initial_board_layout)

    def solver_iterator(self, scene, algorithm_class):
        temp_env = ChessPuzzle(self.mode, self.puzzle.get_state())
        solver = algorithm_class(temp_env)
        iterations = 0
        
        while True:
            state, move = solver.take_action()
            if state is None and move is None:
                break
            
            if settings.SEARCH_ANIMATION:
                self.puzzle.set_state(state)
                scene.trigger_move((move[0], move[1]), (move[2], move[3]), settings.SEARCH_ANIMATION_DURATION)
            
            iterations += 1
            if iterations > 10000:
                yield ("error", "Timeout") 
                break
            yield ("running", iterations) 

        self.reset()
        if solver.solution_found:
            yield ("finished", solver)
        else:
            yield ("failed", [])

    def get_image(self, piece: str):
        return self.images[piece]
    
    def get_board(self):
        return self.puzzle.export_board_string()

    def get_num_of_pieces(self) -> int:
        return self.current_num_of_pieces
        
class PuzzleScene(Scene):
    def __init__(self, manager, mode, initial_map=None):
        super().__init__(manager)
        self.update_screen() 
        
        self.mode = mode
        self.MIN_NUM_PIECES, self.MAX_NUM_PIECES = get_puzzle_limits(mode)
        
        self.drag_piece = None
        self.drag_origin = None
        self.dragging = False
        self.valid_moves = []
        self.mouse_pos = (0, 0)
        self.logic = PuzzleLogic(mode, self.SQUARE_SIZE, initial_map)

        self.animating = False
        self.anim_piece = None      
        self.anim_start_pos = None  
        self.anim_end_pos = None
        self.final_move_data = (0,0,0,0)  
        self.anim_start_time = 0
        self.current_anim_pos = pygame.math.Vector2(0, 0)
        
        self.is_playing_solution = False
        self.playback_queue = []
        self.game_won = False
        
        win_font_size = int(self.SCREEN_WIDTH * 0.1)
        self.win_font = pygame.font.Font(None, win_font_size)
        
        coord_font_size = int(self.SQUARE_SIZE * 0.25)
        self.coord_font = pygame.font.SysFont("arial", coord_font_size, bold=True)
        
        with open(DATA_URL + 'puzzle_info.json') as json_data:
            rules = json.load(json_data)[f"chess_{self.mode}"]["rules"]

        rule_x = self.SCREEN_WIDTH - self.RIGHT_PANEL_WIDTH - self.MARGIN
        rule_y = int(self.MARGIN * 0.7)
        rule_w = self.RIGHT_PANEL_WIDTH
        rule_h = int(self.SCREEN_HEIGHT * 0.15)  
        rule_font_size = int(self.SCREEN_HEIGHT * 0.025) 
        self.rule_box = RuleBox(rule_x, rule_y, rule_w, rule_h, rules, font_size=rule_font_size)
        self.algorithm_handler = AlgorithmHandler(self, start_y=rule_y + rule_h + 10)

        icon_size = int(self.SCREEN_HEIGHT * 0.05)
        self.return_image = ClickableImage(APP_IMG_URL + "return.png", self.MARGIN, self.MARGIN, (icon_size, icon_size), action = lambda: self.manager.switch_scene('menu'), func = lambda image: colorize_image(image, COLOR_DARK))

        left_center_x = self.MARGIN + (self.LEFT_PANEL_WIDTH // 2)
        start_y = int(self.SCREEN_HEIGHT * 0.15)
        
        label_font_size = int(self.SCREEN_HEIGHT * 0.035)
        self.pieces_label_font = pygame.font.SysFont("tahoma", label_font_size, bold=True)
        self.pieces_label_surf = self.pieces_label_font.render("Number of pieces", True, COLOR_LIGHT)
        
        selector_h = int(self.SCREEN_HEIGHT * 0.06)
        selector_real_width = selector_h * 4.5 
        selector_x = int(left_center_x - (selector_real_width / 2))
        
        label_y = start_y
        selector_y = label_y + label_font_size + int(self.SCREEN_HEIGHT * 0.05) # Increased gap

        self.num_of_pieces_selector = NumberSelector(
            selector_x, selector_y, 
            selector_h,
            self.MIN_NUM_PIECES, self.MAX_NUM_PIECES, self.logic.get_num_of_pieces(), 
            APP_IMG_URL + "left-arrow.png", APP_IMG_URL + "right-arrow.png", 
            self.handle_num_of_pieces, self.handle_num_of_pieces,
            image_func=lambda image: colorize_image(image, COLOR_DARK)
        )
        
        btn_w = int(self.LEFT_PANEL_WIDTH * 0.9)
        btn_h = int(self.SCREEN_HEIGHT * 0.07)
        btn_x = self.MARGIN + (self.LEFT_PANEL_WIDTH - btn_w) // 2
        spacing = int(self.SCREEN_HEIGHT * 0.02)
        
        btn_group_y = selector_y + selector_h + int(self.SCREEN_HEIGHT * 0.05)
        self.change_map_button = ThemedButton("Change Map", btn_x, btn_group_y, btn_w, btn_h, action=self.handle_change_map)
        self.reset_button = ThemedButton("Start over", btn_x, btn_group_y + btn_h + spacing, btn_w, btn_h, action=self.handle_reset)

        algo_start_y = btn_group_y + (btn_h + spacing) * 2 + int(self.SCREEN_HEIGHT * 0.05)
        algo_row_h = int(self.SCREEN_HEIGHT * 0.08)

        label_w = int(btn_w * 0.7)
        label_h = int(algo_row_h * 0.8)
        icon_dim = int(algo_row_h * 0.6)
        icon_box_w = int(btn_w * 0.2)

        algo_label_font_size = int(self.SCREEN_HEIGHT * 0.025)
        btn_y_offset = (label_h - icon_dim) // 2
        search_x = btn_x + label_w + int(btn_w * 0.02)
        play_x = search_x + icon_box_w
        
        # A*
        self.astar_y = algo_start_y
        self.astar_label = LabelBox("A* Algorithm", btn_x, self.astar_y, label_w, label_h, font_size=algo_label_font_size)
        self.astar_search_btn = ClickableImage(APP_IMG_URL + "search.png", search_x, self.astar_y + btn_y_offset, (icon_dim, icon_dim), action=lambda: self.handle_search("A*"), func = lambda image: colorize_image(image, COLOR_DARK))
        self.astar_play_btn = ClickableImage(APP_IMG_URL + "play.png", play_x, self.astar_y + btn_y_offset, (icon_dim, icon_dim), action=lambda: self.start_solution_playback("A*"), func = lambda image: colorize_image(image, COLOR_DARK))

        # BFS
        self.bfs_y = algo_start_y + algo_row_h
        self.bfs_label = LabelBox("BFS Algorithm", btn_x, self.bfs_y, label_w, label_h, font_size=algo_label_font_size)
        self.bfs_search_btn = ClickableImage(APP_IMG_URL + "search.png", search_x, self.bfs_y + btn_y_offset, (icon_dim, icon_dim), action=lambda: self.handle_search("BFS"), func = lambda image: colorize_image(image, COLOR_DARK))
        self.bfs_play_btn = ClickableImage(APP_IMG_URL + "play.png", play_x, self.bfs_y + btn_y_offset, (icon_dim, icon_dim), action=lambda: self.start_solution_playback("BFS"), func = lambda image: colorize_image(image, COLOR_DARK))

        # DFS
        self.dfs_y = algo_start_y + algo_row_h * 2
        self.dfs_label = LabelBox("DFS Algorithm", btn_x, self.dfs_y, label_w, label_h, font_size=algo_label_font_size)
        self.dfs_search_btn = ClickableImage(APP_IMG_URL + "search.png", search_x, self.dfs_y + btn_y_offset, (icon_dim, icon_dim), action=lambda: self.handle_search("DFS"), func = lambda image: colorize_image(image, COLOR_DARK))
        self.dfs_play_btn = ClickableImage(APP_IMG_URL + "play.png", play_x, self.dfs_y + btn_y_offset, (icon_dim, icon_dim), action=lambda: self.start_solution_playback("DFS"), func = lambda image: colorize_image(image, COLOR_DARK))

        text_w = self.pieces_label_surf.get_width()
        self.pieces_label_pos = (left_center_x - text_w // 2, label_y)

    def update_screen(self):
        screen = pygame.display.get_surface()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        self.MARGIN = int(min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) * 0.03)
        
        self.BOARD_SIZE = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) - (self.MARGIN * 2)
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        self.BOARD_X = (self.SCREEN_WIDTH - self.BOARD_SIZE) // 2
        self.BOARD_Y = (self.SCREEN_HEIGHT - self.BOARD_SIZE) // 2
        
        self.LEFT_PANEL_WIDTH = self.BOARD_X - (self.MARGIN * 2)
        self.RIGHT_PANEL_WIDTH = self.LEFT_PANEL_WIDTH 

    def update(self, event_list):
        self.update_screen()
        self.mouse_pos = pygame.mouse.get_pos()

        if self.animating:
            current_time = pygame.time.get_ticks()
            time_passed = current_time - self.anim_start_time
            progress = time_passed / self.duration

            if progress >= 1.0:
                self.animating = False
                r1, c1, r2, c2 = self.final_move_data 
                self.logic.step((r1, c1, r2, c2))
            else:
                self.current_anim_pos = self.anim_start_pos.lerp(self.anim_end_pos, progress)

        self.algorithm_handler.update()
                    
        if self.is_playing_solution and not self.animating:
            if self.playback_queue:
                next_move = self.playback_queue.pop(0)
                self.trigger_move((next_move[0], next_move[1]), (next_move[2], next_move[3]), settings.PLAY_ANIMATION_DURATION)
            else:
                self.is_playing_solution = False

        for event in event_list:
            if self.animating: continue 

            if self.return_image.check_click(event): pass
            elif self.change_map_button.check_click(event): pass 
            elif self.reset_button.check_click(event): pass
            elif self.num_of_pieces_selector.handle_event(event): pass

            elif self.astar_search_btn.check_click(event): pass
            elif self.bfs_search_btn.check_click(event): pass
            elif self.dfs_search_btn.check_click(event): pass
    
            elif self.algorithm_handler.has_solution("A*") and self.astar_play_btn.check_click(event): pass
            elif self.algorithm_handler.has_solution("BFS") and self.bfs_play_btn.check_click(event): pass
            elif self.algorithm_handler.has_solution("DFS") and self.dfs_play_btn.check_click(event): pass

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    row, col = self.get_square_under_mouse(self.mouse_pos)
                    self.valid_moves = [] 
                    if row is not None and self.logic.get_board()[row][col] != '--':
                        self.dragging = True
                        self.drag_piece = self.logic.get_board()[row][col]
                        self.drag_origin = (row, col)
                        full_moves = self.logic.puzzle.board.get_all_valid_moves(specific_pos=(row, col))
                        self.valid_moves = [(m[2], m[3]) for m in full_moves]

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging:
                    row, col = self.get_square_under_mouse(self.mouse_pos)
                    move_made = False
                    if row is not None:
                        obs, reward, done, info = self.logic.step((self.drag_origin[0], self.drag_origin[1], row, col))
                        if reward != -10: 
                            move_made = True
                            if done: self.game_won = True
                    self.dragging = False
                    self.drag_piece = None
                    if move_made:
                        self.valid_moves = []   

    def draw(self):
        self.draw_board()
        screen = pygame.display.get_surface()
        
        self.rule_box.draw(screen)
        self.return_image.draw(screen)
        screen.blit(self.pieces_label_surf, self.pieces_label_pos)
        self.num_of_pieces_selector.draw(screen)
        self.change_map_button.draw(screen)
        self.reset_button.draw(screen)
        
        self.algorithm_handler.draw(screen) 

        self.astar_label.draw(screen)
        self.bfs_label.draw(screen)
        self.dfs_label.draw(screen)
        
        self.astar_search_btn.draw(screen)
        self.bfs_search_btn.draw(screen)
        self.dfs_search_btn.draw(screen)

        if self.algorithm_handler.has_solution("A*"):
            self.astar_play_btn.draw(screen)
        if self.algorithm_handler.has_solution("BFS"):
            self.bfs_play_btn.draw(screen)
        if self.algorithm_handler.has_solution("DFS"):
            self.dfs_play_btn.draw(screen)

        if self.animating and self.anim_piece:
            img = self.logic.get_image(self.anim_piece)
            screen.blit(img, (self.current_anim_pos.x, self.current_anim_pos.y))

        if self.dragging and self.drag_piece:
            img = self.logic.get_image(self.drag_piece)
            rect = img.get_rect(center=self.mouse_pos)
            screen.blit(img, rect)

        if self.game_won:
            s = pygame.Surface((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 150)) 
            screen.blit(s, (0,0))
            text_surf = self.win_font.render("YOU WIN!", True, COLOR_DARK)
            text_rect = text_surf.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, (255, 255, 255), text_rect.inflate(20, 20), 4)
            screen.blit(text_surf, text_rect)
    
    def reset_game(self):
        self.animating = False
        self.logic.reset()

    def trigger_move(self, start_grid_pos, end_grid_pos, duration=100):
        r1, c1 = start_grid_pos
        r2, c2 = end_grid_pos
        piece = self.logic.get_board()[r1][c1]
        if piece == '--': return

        self.animating = True
        self.duration = duration
        self.anim_piece = piece
        self.anim_start_time = pygame.time.get_ticks()

        start_x = self.BOARD_X + (c1 * self.SQUARE_SIZE)
        start_y = self.BOARD_Y + (r1 * self.SQUARE_SIZE)
        self.anim_start_pos = pygame.math.Vector2(start_x, start_y)
        self.anim_end_pos = pygame.math.Vector2(self.BOARD_X + c2*self.SQUARE_SIZE, self.BOARD_Y + r2*self.SQUARE_SIZE)
        self.final_move_data = (r1, c1, r2, c2)

    def handle_change_map(self):
        self.logic.change_map()
        self.algorithm_handler.reset()
        self.playback_queue = []
        self.is_playing_solution = False
        self.game_won = False

    def handle_search(self, algorithm_name):
        self.handle_reset()
        self.algorithm_handler.start_search(algorithm_name)

    def handle_reset(self):
        self.logic.reset()
        self.animating = False
        self.is_playing_solution = False
        self.playback_queue = []
        self.game_won = False

    def handle_num_of_pieces(self, num_of_pieces):
        self.logic.change_num_of_pieces(num_of_pieces)
        self.algorithm_handler.reset()
        self.game_won = False

    def start_solution_playback(self, algorithm_name):
        if not self.algorithm_handler.has_solution(algorithm_name):
            return 
        print(f"Replaying {algorithm_name} solution...")
        self.logic.reset()
        self.playback_queue = list(self.algorithm_handler.get_solution_path(algorithm_name))
        self.is_playing_solution = True
        self.game_won = False

    def get_square_under_mouse(self, pos):
        x, y = pos
        if self.BOARD_X <= x <= self.BOARD_X + self.BOARD_SIZE and self.BOARD_Y <= y <= self.BOARD_Y + self.BOARD_SIZE:
            col = (x - self.BOARD_X) // self.SQUARE_SIZE
            row = (y - self.BOARD_Y) // self.SQUARE_SIZE
            return row, col
        return None, None
    
    def draw_board(self):
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                x_pos = self.BOARD_X + (c * self.SQUARE_SIZE)
                y_pos = self.BOARD_Y + (r * self.SQUARE_SIZE)
                is_light_square = (r + c) % 2 == 0
                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(screen, color, (x_pos, y_pos, self.SQUARE_SIZE, self.SQUARE_SIZE))
                text_color = COLOR_DARK if is_light_square else COLOR_LIGHT
                
                offset = int(self.SQUARE_SIZE * 0.1)
                
                if c == 0:
                    rank_text = str(8 - r)
                    text_surf = self.coord_font.render(rank_text, True, text_color)
                    screen.blit(text_surf, (x_pos + offset, y_pos + offset // 2))
                if r == 7:
                    file_text = chr(97 + c)
                    text_surf = self.coord_font.render(file_text, True, text_color)
                    text_width = text_surf.get_width()
                    text_height = text_surf.get_height()
                    screen.blit(text_surf, (x_pos + self.SQUARE_SIZE - text_width - offset, y_pos + self.SQUARE_SIZE - text_height - offset // 2))

        if self.dragging:
            hover_row, hover_col = self.get_square_under_mouse(self.mouse_pos)
            if hover_row is not None:
                s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE))
                s.set_alpha(150) 
                s.fill(COLOR_HIGHLIGHT) 
                screen.blit(s, (self.BOARD_X + hover_col * self.SQUARE_SIZE, self.BOARD_Y + hover_row * self.SQUARE_SIZE))

        board = self.logic.get_board()
        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                piece = board[r][c]
                if piece != '--':
                    if self.dragging and (r, c) == self.drag_origin: continue
                    if self.animating and (r, c) == (self.final_move_data[0], self.final_move_data[1]): continue
                    x_pos = self.BOARD_X + (c * self.SQUARE_SIZE)
                    y_pos = self.BOARD_Y + (r * self.SQUARE_SIZE)
                    screen.blit(self.logic.get_image(piece), (x_pos, y_pos))
        if self.valid_moves: 
            for (r, c) in self.valid_moves:
                x_pos = self.BOARD_X + (c * self.SQUARE_SIZE)
                y_pos = self.BOARD_Y + (r * self.SQUARE_SIZE)
                radius = self.SQUARE_SIZE // 8 
                s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(s, COLOR_ORANGE_HIGHLIGHT, (self.SQUARE_SIZE//2, self.SQUARE_SIZE//2), radius)
                screen.blit(s, (x_pos, y_pos))