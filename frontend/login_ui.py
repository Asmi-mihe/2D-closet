import pygame
from backend.auth import signup, login

# Initialize pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 500, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mon Armoire Login/Signup")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
HOVER_BLUE = (135, 206, 250)
PASTEL_PINK = (255, 182, 193)
PASTEL_PURPLE = (216, 191, 216)
GRAY = (200, 200, 200)

# Fonts
FONT = pygame.font.Font(None, 36)
LABEL_FONT = pygame.font.Font(None, 28)

# Load logo
LOGO = pygame.image.load(r"C:\Mon Armoire Logo.png")  
LOGO = pygame.transform.smoothscale(LOGO, (150, 150))
WIN.blit(LOGO, (WIDTH // 2 - LOGO.get_width() // 2, 30))

# Input box
class InputBox:
    def __init__(self, x, y, w, h, text='', is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = PASTEL_PURPLE
        self.text = text
        self.txt_surface = FONT.render(text, True, BLACK)
        self.active = False
        self.is_password = is_password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = PASTEL_PINK if self.active else PASTEL_PURPLE

        if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_RETURN:
                    pass  
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

                self.txt_surface = FONT.render(self.text, True, BLACK)
                display_text = '*' * len(self.text) if self.is_password else self.text
                self.txt_surface = FONT.render(display_text, True, BLACK)

    def draw(self, win):
        win.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(win, self.color, self.rect, border_radius=12)

# Create username and password input boxes
username_box = InputBox(150, 220, 200, 40)
password_box = InputBox(150, 300, 200, 40, is_password=True)

input_boxes = [username_box, password_box]

# Buttons with hover effect
def draw_button(win, rect, text):
    mouse_pos = pygame.mouse.get_pos()
    color = HOVER_BLUE if rect.collidepoint(mouse_pos) else LIGHT_BLUE
    pygame.draw.rect(win, color, rect, border_radius=12)
    txt_surf = FONT.render(text, True, BLACK)
    win.blit(txt_surf, (rect.x + 10, rect.y + 5))

signup_rect = pygame.Rect(150, 360, 90, 40)
login_rect = pygame.Rect(260, 360, 90, 40)

# Message
message = ""

# Buttons (simplest rectangles)
def draw_button(win, rect, text):
    pygame.draw.rect(win, LIGHT_BLUE, rect, border_radius=12)
    txt_surf = FONT.render(text, True, BLACK)
    win.blit(txt_surf, (rect.x + 10, rect.y + 5))

signup_rect = pygame.Rect(150, 500, 90, 40)
login_rect = pygame.Rect(260, 500, 90, 40)

# Main loop
run = True
while run:
    WIN.fill(WHITE)  # Background

    # Draw logo first (on top of background)
    WIN.blit(LOGO, (WIDTH//2 - LOGO.get_width()//2, 50))

    # Draw labels
    username_label = FONT.render("Username:", True, BLACK)
    password_label = FONT.render("Password:", True, BLACK)
    WIN.blit(username_label, (username_box.rect.x, username_box.rect.y - 25))
    WIN.blit(password_label, (password_box.rect.x, password_box.rect.y - 25))

    # Draw input boxes (text appears on top of their boxes)
    for box in input_boxes:
        box.draw(WIN)

    # Draw buttons last (on top of background, below inputs)
    draw_button(WIN, signup_rect, "Signup")
    draw_button(WIN, login_rect, "Login")

    # Draw message below buttons
    msg_surf = FONT.render(message, True, BLACK)
    WIN.blit(msg_surf, (150, login_rect.y + 60))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        for box in input_boxes:
            box.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if signup_rect.collidepoint(event.pos):
                success, msg = signup(username_box.text, password_box.text)
                message = msg
            if login_rect.collidepoint(event.pos):
                success, msg = login(username_box.text, password_box.text)
                message = msg

    pygame.display.flip()
pygame.quit()