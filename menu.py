import pygame
import os
import sys

class Button:
    def __init__(self, x, y, width, height, text, font, color=(255, 255, 255), hover_color=(200, 200, 200)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.action = None
        
    def draw(self, surface):
        # Draw button with hover effect
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2, border_radius=8)  # Border
        
        # Render text
        text_surface = self.font.render(self.text, True, (30, 30, 30))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def check_click(self):
        return self.is_hovered and pygame.mouse.get_pressed()[0]

class Slider:
    def __init__(self, x, y, width, height, min_val=0, max_val=100, current_val=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_radius = height  # Handle is circular
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = current_val
        self.dragging = False
        self.label_font = pygame.font.SysFont('Arial', 22)
        
    def draw(self, surface):
        # Draw track
        pygame.draw.rect(surface, (150, 150, 150), self.rect, border_radius=5)
        
        # Calculate handle position
        handle_x = self.rect.x + (self.current_val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_y = self.rect.y + self.rect.height // 2
        
        # Draw active part of track
        active_rect = pygame.Rect(self.rect.x, self.rect.y, handle_x - self.rect.x, self.rect.height)
        pygame.draw.rect(surface, (107, 136, 254), active_rect, border_radius=5)
        
        # Draw handle
        pygame.draw.circle(surface, (255, 255, 255), (int(handle_x), handle_y), self.handle_radius)
        pygame.draw.circle(surface, (180, 180, 180), (int(handle_x), handle_y), self.handle_radius, 1)
        
        # Draw value label
        value_text = self.label_font.render(f"{int(self.current_val)}%", True, (30, 30, 30))
        value_rect = value_text.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
        surface.blit(value_text, value_rect)
        
    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        
        handle_x = self.rect.x + (self.current_val - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_y = self.rect.y + self.rect.height // 2
        handle_rect = pygame.Rect(handle_x - self.handle_radius, handle_y - self.handle_radius, 
                                self.handle_radius * 2, self.handle_radius * 2)
        
        # Check for mouse press on handle
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if handle_rect.collidepoint(event.pos):
                    self.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
        
        # Update position if dragging
        if self.dragging:
            # Calculate new value based on mouse position
            pos_ratio = max(0, min(1, (mouse_pos[0] - self.rect.x) / self.rect.width))
            self.current_val = self.min_val + pos_ratio * (self.max_val - self.min_val)
            return True  # Value changed
        
        return False  # Value unchanged

class GameMenu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Load fonts
        self.title_font = pygame.font.SysFont('Arial', 48)
        self.button_font = pygame.font.SysFont('Arial', 32)
        self.subtitle_font = pygame.font.SysFont('Arial', 24)
        
        # Menu background
        self.bg_color = (245, 245, 245)
        self.panel_color = (235, 235, 235)
        
        # Calculate menu dimensions
        self.menu_width = 400
        self.menu_height = 500
        self.menu_x = (screen_width - self.menu_width) // 2
        self.menu_y = (screen_height - self.menu_height) // 2
        
        # Create buttons
        button_width = 300
        button_height = 50
        button_x = self.menu_x + (self.menu_width - button_width) // 2
        
        self.play_button = Button(button_x, self.menu_y + 180, button_width, button_height, 
                                "Play", self.button_font)
        
        self.exit_button = Button(button_x, self.menu_y + 400, button_width, button_height, 
                                "Exit", self.button_font)
        
        # Create volume slider
        slider_width = 250
        self.volume_slider = Slider(button_x, self.menu_y + 280, slider_width, 20, 0, 100, 30)
        
        # High score
        self.high_score = 0
        self.load_high_score()
        
        # State
        self.game_paused = False
        
    def load_high_score(self):
        if os.path.exists('score.txt'):
            try:
                with open('score.txt', 'r') as file:
                    self.high_score = int(file.read())
            except:
                self.high_score = 0
        
    def draw(self, screen):
        # Draw background overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Draw menu panel
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(screen, self.panel_color, menu_rect, border_radius=15)
        
        # Draw shadow effect
        shadow = pygame.Surface((self.menu_width, self.menu_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 30), (0, 0, self.menu_width, self.menu_height), border_radius=15)
        screen.blit(shadow, (self.menu_x + 5, self.menu_y + 5))
        
        # Draw menu title
        title_text = self.title_font.render("Game Menu", True, (40, 40, 40))
        title_rect = title_text.get_rect(centerx=self.menu_x + self.menu_width // 2, top=self.menu_y + 30)
        screen.blit(title_text, title_rect)
        
        # Draw high score
        score_text = self.subtitle_font.render(f"High Score: {self.high_score}", True, (70, 70, 70))
        score_rect = score_text.get_rect(centerx=self.menu_x + self.menu_width // 2, top=self.menu_y + 100)
        screen.blit(score_text, score_rect)
        
        # Draw buttons
        self.play_button.text = "Resume" if self.game_paused else "Play"
        self.play_button.draw(screen)
        self.exit_button.draw(screen)
        
        # Draw volume slider
        volume_label = self.subtitle_font.render("Volume:", True, (70, 70, 70))
        screen.blit(volume_label, (self.menu_x + 50, self.menu_y + 250))
        self.volume_slider.draw(screen)
        
    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        
        # Check button hover
        self.play_button.check_hover(mouse_pos)
        self.exit_button.check_hover(mouse_pos)
        
        # Update volume slider
        volume_changed = self.volume_slider.update(events)
        
        # Handle volume change
        if volume_changed:
            pygame.mixer.music.set_volume(self.volume_slider.current_val / 100)
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check button clicks
                if self.play_button.check_hover(mouse_pos):
                    return "play"
                elif self.exit_button.check_hover(mouse_pos):
                    return "exit"
        
        return None