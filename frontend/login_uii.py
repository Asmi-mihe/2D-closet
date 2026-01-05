import pygame
from backend.auth import signup, login

pygame.init()

# -------------------- CONFIG --------------------
WIDTH, HEIGHT = 500, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mon Armoire")

HOME, LOGIN, SIGNUP = "home", "login", "signup"
screen = HOME

# -------------------- COLORS --------------------
WHITE = (250, 250, 250)
BLACK = (30, 30, 30)
BLUE = (180, 215, 255)
HOVER = (160, 200, 245)
GRAY = (210, 210, 210)
RED = (200, 50, 50)

# -------------------- FONTS --------------------
FONT = pygame.font.Font(None, 36)
SMALL = pygame.font.Font(None, 24)
TITLE_FONT = pygame.font.Font(None, 48)

# -------------------- IMAGES --------------------
BG = pygame.image.load("C:\\2D-closet\\static\\images\\bg.png")
BG = pygame.transform.scale(BG, (WIDTH, HEIGHT))

LOGO = pygame.image.load("C:\\2D-closet\\static\\images\\Logo.png")
LOGO = pygame.transform.scale(LOGO, (140, 140))

# -------------------- INPUT BOX --------------------
class InputBox:
    def __init__(self, x, y, w, h, password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.password = password

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(e.pos)

        if e.type == pygame.KEYDOWN and self.active:
            if e.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif e.key != pygame.K_RETURN:
                self.text += e.unicode

    def draw(self):
        pygame.draw.rect(WIN, BLUE if self.active else GRAY, self.rect, 2, 8)
        display = "*" * len(self.text) if self.password else self.text
        WIN.blit(FONT.render(display, True, BLACK),
                 (self.rect.x + 8, self.rect.y + 8))

# -------------------- BUTTON --------------------
def draw_button(rect, text):
    hover = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(WIN, HOVER if hover else BLUE, rect, border_radius=10)
    text_surf = FONT.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    WIN.blit(text_surf, text_rect)

# -------------------- INPUTS --------------------
su_user = InputBox(150, 230, 200, 42)
su_email = InputBox(150, 285, 200, 42)
su_pass = InputBox(150, 340, 200, 42, True)

li_user = InputBox(150, 270, 200, 42)
li_pass = InputBox(150, 325, 200, 42, True)

# -------------------- BUTTON RECTS --------------------
login_btn = pygame.Rect(150, 330, 200, 45)
signup_btn = pygame.Rect(150, 390, 200, 45)
submit_btn = pygame.Rect(150, 400, 200, 45)
back_btn = pygame.Rect(20, 20, 80, 35)

# -------------------- MESSAGE --------------------
message = ""
message_timer = 0  # timer to hide messages

# -------------------- MAIN LOOP --------------------
run = True
clock = pygame.time.Clock()

while run:
    clock.tick(60)
    
    # -------------------- DRAW BACKGROUND & LOGO --------------------
    WIN.blit(BG, (0, 0))
    WIN.blit(LOGO, (WIDTH // 2 - 70, 30))
    
    # Title text
    title_surf = TITLE_FONT.render("Mon Armoire", True, BLACK)
    title_rect = title_surf.get_rect(center=(WIDTH // 2, 180))
    WIN.blit(title_surf, title_rect)

    # -------------------- EVENTS --------------------
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False

        # -------- HOME EVENTS --------
        if screen == HOME and e.type == pygame.MOUSEBUTTONDOWN:
            if login_btn.collidepoint(e.pos):
                screen = LOGIN
                message = ""
            if signup_btn.collidepoint(e.pos):
                screen = SIGNUP
                message = ""

        # -------- SIGNUP EVENTS --------
        if screen == SIGNUP:
            for box in [su_user, su_email, su_pass]:
                box.handle_event(e)

            if e.type == pygame.MOUSEBUTTONDOWN:
                if submit_btn.collidepoint(e.pos):
                    ok, msg = signup(su_user.text, su_email.text, su_pass.text)
                    message = msg
                    message_timer = pygame.time.get_ticks()
                    if ok:
                        screen = HOME
                if back_btn.collidepoint(e.pos):
                    screen = HOME

        # -------- LOGIN EVENTS --------
        if screen == LOGIN:
            for box in [li_user, li_pass]:
                box.handle_event(e)

            if e.type == pygame.MOUSEBUTTONDOWN:
                if submit_btn.collidepoint(e.pos):
                    ok, msg = login(li_user.text, li_pass.text)
                    message = msg
                    message_timer = pygame.time.get_ticks()
                if back_btn.collidepoint(e.pos):
                    screen = HOME

    # -------------------- DRAW SCREENS --------------------
    if screen == HOME:
        draw_button(login_btn, "Login")
        draw_button(signup_btn, "Signup")

    if screen == SIGNUP:
        for label, box in zip(
            ["Username", "Email", "Password"],
            [su_user, su_email, su_pass]
        ):
            WIN.blit(SMALL.render(label, True, BLACK),
                     (box.rect.x, box.rect.y - 22))
            box.draw()
        draw_button(submit_btn, "Create Account")
        draw_button(back_btn, "Back")

    if screen == LOGIN:
        for label, box in zip(
            ["Username or Email", "Password"],
            [li_user, li_pass]
        ):
            WIN.blit(SMALL.render(label, True, BLACK),
                     (box.rect.x, box.rect.y - 22))
            box.draw()
        draw_button(submit_btn, "Login")
        draw_button(back_btn, "Back")

    # -------------------- DRAW MESSAGE --------------------
    if message:
        # show message for 3 seconds
        if pygame.time.get_ticks() - message_timer < 3000:
            WIN.blit(SMALL.render(message, True, RED),
                     (WIDTH // 2 - 100, HEIGHT - 40))
        else:
            message = ""

    pygame.display.flip()

pygame.quit()
