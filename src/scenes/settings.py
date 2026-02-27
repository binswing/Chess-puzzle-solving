from src.scenes.scene import Scene
from src.ui.element import *
import settings
import pygame

class SettingsScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        screen = pygame.display.get_surface()
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen.get_size()
        
        title_font_size = int(self.SCREEN_HEIGHT * 0.08)
        text_font_size = int(self.SCREEN_HEIGHT * 0.035)
        
        self.title_font = pygame.font.SysFont("arial", title_font_size, bold=True)
        self.text_font = pygame.font.SysFont("arial", text_font_size)
        
        self.title_surf = self.title_font.render("Settings", True, COLOR_LIGHT)
        self.title_rect = self.title_surf.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 10))

        center_x = self.SCREEN_WIDTH // 2
        start_y = self.SCREEN_HEIGHT // 4
        gap = self.SCREEN_HEIGHT // 8
        
        label_col_x = center_x - (self.SCREEN_WIDTH // 4) 
        control_col_x = center_x + (self.SCREEN_WIDTH // 20)
        
        label_w = self.SCREEN_WIDTH // 5
        label_h = self.SCREEN_HEIGHT // 15
        slider_w = self.SCREEN_WIDTH // 6
        slider_h = int(label_h * 0.8)

        self.anim_label = LabelBox("Search Animation", label_col_x, start_y, label_w, label_h, font_size=text_font_size)
        
        toggle_w = int(slider_w * 0.4)
        toggle_h = int(label_h * 0.8)
        toggle_y_offset = (label_h - toggle_h) // 2
        
        self.anim_toggle = ToggleSwitch(control_col_x, start_y + toggle_y_offset, toggle_w, toggle_h, settings.SEARCH_ANIMATION, lambda val: self.set_attibute("SEARCH_ANIMATION", val))

        self.play_speed_y = start_y + gap
        self.play_speed_label = LabelBox("Play Speed", label_col_x, self.play_speed_y, label_w, label_h, font_size=text_font_size)
        self.play_speed_slider = Slider(control_col_x, self.play_speed_y + label_h//2, slider_w, slider_h, PLAY_SPEED_LIMIT, settings.PLAY_ANIMATION_DURATION, lambda val: self.set_attibute("PLAY_ANIMATION_DURATION", val))
        
        self.search_speed_y = self.play_speed_y + gap
        self.search_speed_label = LabelBox("Search Speed", label_col_x, self.search_speed_y, label_w, label_h, font_size=text_font_size)
        self.search_speed_slider = Slider(control_col_x, self.search_speed_y + label_h//2, slider_w, slider_h, SEARCH_SPEED_LIMIT, settings.SEARCH_ANIMATION_DURATION, lambda val: self.set_attibute("SEARCH_ANIMATION_DURATION", val))

        self.fps_y = self.search_speed_y + gap
        self.fps_label = LabelBox("Target FPS", label_col_x, self.fps_y, label_w, label_h, font_size=text_font_size)
        self.fps_slider = Slider(control_col_x, self.fps_y + label_h//2, slider_w, slider_h, FPS_LIMIT, settings.FPS, lambda val: self.set_attibute("FPS", val))

        btn_w = self.SCREEN_WIDTH // 6
        btn_h = self.SCREEN_HEIGHT // 12
        btn_y = self.SCREEN_HEIGHT - (self.SCREEN_HEIGHT // 6)
        self.back_btn = ThemedButton("Back to Menu", center_x - btn_w//2, btn_y, btn_w, btn_h, font_size = text_font_size, action = lambda: self.manager.switch_scene('menu'))

    def set_attibute(self, attribute_name, value):
        setattr(settings, attribute_name, value)
        settings.save_settings()

    def update(self, event_list):
        for event in event_list:
            if self.anim_toggle.check_click(event): pass
            elif self.back_btn.check_click(event): pass

            self.play_speed_slider.handle_event(event)
            self.search_speed_slider.handle_event(event)
            self.fps_slider.handle_event(event)

    def draw(self):
        screen = pygame.display.get_surface()
        screen.fill(COLOR_BG)
        screen.blit(self.title_surf, self.title_rect)
        
        self.anim_label.draw(screen)
        self.play_speed_label.draw(screen)
        self.search_speed_label.draw(screen)
        self.fps_label.draw(screen)
        
        self.anim_toggle.draw(screen)
        self.play_speed_slider.draw(screen)
        self.search_speed_slider.draw(screen)
        self.fps_slider.draw(screen)
        
        self.draw_value_text(screen, f"{settings.PLAY_ANIMATION_DURATION}ms", self.play_speed_slider)
        self.draw_value_text(screen, f"{settings.SEARCH_ANIMATION_DURATION}ms", self.search_speed_slider)
        self.draw_value_text(screen, f"{settings.FPS}", self.fps_slider)

        self.back_btn.draw(screen)

    def draw_value_text(self, screen, text, slider):
        surf = self.text_font.render(text, True, COLOR_LIGHT)
        padding_x = self.SCREEN_WIDTH // 50
        screen.blit(surf, (slider.rect.right + padding_x, slider.rect.y - 10))