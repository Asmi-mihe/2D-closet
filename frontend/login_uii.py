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
GRAY = (200, 200, 200)
BUTTON_HOVER = (135, 206, 250)

# Fonts
FONT = pygame.font.Font(None, 36)
LABEL_FONT = pygame.font.Font(None, 28)

# Load and scale logo
LOGO_IMG = pygame.image.load(r"C:\Mon Armoire Logo.png") 
LOGO_IMG = pygame.transform.scale(LOGO_IMG, (150, 150))
WIN.blit(LOGO_IMG, (WIDTH//2 - LOGO_IMG.get_width()//2, 50))

# Input box class
class InputBox:
    def __init__(self, x, y, w, h, text='', is_password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = GRAY
        self.text = text
        self.txt_surface = FONT.render(text, True, BLACK)
        self.active = False
        self.is_password = is_password

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = LIGHT_BLUE if self.active else GRAY

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                pass
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode

            display_text = '*' * len(self.text) if self.is_password else self.text
            self.txt_surface = FONT.render(display_text, True, BLACK)

    def draw(self, win):
        win.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(win, self.color, self.rect, 2)

# Create input boxes
username_box = InputBox(150, 250, 200, 40)
password_box = InputBox(150, 320, 200, 40, is_password=True)
input_boxes = [username_box, password_box]

# Buttons
signup_rect = pygame.Rect(150, 400, 90, 40)
login_rect = pygame.Rect(260, 400, 90, 40)

def draw_button(win, rect, text, hover=False):
    color = BUTTON_HOVER if hover else LIGHT_BLUE
    pygame.draw.rect(win, color, rect, border_radius=8)
    txt_surf = FONT.render(text, True, BLACK)
    txt_rect = txt_surf.get_rect(center=rect.center)
    win.blit(txt_surf, txt_rect)

# Message
message = ""

# Main loop
run = True
while run:
    WIN.fill(WHITE)

    # Draw logo
    WIN.blit(LOGO_IMG, (WIDTH//2 - LOGO_IMG.get_width()//2, 50))

    # Draw labels
    username_label = LABEL_FONT.render("Username:", True, BLACK)
    password_label = LABEL_FONT.render("Password:", True, BLACK)
    WIN.blit(username_label, (username_box.rect.x, username_box.rect.y - 25))
    WIN.blit(password_label, (password_box.rect.x, password_box.rect.y - 25))

    # Draw input boxes
    for box in input_boxes:
        box.draw(WIN)

    # Draw buttons with hover effect
    mouse_pos = pygame.mouse.get_pos()
    draw_button(WIN, signup_rect, "Signup", hover=signup_rect.collidepoint(mouse_pos))
    draw_button(WIN, login_rect, "Login", hover=login_rect.collidepoint(mouse_pos))

    # Draw message below buttons
    msg_surf = FONT.render(message, True, BLACK)
    WIN.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, login_rect.y + 60))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        for box in input_boxes:
            box.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if signup_rect.collidepoint(event.pos):
                try:
                    success, msg = signup(username_box.text, password_box.text)
                    message = msg
                except Exception as e:
                    message = str(e)
            if login_rect.collidepoint(event.pos):
                try:
                    success, msg = login(username_box.text, password_box.text)
                    message = msg
                except Exception as e:
                    message = str(e)

    pygame.display.flip()

pygame.quit()
