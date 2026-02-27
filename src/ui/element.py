import pygame
import sys

from settings import *

# --- Theme Colors ---
THEME = {
    'primary': (210, 180, 140),
    'shadow': (139, 69, 19),
    'highlight': (255, 248, 220),
    'text': (50, 30, 10),
    'box_bg': (30, 30, 30, 200)
}

class UIElement:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 0, 0)

    def draw(self, screen):
        pass

    def update(self):
        pass

class ThemedButton(UIElement):
    def __init__(self, text, x, y, width, height, font_size=None, action=None):
        super().__init__(x, y)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        
        if font_size is None:
            font_size = int(height * 0.5)
            
        self.font = pygame.font.Font(None, font_size)
        self.elevation = int(height * 0.1)
        self.dynamic_elevation = self.elevation
        self.y_original = y
        self.pressed = False
        self.hovered = False
        self.border_radius = int(height * 0.2)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)

        if self.pressed:
            self.dynamic_elevation = 0
            curr_y = self.y_original + self.elevation
            main_color = THEME['shadow']
        elif self.hovered:
            self.dynamic_elevation = self.elevation
            curr_y = self.y_original
            main_color = THEME['highlight']
        else:
            self.dynamic_elevation = self.elevation
            curr_y = self.y_original
            main_color = THEME['primary']

        shadow_rect = pygame.Rect(self.rect.x, self.y_original + self.elevation, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, THEME['shadow'], shadow_rect, border_radius=self.border_radius)

        self.top_rect = pygame.Rect(self.rect.x, curr_y, self.rect.width, self.rect.height)
        pygame.draw.rect(screen, main_color, self.top_rect, border_radius=self.border_radius)
        pygame.draw.rect(screen, THEME['text'], self.top_rect, 2, border_radius=self.border_radius)

        text_surf = self.font.render(self.text, True, THEME['text'])
        text_rect = text_surf.get_rect(center=self.top_rect.center)
        screen.blit(text_surf, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.top_rect.collidepoint(event.pos):
                self.pressed = True
                return False
        
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed:
                self.pressed = False
                if self.top_rect.collidepoint(event.pos):
                    if self.action:
                        self.action()
                    return True
        return False

class RuleBox(UIElement):
    def __init__(self, x, y, width, height, text_list, font_size=None):
        super().__init__(x, y)
        self.rect = pygame.Rect(x, y, width, height)
        self.text_list = text_list
        
        if font_size is None:
            font_size = int(width * 0.08)
            
        self.font = pygame.font.Font(None, font_size)
        self.bg_color = THEME['box_bg']
        self.text_color = (240, 240, 240)
        self.line_height = int(font_size * 1.1)
        self.rendered_lines = self.wrap_text(self.text_list)

    def wrap_text(self, lines):
        wrapped_lines = []
        for line in lines:
            words = line.split(' ')
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                fw, fh = self.font.size(test_line)
                if fw < self.rect.width - 20:
                    current_line = test_line
                else:
                    wrapped_lines.append(current_line)
                    current_line = word + " "
            wrapped_lines.append(current_line)
        return wrapped_lines

    def draw(self, screen):
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill(self.bg_color) 
        screen.blit(s, (self.rect.x, self.rect.y))
        pygame.draw.rect(screen, THEME['primary'], self.rect, 3)

        y_offset = int(self.rect.height * 0.1)
        x_offset = int(self.rect.width * 0.05)
        
        for line in self.rendered_lines:
            text_surf = self.font.render(line, True, self.text_color)
            screen.blit(text_surf, (self.rect.x + x_offset, self.rect.y + y_offset))
            y_offset += self.line_height

class Image(UIElement):
    def __init__(self, image_url, x, y, size = None) -> None:
        super().__init__(x, y)
        try:
            self.logo_image = pygame.image.load(image_url).convert_alpha()
            if size is not None:
                self.logo_image = pygame.transform.smoothscale(self.logo_image, size)
        except pygame.error as e:
            print(f"Error loading image: {e}")
            sys.exit()
        
        self.rect = self.logo_image.get_rect(topleft=(x,y))

    def draw(self, screen):
        screen.blit(self.logo_image, (self.rect.x, self.rect.y))

class ClickableImage(UIElement):
    def __init__(self, image_path, x, y, size=None, action=None, func=None):
        super().__init__(x, y)
        self.action = action  
        self.is_hovered = False

        try:
            self.surface = pygame.image.load(image_path).convert_alpha()
            
            if size is not None:
                self.surface = pygame.transform.smoothscale(self.surface, size)
            
            if func:
                self.surface = func(self.surface)

            width = self.surface.get_width()
            height = self.surface.get_height()
            self.hover_surface = pygame.transform.smoothscale(
                self.surface, 
                (int(width * 1.1), int(height * 1.1))
            )
                
        except pygame.error as e:
            print(f"Error loading image: {e}")
            sys.exit()

        self.rect = self.surface.get_rect(topleft=(x, y))
        self.hover_rect = self.hover_surface.get_rect(center=self.rect.center)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if self.is_hovered:
            screen.blit(self.hover_surface, self.hover_rect)
        else:
            screen.blit(self.surface, self.rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False
    
class NumberSelector(UIElement):
    def __init__(self, x, y, height, min_val, max_val, initial_val, left_img_path, right_img_path, left_action=None, right_action=None, image_func = None):
        super().__init__(x, y)
        self.value = initial_val
        self.min_val = min_val
        self.max_val = max_val
        self.left_action = left_action
        self.right_action = right_action
        
        self.size = height
        font_size = int(height * 0.8)
        self.font = pygame.font.Font(None, font_size)
        self.text_color = (255, 255, 255)
        
        self.spacing = int(height * 0.5)
        self.text_area_width = int(height * 1.5)

        def decrease():
            if self.value > self.min_val:
                self.value -= 1
                self.update_text()
                if self.left_action:
                    self.left_action(self.value)

        self.btn_left = ClickableImage(left_img_path, x, y, size=(int(height), int(height)), action=decrease, func=image_func)

        def increase():
            if self.value < self.max_val:
                self.value += 1
                self.update_text()
                if self.right_action:
                    self.right_action(self.value)

        btn_right_x = x + int(height) + self.spacing + self.text_area_width + self.spacing
        self.btn_right = ClickableImage(right_img_path, btn_right_x, y, size=(int(height), int(height)), action=increase, func=image_func)

        self.text_surf = None
        self.text_rect = None
        self.update_text()

    def update_text(self):
        text_str = str(self.value)
        self.text_surf = self.font.render(text_str, True, self.text_color)
        start_x = self.btn_left.rect.x + self.size + self.spacing
        center_x = start_x + (self.text_area_width // 2)
        center_y = self.btn_left.rect.y + self.size // 2 
        self.text_rect = self.text_surf.get_rect(center=(center_x, center_y))

    def handle_event(self, event):
        self.btn_left.check_click(event)
        self.btn_right.check_click(event)

    def draw(self, screen):
        self.btn_left.draw(screen)
        if self.text_surf:
            screen.blit(self.text_surf, self.text_rect)
        self.btn_right.draw(screen)
        
    def get_value(self):
        return self.value

class StatsPanel(UIElement):
    def __init__(self, x, y, width, font_size=30, text_list:list[str]=[]):
        self.rect = pygame.Rect(x, y, width, 0)
        self.font = pygame.font.Font(None, font_size)
        self.font_size = font_size
        self.bg_color = (30, 30, 30, 200)
        self.text_color = (255, 255, 255)
        self.base_text_list = text_list

        self.nodes_visited = 0
        self.path_length = 0
        self.status = "Ready"
        self.path = None
        
        self.lines_to_draw = []
        self.line_height = int(font_size * 1.2)
        self.side_padding = int(width * 0.05)
        self.top_margin = int(font_size * 0.8)    
        self.bottom_padding = int(font_size * 0.5)
        
        self.recalculate_layout()

    def update_stats(self, nodes=None, status=None, path=None):
        if nodes is not None: self.nodes_visited = nodes
        if status is not None: self.status = status
        if path is not None: 
            self.path = path
            self.path_length = len(path)
        
        self.recalculate_layout()

    def recalculate_layout(self):
        self.lines_to_draw = self.base_text_list[:]
        self.lines_to_draw.append(f"Status: {self.status}")
        self.lines_to_draw.append(f"Nodes: {self.nodes_visited}")
        
        if self.path is not None:
            self.lines_to_draw.append(f"Steps: {self.path_length}")
            if self.path_length > 0:
                self.lines_to_draw.append("Path:")
                moves_str = []
                for move in self.path:
                    start = f"{chr(move[1]+97)}{8-move[0]}"
                    end = f"{chr(move[3]+97)}{8-move[2]}"
                    moves_str.append(f"{start}-{end}")
                
                full_path_str = " -> ".join(moves_str)
                char_width_approx = self.font_size * 0.4
                chars_per_line = max(10, int(self.rect.width / char_width_approx)) 
                
                for i in range(0, len(full_path_str), chars_per_line):
                    self.lines_to_draw.append(full_path_str[i : i + chars_per_line])
        num_lines = len(self.lines_to_draw)
        new_height = self.top_margin + (num_lines * self.line_height) + self.bottom_padding
        self.rect.height = new_height

    def draw(self, screen):
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill(self.bg_color)
        screen.blit(s, self.rect.topleft)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)

        y_offset = self.top_margin 
        
        for line in self.lines_to_draw:
            surf = self.font.render(line, True, self.text_color)
            screen.blit(surf, (self.rect.x + self.side_padding, self.rect.y + y_offset))
            y_offset += self.line_height

class FeedbackToast(UIElement):
    def __init__(self, x, y, height_ref, min_width_ref):
        self.x = x
        self.y = y
        self.min_width = min_width_ref
        self.height = int(height_ref)
        self.text = ""
        self.is_visible = False
        self.timer = 0
        self.duration = 3000
        
        font_size = int(self.height * 0.5)
        self.font = pygame.font.SysFont("arial", font_size)
        self.color = (0, 255, 0)
        self.bg_color = (30, 30, 30, 220)
        self.border_color = (100, 100, 100)

    def show(self, text, is_error=False):
        self.text = text
        self.is_visible = True
        self.timer = pygame.time.get_ticks()
        self.color = (255, 80, 80) if is_error else (100, 255, 100)
        self.border_color = (200, 50, 50) if is_error else (50, 200, 50)

    def update(self):
        if self.is_visible:
            if pygame.time.get_ticks() - self.timer > self.duration:
                self.is_visible = False

    def draw(self, screen):
        if not self.is_visible:
            return
        text_surf = self.font.render(self.text, True, self.color)
        width = max(self.min_width, text_surf.get_width() + int(self.min_width * 0.2))
        
        rect = pygame.Rect(self.x, self.y, width, self.height)
        s = pygame.Surface((width, self.height), pygame.SRCALPHA)
        s.fill(self.bg_color)
        screen.blit(s, (self.x, self.y)) 
        pygame.draw.rect(screen, self.border_color, rect, 2)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)

class LabelBox(UIElement):
    def __init__(self, text, x, y, width, height, font_size=None):
        super().__init__(x, y)
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        
        if font_size is None:
            font_size = int(height * 0.6)
            
        self.font = pygame.font.SysFont("arial", font_size, bold=True)
        self.bg_color = COLOR_LIGHT
        self.border_color = COLOR_DARK
        self.text_color = THEME['text']

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

class Slider(UIElement):
    def __init__(self, x, y, width, height, limit : tuple[int, int], initial_val, action=None):
        super().__init__(x, y)
        self.rect = pygame.Rect(x, y, width, int(height * 0.2))
        self.rect.centery = y
        self.min_val, self.max_val = limit
        self.value = initial_val
        self.action = action
        self.dragging = False
        
        self.knob_width = int(height * 0.4)
        self.knob_height = int(height * 0.6)
        
        pct = (self.value - self.min_val) / (self.max_val - self.min_val)
        knob_x = self.rect.x + (self.rect.width * pct)
        self.knob_rect = pygame.Rect(0, 0, self.knob_width, self.knob_height)
        self.knob_rect.center = (knob_x, y)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.knob_rect.collidepoint(event.pos) or self.rect.inflate(0, self.knob_height).collidepoint(event.pos):
                    self.dragging = True
                    self.update_from_mouse(event.pos[0])
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.update_from_mouse(event.pos[0])
                return True
        return False

    def update_from_mouse(self, mouse_x):
        x = max(self.rect.left, min(mouse_x, self.rect.right))
        self.knob_rect.centerx = x
        
        pct = (x - self.rect.left) / self.rect.width
        self.value = int(self.min_val + (self.max_val - self.min_val) * pct)
        
        if self.action:
            self.action(self.value)

    def draw(self, screen):
        pygame.draw.rect(screen, (100, 100, 100), self.rect, border_radius=int(self.rect.height//2))
        
        pygame.draw.rect(screen, THEME['primary'], self.knob_rect, border_radius=int(self.knob_width//4))
        pygame.draw.rect(screen, THEME['text'], self.knob_rect, 2, border_radius=int(self.knob_width//4))

class ToggleSwitch(UIElement):
    def __init__(self, x, y, width, height, initial_state, on_toggle=None):
        super().__init__(x, y)
        self.rect = pygame.Rect(x, y, width, height)
        self.state = initial_state
        self.on_toggle = on_toggle
        self.slide_pos = 1.0 if self.state else 0.0 

    def update(self):
        target = 1.0 if self.state else 0.0
        if self.slide_pos < target: self.slide_pos = min(target, self.slide_pos + 0.1)
        elif self.slide_pos > target: self.slide_pos = max(target, self.slide_pos - 0.1)

    def draw(self, screen):
        self.update()
        bg_color = (100, 200, 100) if self.state else (200, 100, 100)
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=self.rect.height//2)
        pygame.draw.rect(screen, (50, 50, 50), self.rect, 2, border_radius=self.rect.height//2)
        
        padding = int(self.rect.height * 0.1)
        knob_size = self.rect.height - (padding * 2)
        min_x = self.rect.x + padding
        max_x = self.rect.x + self.rect.width - padding - knob_size
        current_x = min_x + (max_x - min_x) * self.slide_pos
        
        knob_rect = pygame.Rect(current_x, self.rect.y + padding, knob_size, knob_size)
        pygame.draw.ellipse(screen, (255, 255, 255), knob_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
                if self.on_toggle: self.on_toggle(self.state)
                return True
        return False