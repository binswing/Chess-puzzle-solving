import pygame
import sys
import json
import random
import os

from src.scenes.scene import Scene
from src.ui.element import *
from settings import *
from src.utils.asset_loading import load_images
from src.entities.figure import int_to_piece

class MenuScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        screen = pygame.display.get_surface()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        
        logo_path = APP_IMG_URL + "logo.png"
        max_w = self.SCREEN_WIDTH * 0.60
        max_h = self.SCREEN_HEIGHT * 0.35

        try:
            temp_surf = pygame.image.load(logo_path)
            orig_w, orig_h = temp_surf.get_size() 
            scale = min(max_w / orig_w, max_h / orig_h)
            
            final_w = int(orig_w * scale)
            final_h = int(orig_h * scale)
        except Exception as e:
            print(f"Warning: Could not calculate logo aspect ratio: {e}")
            final_w, final_h = int(max_w), int(max_h)

        logo_x = int(self.SCREEN_WIDTH * 0.05)
        logo_y = int(self.SCREEN_HEIGHT * 0.05)

        self.logo_image = Image(logo_path, logo_x, logo_y, (final_w, final_h))

        btn_w = int(self.SCREEN_WIDTH * 0.25)
        btn_h = int(self.SCREEN_HEIGHT * 0.06)
        font_size = int(self.SCREEN_HEIGHT * 0.035)
        spacing = int(self.SCREEN_HEIGHT * 0.075)
        btn_x = int(self.SCREEN_WIDTH * 0.1) 
        start_y = int(self.SCREEN_HEIGHT * 0.45) 

        self.chess_ranger_scene_button = ThemedButton("Chess Ranger Mode", btn_x, start_y + spacing * 0, btn_w, btn_h, font_size=font_size, action=lambda: self.start_puzzle("ranger"))
        self.chess_melee_scene_button = ThemedButton("Chess Melee Mode", btn_x, start_y + spacing * 1, btn_w, btn_h, font_size=font_size, action=lambda: self.start_puzzle("melee"))
        self.chess_solo_scene_button = ThemedButton("Chess Solo Mode", btn_x, start_y + spacing * 2, btn_w, btn_h, font_size=font_size, action=lambda: self.start_puzzle("solo"))
        self.creator_button = ThemedButton("Map Creator", btn_x, start_y + spacing * 3, btn_w, btn_h, font_size=font_size, action=lambda: self.manager.switch_scene('creator'))
        self.settings_button = ThemedButton("Settings", btn_x, start_y + spacing * 4, btn_w, btn_h, font_size=font_size, action=lambda: self.manager.switch_scene('settings'))
        self.credit_scene_button = ThemedButton("Credits", btn_x, start_y + spacing * 5, btn_w, btn_h, font_size=font_size)
        self.quit_button = ThemedButton("Quit", btn_x, start_y + spacing * 6, btn_w, btn_h, font_size=font_size, action=self.quit)

        self.ranger_rect = pygame.Rect(btn_x, start_y + spacing * 0, btn_w, btn_h)
        self.melee_rect = pygame.Rect(btn_x, start_y + spacing * 1, btn_w, btn_h)
        self.solo_rect = pygame.Rect(btn_x, start_y + spacing * 2, btn_w, btn_h)
        self.preview_size = min(self.SCREEN_WIDTH * 0.45, self.SCREEN_HEIGHT * 0.7)
        self.preview_sq_size = int(self.preview_size // 8)
        self.preview_x = self.SCREEN_WIDTH * 0.55
        self.preview_y = (self.SCREEN_HEIGHT - self.preview_size) // 2
        
        self.preview_images = load_images(self.preview_sq_size)
        self.ranger_maps = self.load_maps("ranger")
        self.melee_maps = self.load_maps("melee")
        self.solo_maps = self.load_maps("solo")
        self.hovered_mode = None
        self.current_preview_map = None

    def start_puzzle(self, mode):
        starting_map = None
        if self.hovered_mode == mode and self.current_preview_map:
            starting_map = self.current_preview_map
        self.manager.switch_scene('puzzle', mode, starting_map)

    def load_maps(self, mode):
        all_maps = []
        try:
            path = DATA_URL + f'chess_{mode}/puzzle_map.json'
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                    for key in data:
                        all_maps.extend(data[key])
        except Exception as e:
            print(f"Error loading maps for preview: {e}")
        return all_maps

    def update(self, event_list):
        mouse_pos = pygame.mouse.get_pos()
        target_mode = None

        if self.ranger_rect.collidepoint(mouse_pos):
            target_mode = "ranger"
        elif self.melee_rect.collidepoint(mouse_pos):
            target_mode = "melee"
        elif self.solo_rect.collidepoint(mouse_pos):  
            target_mode = "solo"
        if target_mode != self.hovered_mode:
            self.hovered_mode = target_mode
            
            if target_mode == "ranger" and self.ranger_maps:
                self.current_preview_map = random.choice(self.ranger_maps)
            elif target_mode == "melee" and self.melee_maps:
                self.current_preview_map = random.choice(self.melee_maps)
            elif target_mode == "solo" and self.solo_maps:  # 👈 THÊM MỚI
                self.current_preview_map = random.choice(self.solo_maps)
            else:
                self.current_preview_map = None

        for event in event_list:
            if self.chess_ranger_scene_button.check_click(event): pass
            elif self.chess_melee_scene_button.check_click(event): pass
            elif self.chess_solo_scene_button.check_click(event):  
                pass
            elif self.creator_button.check_click(event): pass
            elif self.settings_button.check_click(event): pass
            elif self.credit_scene_button.check_click(event): pass
            elif self.quit_button.check_click(event): pass
                
    def draw(self):
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)
        self.logo_image.draw(screen)
        self.chess_ranger_scene_button.draw(screen)
        self.chess_melee_scene_button.draw(screen)
        self.chess_solo_scene_button.draw(screen)
        self.creator_button.draw(screen)
        self.settings_button.draw(screen)
        self.credit_scene_button.draw(screen)
        self.quit_button.draw(screen)

        if self.hovered_mode and self.current_preview_map:
            self.draw_preview_board(screen)

    def draw_preview_board(self, screen):
        border_rect = pygame.Rect(self.preview_x - 5, self.preview_y - 5, self.preview_size + 10, self.preview_size + 10)
        pygame.draw.rect(screen, (50, 50, 50), border_rect)
        
        for r in range(8):
            for c in range(8):
                x = self.preview_x + c * self.preview_sq_size
                y = self.preview_y + r * self.preview_sq_size
                
                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(screen, color, (x, y, self.preview_sq_size, self.preview_sq_size))
                
                code = self.current_preview_map[r][c]
                if code != 0:
                    piece_cls = int_to_piece[abs(code)]
                    p_obj = piece_cls(code > 0)
                    img_key = p_obj.get_short_name()
                    if img_key in self.preview_images:
                        screen.blit(self.preview_images[img_key], (x, y))

    def quit(self):
        pygame.quit()
        sys.exit()