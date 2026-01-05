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

# -------------------- LOGO --------------------
LOGO = pygame.image.load("C:\\Mon Armoire Logo.png")
LOGO = pygame.transform.scale(LOGO, (140, 140))

# -------------------- INPUT BOX --------------------
class InputBox:
    def __init__(self, x, y, w, h, password=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.password = password

    def handle(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(e.pos)
        if e.type == pygame.KEYDOWN and self.active:
            if e.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif e.key != pygame.K_RETURN:
                self.text += e.unicode

    def draw(self):
        pygame.draw.rect(WIN, BLUE if self.active else GRAY, self.rect, 2, 8)
        txt = "*" * len(self.text) if self.password else self.text
        WIN.blit(FONT.render(txt, True, BLACK), (self.rect.x + 8, self.rect.y + 8))

# -------------------- BUTTON --------------------
def button(rect, text):
    hover = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(WIN, HOVER if hover else BLUE, rect, border_radius=10)
    WIN.blit(FONT.render(text, True, BLACK), FONT.render(text, True, BLACK).get_rect(center=rect.center))
    return hover

# -------------------- INPUTS --------------------
su_user = InputBox(150, 230, 200, 42)
su_email = InputBox(150, 285, 200, 42)
su_pass = InputBox(150, 340, 200, 42, True)

li_user = InputBox(150, 270, 200, 42)
li_pass = InputBox(150, 325, 200, 42, True)

message = ""

# -------------------- LOOP --------------------
run = True
while run:
    WIN.fill(WHITE)
    WIN.blit(LOGO, (WIDTH//2 - 70, 30))

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            run = False

        if screen == HOME and e.type == pygame.MOUSEBUTTONDOWN:
            if login_btn.collidepoint(e.pos):
                screen = LOGIN
            if signup_btn.collidepoint(e.pos):
                screen = SIGNUP

        if screen == SIGNUP:
            for b in [su_user, su_email, su_pass]:
                b.handle(e)
            if e.type == pygame.MOUSEBUTTONDOWN:
                if submit.collidepoint(e.pos):
                    ok, msg = signup(su_user.text, su_email.text, su_pass.text)
                    message = msg
                    if ok:
                        screen = HOME
                if back.collidepoint(e.pos):
                    screen = HOME

        if screen == LOGIN:
            for b in [li_user, li_pass]:
                b.handle(e)
            if e.type == pygame.MOUSEBUTTONDOWN:
                if submit.collidepoint(e.pos):
                    ok, msg = login(li_user.text, li_pass.text)
                    message = msg
                if back.collidepoint(e.pos):
                    screen = HOME

    # -------------------- DRAW --------------------
    if screen == HOME:
        login_btn = pygame.Rect(150, 330, 200, 45)
        signup_btn = pygame.Rect(150, 390, 200, 45)
        button(login_btn, "Login")
        button(signup_btn, "Signup")

    if screen == SIGNUP:
        for txt, box in zip(["Username", "Email", "Password"], [su_user, su_email, su_pass]):
            WIN.blit(SMALL.render(txt, True, BLACK), (box.rect.x, box.rect.y - 22))
            box.draw()
        submit = pygame.Rect(150, 400, 200, 45)
        back = pygame.Rect(20, 20, 80, 35)
        button(submit, "Create Account")
        button(back, "Back")

    if screen == LOGIN:
        for txt, box in zip(["Username or Email", "Password"], [li_user, li_pass]):
            WIN.blit(SMALL.render(txt, True, BLACK), (box.rect.x, box.rect.y - 22))
            box.draw()
        submit = pygame.Rect(150, 400, 200, 45)
        back = pygame.Rect(20, 20, 80, 35)
        button(submit, "Login")
        button(back, "Back")

    if message:
        WIN.blit(SMALL.render(message, True, RED), (WIDTH//2 - 90, HEIGHT - 40))

    pygame.display.flip()

pygame.quit()
