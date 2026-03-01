import pygame
import json
import os
import copy

from src.scenes.scene import Scene
from src.ui.element import *
from settings import *
from src.utils.asset_loading import load_images, colorize_image
from src.entities.figure import int_to_piece
from src.entities.chess import ChessPuzzle
from src.algorithms.Astar import AStarSolver

class MapCreatorScene(Scene):
    def __init__(self, manager, grid_rows=8, grid_cols=8):
        super().__init__(manager)
        
        self.setup_layout()
        self.images = load_images(self.SQUARE_SIZE)
        self.palette_images = load_images(self.SQUARE_SIZE // 1.5)
        trash_font_size = int(self.SCREEN_HEIGHT * 0.05)
        coord_font_size = int(self.SQUARE_SIZE * 0.25)
        self.trash_icon = pygame.font.SysFont("segoe ui emoji", trash_font_size).render("🗑️", True, (200, 50, 50))
        self.coord_font = pygame.font.SysFont("arial", coord_font_size, bold=True)

        self.mode = "ranger" 
        self.board_data = [[0 for _ in range(8)] for _ in range(8)]
        self.drag_piece_code = None  
        self.selected_tool_code = 1 
        self.trash_rect = None 
        self.is_play_mode = False
        self.temp_game_env = None
        self.backup_board_data = None

        self.dragging = False
        self.drag_origin = None
        self.valid_moves = []

        self.setup_ui()
        toast_h = int(self.SCREEN_HEIGHT * 0.06)
        toast_w = int(self.SCREEN_WIDTH * 0.2)
        toast_y = self.clear_btn.rect.bottom + int(self.SCREEN_HEIGHT * 0.05)
        self.feedback = FeedbackToast(self.LEFT_PANEL_X, toast_y, toast_h, toast_w)

    def setup_layout(self):
        screen = pygame.display.get_surface()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        self.MARGIN = int(min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) * 0.05)
        
        self.BOARD_SIZE = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT) - (self.MARGIN * 2)
        self.SQUARE_SIZE = self.BOARD_SIZE // 8
        self.BOARD_X = (self.SCREEN_WIDTH - self.BOARD_SIZE) // 2
        self.BOARD_Y = (self.SCREEN_HEIGHT - self.BOARD_SIZE) // 2
        
        self.LEFT_PANEL_WIDTH = self.BOARD_X - (self.MARGIN * 2)
        self.LEFT_PANEL_X = self.MARGIN
        self.PALETTE_X = self.BOARD_X + self.BOARD_SIZE + self.MARGIN
        self.PALETTE_Y = self.BOARD_Y

    def setup_ui(self):
        btn_width = int(self.LEFT_PANEL_WIDTH * 0.9)
        btn_height = int(self.SCREEN_HEIGHT * 0.07)
        font_size = int(self.SCREEN_HEIGHT * 0.035)

        btn_x = self.LEFT_PANEL_X + (self.LEFT_PANEL_WIDTH - btn_width) // 2
        
        start_y = int(self.SCREEN_HEIGHT * 0.15)
        spacing = int(self.SCREEN_HEIGHT * 0.02)
        
        icon_size = int(self.SCREEN_HEIGHT * 0.05)
        self.back_btn = ClickableImage(APP_IMG_URL + "return.png", self.MARGIN, self.MARGIN, (icon_size, icon_size), action=lambda: self.manager.switch_scene('menu'), func = lambda image: colorize_image(image, COLOR_DARK))
        
        self.mode_btn = ThemedButton(f"Mode: {self.mode.title()}", btn_x, start_y, btn_width, btn_height, font_size=font_size, action=self.toggle_mode)
        self.test_btn = ThemedButton("Testing", btn_x, start_y + btn_height + spacing, btn_width, btn_height, font_size=font_size, action=self.toggle_play_mode)
        self.save_btn = ThemedButton("Save Map", btn_x, start_y + (btn_height + spacing) * 2, btn_width, btn_height, font_size=font_size, action=self.save_map)
        self.clear_btn = ThemedButton("Clear Board", btn_x, start_y + (btn_height + spacing) * 3, btn_width, btn_height, font_size=font_size, action=self.clear_board)

        self.white_pieces = [1, 2, 3, 4, 5, 6] 
        self.black_pieces = [-1, -2, -3, -4, -5, -6]

    def toggle_mode(self):
        if self.is_play_mode: return
        if self.mode == "ranger":
            self.mode = "melee"
        elif self.mode == "melee":
            self.mode = "solo"
            for r in range(8):
                for c in range(8):
                    if self.board_data[r][c] < 0:
                        self.board_data[r][c] = abs(self.board_data[r][c])
        else:
            self.mode = "ranger"
            for r in range(8):
                for c in range(8):
                    if self.board_data[r][c] < 0:
                        self.board_data[r][c] = - self.board_data[r][c]
                        
        self.mode_btn.text = f"Mode: {self.mode.title()}"
        self.feedback.show(f"Switched to {self.mode.title()}")

    def toggle_play_mode(self):
        if self.is_play_mode:
            self.board_data = copy.deepcopy(self.backup_board_data)
            self.temp_game_env = None
            self.is_play_mode = False
            self.test_btn.text = "Testing"
            self.feedback.show("Edit Mode")
        else:
            count = sum(1 for r in self.board_data for c in r if c != 0)
            if count < 2:
                self.feedback.show("Need 2+ pieces!", True)
                return
            if self.mode == "solo":
                has_king = 0
                for r in range(8):
                    for c in range(8):
                        if abs(self.board_data[r][c]) == 6:  # King
                            has_king += 1 

                if  has_king == 0:
                    self.feedback.show("Solo mode needs a King!", True)
                    return
                elif has_king >1:
                    self.feedback.show("Solo mode can only have one King!", True)
                    return
            self.backup_board_data = copy.deepcopy(self.board_data)
            puzzle_data = { "board": self.board_data, "turn": True }
            self.temp_game_env = ChessPuzzle(self.mode, puzzle_data)
            
            self.is_play_mode = True
            self.test_btn.text = "Stop Testing"
            self.feedback.show("Play Mode Active")

    def update(self, event_list):
        self.setup_layout()
        mouse_pos = pygame.mouse.get_pos()
        self.feedback.update()

        for event in event_list:
            if self.back_btn.check_click(event): return
            if self.mode_btn.check_click(event): return
            if self.test_btn.check_click(event): return
            if self.save_btn.check_click(event): return
            if self.clear_btn.check_click(event): return

            if self.is_play_mode:
                self.handle_play_input(event, mouse_pos)
            else:
                self.handle_edit_input(event, mouse_pos)

    def handle_edit_input(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                r, c = self.get_square_under_mouse(mouse_pos)
                if r is not None:
                    clicked_piece = self.board_data[r][c]
                    if self.selected_tool_code == 0:
                        if clicked_piece != 0:
                            self.board_data[r][c] = 0
                    elif clicked_piece == 0 and self.selected_tool_code != 0:
                        self.board_data[r][c] = self.selected_tool_code
                    elif clicked_piece != 0:
                        self.drag_piece_code = clicked_piece
                        self.board_data[r][c] = 0
                        self.selected_tool_code = clicked_piece

                sel = self.get_palette_piece_under_mouse(mouse_pos)
                if sel is not None:
                    self.selected_tool_code = sel
                    if sel != 0:
                        self.drag_piece_code = sel

            elif event.button == 3:
                r, c = self.get_square_under_mouse(mouse_pos)
                if r is not None:
                    self.board_data[r][c] = 0

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.drag_piece_code is not None:
                    r, c = self.get_square_under_mouse(mouse_pos)
                    if r is not None:
                        self.board_data[r][c] = self.drag_piece_code
                    self.drag_piece_code = None

    def handle_play_input(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                r, c = self.get_square_under_mouse(mouse_pos)
                if r is not None:
                    board_state = self.temp_game_env.board.export_board()
                    piece = board_state[r][c]

                    if piece != 0:
                        self.dragging = True
                        self.drag_piece_code = piece
                        self.drag_origin = (r, c)

                        raw_moves = self.temp_game_env.board.get_all_valid_moves(specific_pos=(r,c))
                        self.valid_moves = [(m[2], m[3]) for m in raw_moves]

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                r, c = self.get_square_under_mouse(mouse_pos)
                
                if r is not None and self.drag_origin:
                    start_r, start_c = self.drag_origin
                    obs, reward, done, info = self.temp_game_env.step((start_r, start_c, r, c))
                    
                    if reward == -10:
                        pass
                    else:
                        if done:
                            if reward > 0: self.feedback.show("You Won!", False)
                            else: self.feedback.show("Dead End!", True)
                self.dragging = False
                self.drag_piece_code = None
                self.drag_origin = None
                self.valid_moves = []

    def draw(self):
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)
        
        self.draw_board(screen)
        if not self.is_play_mode:
            self.draw_palette(screen)
        
        self.back_btn.draw(screen)
        self.mode_btn.draw(screen)
        self.test_btn.draw(screen)
        self.save_btn.draw(screen)
        self.clear_btn.draw(screen)
        
        self.feedback.draw(screen)

        if self.drag_piece_code is not None:
            piece_cls = int_to_piece[abs(self.drag_piece_code)]
            p_obj = piece_cls(self.drag_piece_code > 0)
            img_key = p_obj.get_short_name()
            if img_key in self.images:
                img = self.images[img_key]
                rect = img.get_rect(center=pygame.mouse.get_pos())
                screen.blit(img, rect)

    def draw_board(self, screen):
        if self.is_play_mode and self.temp_game_env:
            display_grid = self.temp_game_env.board.export_board()
        else:
            display_grid = self.board_data

        for r in range(8):
            for c in range(8):
                x = self.BOARD_X + c * self.SQUARE_SIZE
                y = self.BOARD_Y + r * self.SQUARE_SIZE

                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(screen, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))
                text_color = COLOR_DARK if (r + c) % 2 == 0 else COLOR_LIGHT
                
                offset = int(self.SQUARE_SIZE * 0.1)
                
                if c == 0:
                    rank_text = str(8 - r)
                    text_surf = self.coord_font.render(rank_text, True, text_color)
                    screen.blit(text_surf, (x + offset, y + offset))
                if r == 7:
                    file_text = chr(97 + c)
                    text_surf = self.coord_font.render(file_text, True, text_color)
                    text_width = text_surf.get_width()
                    text_height = text_surf.get_height()
                    screen.blit(text_surf, (x + self.SQUARE_SIZE - text_width - offset, y + self.SQUARE_SIZE - text_height - offset))

                if self.is_play_mode and self.dragging and (r, c) in self.valid_moves:
                    s = pygame.Surface((self.SQUARE_SIZE, self.SQUARE_SIZE), pygame.SRCALPHA)
                    pygame.draw.circle(s, (0, 255, 0, 100), (self.SQUARE_SIZE//2, self.SQUARE_SIZE//2), self.SQUARE_SIZE//6)
                    screen.blit(s, (x, y))

                if self.is_play_mode and self.dragging and (r, c) == self.drag_origin:
                    continue

                code = display_grid[r][c]
                if code != 0:
                    piece_cls = int_to_piece[abs(code)]
                    p_obj = piece_cls(code > 0)
                    img_key = p_obj.get_short_name()
                    if img_key in self.images:
                        screen.blit(self.images[img_key], (x, y))

    def draw_palette(self, screen):
        col_width = self.SQUARE_SIZE
        row_height = self.SQUARE_SIZE
        start_x = self.PALETTE_X
        start_y = self.PALETTE_Y
        gap = int(self.SQUARE_SIZE * 0.1)
        
        for row in range(6):
            for col in range(3):
                if self.mode == "ranger" and col == 2: continue
                if self.mode == "solo" and col == 2: continue

                code = None
                if col == 0:
                    if row == 0: code = 0 
                    else: continue 
                elif col == 1: code = self.white_pieces[row]
                elif col == 2: code = self.black_pieces[row]

                if code is None: continue

                x = start_x + col * (col_width + gap)
                y = start_y + row * (row_height + gap)
                
                if code == self.selected_tool_code:
                    color = (255, 50, 50) if code == 0 else (0, 255, 0)
                    pygame.draw.rect(screen, color, (x - 2, y - 2, col_width + 4, row_height + 4), 3)
                
                pygame.draw.rect(screen, (220, 220, 220), (x, y, col_width, row_height))
                
                if code == 0:
                    rect = self.trash_icon.get_rect(center=(x + col_width//2, y + row_height//2))
                    screen.blit(self.trash_icon, rect)
                else:
                    piece_cls = int_to_piece[abs(code)]
                    p_obj = piece_cls(code > 0)
                    img_key = p_obj.get_short_name()
                    if img_key in self.palette_images:
                        img = self.palette_images[img_key]
                        rect = img.get_rect(center=(x + col_width//2, y + row_height//2))
                        screen.blit(img, rect)

    def get_palette_piece_under_mouse(self, pos):
        mx, my = pos
        col_width = self.SQUARE_SIZE
        row_height = self.SQUARE_SIZE
        start_x = self.PALETTE_X
        start_y = self.PALETTE_Y
        gap = int(self.SQUARE_SIZE * 0.1)
        
        for row in range(6):
            for col in range(3):
                if self.mode == "ranger" and col == 2: continue
                
                code = None
                if col == 0:
                    if row == 0: code = 0
                    else: continue
                elif col == 1: code = self.white_pieces[row]
                elif col == 2: code = self.black_pieces[row]

                if code is None: continue

                x = start_x + col * (col_width + gap)
                y = start_y + row * (row_height + gap)
                
                rect = pygame.Rect(x, y, col_width, row_height)
                if rect.collidepoint(mx, my):
                    return code
        return None

    def get_square_under_mouse(self, pos):
        x, y = pos
        if self.BOARD_X <= x <= self.BOARD_X + self.BOARD_SIZE and self.BOARD_Y <= y <= self.BOARD_Y + self.BOARD_SIZE:
            return (y - self.BOARD_Y) // self.SQUARE_SIZE, (x - self.BOARD_X) // self.SQUARE_SIZE
        return None, None

    def clear_board(self):
        if self.is_play_mode: return
        self.board_data = [[0]*8 for _ in range(8)]
        self.feedback.show("Board Cleared")

    def save_map(self):
        if self.is_play_mode:
            self.feedback.show("Stop testing first!", True)
            return
        
        count = sum(1 for r in self.board_data for c in r if c != 0)
        if count < 2:
            self.feedback.show("Map too empty!", True)
            return
        if self.mode == "solo":
            has_king = False
            king_count = 0
            for r in range(8):
                for c in range(8):
                    if abs(self.board_data[r][c]) == 6:
                        has_king = True
                        king_count += 1
                    elif self.board_data[r][c] < 0:
                        self.feedback.show("Solo mode cannot have black pieces!", True)
                        return
            
            if not has_king:
                self.feedback.show("Solo mode needs a King!", True)
                return
            if king_count > 1:
                self.feedback.show("Solo mode can only have one King!", True)
                return
        self.feedback.show("Checking Solvability...", False)
        self.draw() 
        pygame.display.flip()
        
        puzzle_data = { "board": self.board_data, "turn": True }
        
        try:
            env = ChessPuzzle(self.mode, puzzle_data)
            solver = AStarSolver(env)
            steps = 0
            solved = False
            while steps < 5000:
                state, move = solver.take_action()
                if solver.solution_found:
                    solved = True
                    break
                if state is None and move is None:
                    break 
                steps += 1
            
            if not solved:
                self.feedback.show("Map is Unsolvable!", True)
                return
                
        except Exception as e:
            print(f"Solver Error: {e}")
            self.feedback.show("Error checking map!", True)
            return

        folder = "chess_ranger" if self.mode == "ranger" else "chess_melee" if self.mode == "melee" else "chess_solo"
        filepath = DATA_URL + f'{folder}/puzzle_map.json'
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        data = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                try: data = json.load(f)
                except: data = {}
        
        key = str(count)
        if key not in data:
            data[key] = []
                
        if self.board_data not in data[key]:
            data[key].append(self.board_data)
            with open(filepath, 'w') as f:
                json.dump(data, f)
            self.feedback.show(f"Saved! ({count} pieces)")
        else:
            self.feedback.show("Map already exists!", True)