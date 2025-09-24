import pygame, sys
pygame.init()

# -------- ventana y colores --------
ANCHO, ALTO = 800, 600
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Cruce - dibujo estático")

VERDE_OSCURO = (0, 100, 0)
GRIS = (160, 160, 160)
BLANCO = (255, 255, 255)
ROJO = (220, 70, 70)
AMARILLO = (245, 205, 70)
VERDE = (70, 200, 110)
CAR1 = (240, 80, 60)
CAR2 = (80, 160, 240)
CAR3 = (80, 200, 130)
CAR4 = (190, 90, 220)
CAR5 = (200, 200, 200)


cx, cy = ANCHO // 2, ALTO // 2
ANCHO_VIA = 200
MITAD = ANCHO_VIA // 2
CEBRA = 48
LANE_OFF = 50

rect_v = pygame.Rect(cx - MITAD, 0, ANCHO_VIA, ALTO)
rect_h = pygame.Rect(0, cy - MITAD, ANCHO, ANCHO_VIA)


STOP_W = cx - MITAD - CEBRA - 6
STOP_E = cx + MITAD + CEBRA + 6
STOP_N = cy - MITAD - CEBRA - 6
STOP_S = cy + MITAD + CEBRA + 6

def draw_center_dashes():

    for y in range(0, cy - MITAD - 10, 28):
        pygame.draw.line(screen, BLANCO, (cx, y), (cx, y + 16), 3)
    for y in range(cy + MITAD + 10, ALTO, 28):
        pygame.draw.line(screen, BLANCO, (cx, y), (cx, y + 16), 3)

    for x in range(0, cx - MITAD - 10, 28):
        pygame.draw.line(screen, BLANCO, (x, cy), (x + 16, cy), 3)
    for x in range(cx + MITAD + 10, ANCHO, 28):
        pygame.draw.line(screen, BLANCO, (x, cy), (x + 16, cy), 3)

def draw_zebra_top_bottom():
    # superior (sobre la vía vertical)
    zona = pygame.Rect(cx - MITAD, cy - MITAD - CEBRA, ANCHO_VIA, CEBRA)

    stripe_h = 10
    gap = 8
    y = zona.top + 4
    while y + stripe_h <= zona.bottom - 4:
        pygame.draw.rect(screen, BLANCO, (zona.left + 2, y, zona.width - 4, stripe_h), border_radius=2)
        y += stripe_h + gap
    # inferior
    zona = pygame.Rect(cx - MITAD, cy + MITAD, ANCHO_VIA, CEBRA)
    y = zona.top + 4
    while y + stripe_h <= zona.bottom - 4:
        pygame.draw.rect(screen, BLANCO, (zona.left + 2, y, zona.width - 4, stripe_h), border_radius=2)
        y += stripe_h + gap

def draw_zebra_left_right():

    zona = pygame.Rect(cx - MITAD - CEBRA, cy - MITAD, CEBRA, ANCHO_VIA)
    stripe_w = 10
    gap = 8
    x = zona.left + 4
    while x + stripe_w <= zona.right - 4:
        pygame.draw.rect(screen, BLANCO, (x, zona.top + 2, stripe_w, zona.height - 4), border_radius=2)
        x += stripe_w + gap

    zona = pygame.Rect(cx + MITAD, cy - MITAD, CEBRA, ANCHO_VIA)
    x = zona.left + 4
    while x + stripe_w <= zona.right - 4:
        pygame.draw.rect(screen, BLANCO, (x, zona.top + 2, stripe_w, zona.height - 4), border_radius=2)
        x += stripe_w + gap

def draw_stop_lines():

    pygame.draw.line(screen, BLANCO, (STOP_W, cy - MITAD), (STOP_W, cy + MITAD), 6)  # oeste
    pygame.draw.line(screen, BLANCO, (STOP_E, cy - MITAD), (STOP_E, cy + MITAD), 6)  # este
    pygame.draw.line(screen, BLANCO, (cx - MITAD, STOP_N), (cx + MITAD, STOP_N), 6)  # norte
    pygame.draw.line(screen, BLANCO, (cx - MITAD, STOP_S), (cx + MITAD, STOP_S), 6)  # sur

def draw_light(x, y, vertical=True, color='rojo'):
    caja = pygame.Rect(x, y, 20, 50) if vertical else pygame.Rect(x, y, 50, 20)
    pygame.draw.rect(screen, (40, 40, 40), caja, border_radius=4)
    r = 6

    colR = ROJO if color == 'rojo' else (120, 60, 60)
    colY = AMARILLO if color == 'amarillo' else (120, 110, 60)
    colG = VERDE if color == 'verde' else (60, 100, 60)
    if vertical:
        pygame.draw.circle(screen, colR, (caja.centerx, caja.top + 10), r)
        pygame.draw.circle(screen, colY, (caja.centerx, caja.centery), r)
        pygame.draw.circle(screen, colG, (caja.centerx, caja.bottom - 10), r)
    else:
        pygame.draw.circle(screen, colR, (caja.left + 10, caja.centery), r)
        pygame.draw.circle(screen, colY, (caja.centerx, caja.centery), r)
        pygame.draw.circle(screen, colG, (caja.right - 10, caja.centery), r)

def draw_car(x, y, dir_, color):

    L, W = 44, 22  # largo y ancho del auto
    if dir_ in ('N', 'S'):  # vertical
        rect = pygame.Rect(x - W//2, y - L//2, W, L)
    else:                   # horizontal
        rect = pygame.Rect(x - L//2, y - W//2, L, W)
    pygame.draw.rect(screen, color, rect, border_radius=4)

def draw_scene():
    screen.fill(VERDE_OSCURO)
    pygame.draw.rect(screen, GRIS, rect_v)
    pygame.draw.rect(screen, GRIS, rect_h)
    draw_center_dashes()
    draw_zebra_top_bottom()
    draw_zebra_left_right()
    draw_stop_lines()

    draw_light(cx - MITAD - 28, cy - MITAD - 64, True,  'rojo')     # norte
    draw_light(cx + MITAD + 8,   cy + MITAD + 8,   True,  'verde')   # sur
    draw_light(cx - MITAD - 60,  cy + MITAD + 8,   False, 'rojo')    # oeste
    draw_light(cx + MITAD + 8,   cy - MITAD - 32,  False, 'verde')   # este

    y_WE = cy - LANE_OFF
    draw_car(STOP_W - 26, y_WE, 'E', CAR2)
    draw_car(STOP_W - 90, y_WE, 'E', CAR5)

    y_EW = cy + LANE_OFF
    draw_car(STOP_E + 26, y_EW, 'W', CAR1)
    draw_car(STOP_E + 95, y_EW, 'W', CAR3)

    x_NS = cx - LANE_OFF
    draw_car(x_NS, STOP_N - 26, 'S', CAR4)
    draw_car(x_NS, STOP_N - 95, 'S', CAR2)

    x_SN = cx + LANE_OFF
    draw_car(x_SN, STOP_S + 26, 'N', CAR5)

clock = pygame.time.Clock()
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
    draw_scene()
    pygame.display.flip()
    clock.tick(60)
