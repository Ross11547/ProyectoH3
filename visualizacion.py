import pygame, sys, random
pygame.init()

ANCHO, ALTO = 800, 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulación de tráfico – Semana 1")

NEGRO = (0, 0, 0)
GRIS = (150, 150, 150)
BLANCO = (255, 255, 255)
VERDE_OSCURO = (0, 100, 0)
ROJO = (220, 60, 60)
AMARILLO = (240, 200, 60)
VERDE = (60, 200, 90)
AZUL_TXT = (40, 120, 200)

reloj = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)

cx, cy = ANCHO // 2, ALTO // 2
ANCHO_VIA = 200
MITAD = ANCHO_VIA // 2
INTER = ANCHO_VIA
CEBRA = 50

rect_v = pygame.Rect(cx - MITAD, 0, ANCHO_VIA, ALTO)
rect_h = pygame.Rect(0, cy - MITAD, ANCHO, ANCHO_VIA)


MARGEN_STOP = 10
stop_S = cy + MITAD + CEBRA + MARGEN_STOP
stop_N = cy - MITAD - CEBRA - MARGEN_STOP
stop_E = cx - MITAD - CEBRA - MARGEN_STOP
stop_W = cx + MITAD + CEBRA + MARGEN_STOP

lane_Nx = cx - ANCHO_VIA // 4
lane_Sx = cx + ANCHO_VIA // 4
lane_Ey = cy - ANCHO_VIA // 4
lane_Wy = cy + ANCHO_VIA // 4

CAR_L = 40
CAR_W = 20
VEL = 2.2
GAP = 6
SPAWN_RATE = {
    'N': 0.45,
    'S': 0.55,
    'E': 0.60,
    'W': 0.50,
}
COLORES_AUTOS = [(240,80,60),(250,160,60),(240,220,60),(80,200,120),(80,160,240),(190,90,220),(180,180,180)]

class Auto:
    def __init__(self, d):
        self.d = d
        c = random.choice(COLORES_AUTOS)
        if d == 'N':
            self.rect = pygame.Rect(lane_Nx - CAR_W//2, -CAR_L, CAR_W, CAR_L)
            self.vx, self.vy = 0, VEL
        elif d == 'S':
            self.rect = pygame.Rect(lane_Sx - CAR_W//2, ALTO, CAR_W, CAR_L)
            self.vx, self.vy = 0, -VEL
        elif d == 'E':
            self.rect = pygame.Rect(-CAR_L, lane_Ey - CAR_W//2, CAR_L, CAR_W)
            self.vx, self.vy = VEL, 0
        else:
            self.rect = pygame.Rect(ANCHO, lane_Wy - CAR_W//2, CAR_L, CAR_W)
            self.vx, self.vy = -VEL, 0
        self.color = c

    def frente(self):

        if self.d == 'N':   return self.rect.bottom
        if self.d == 'S':   return self.rect.top
        if self.d == 'E':   return self.rect.right
        return self.rect.left  # 'W'

    def mover(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

    def fuera(self):
        return (self.rect.bottom < 0 or self.rect.top > ALTO or
                self.rect.right < 0 or self.rect.left > ANCHO)

FASE_NS_G, FASE_NS_Y, FASE_EW_G, FASE_EW_Y = range(4)

class ControlSemaforo:
    def __init__(self):
        self.fase = FASE_NS_G
        self.timer = 0.0
        self.verde_actual = 6.0

    def autos_en_cola(self, lista_autos, d, ventana_cola=220):
        cnt = 0
        for a in lista_autos:
            if a.d != d:
                continue
            if d == 'N' and 0 <= (stop_N - a.rect.bottom) <= ventana_cola: cnt += 1
            if d == 'S' and 0 <= (a.rect.top - stop_S)     <= ventana_cola: cnt += 1
            if d == 'E' and 0 <= (stop_E - a.rect.right)   <= ventana_cola: cnt += 1
            if d == 'W' and 0 <= (a.rect.left - stop_W)    <= ventana_cola: cnt += 1
        return cnt

    def recomputar_verde(self, autos):
        base = 4.0
        k = 0.7
        if self.fase in (FASE_NS_G, FASE_NS_Y):
            n = self.autos_en_cola(autos, 'N') + self.autos_en_cola(autos, 'S')
        else:
            n = self.autos_en_cola(autos, 'E') + self.autos_en_cola(autos, 'W')
        self.verde_actual = max(4.0, min(14.0, base + k * n))  # límites
        self.timer = self.verde_actual

    def actualizar(self, dt, autos):
        self.timer -= dt
        if self.timer > 0:
            return
        if self.fase == FASE_NS_G:
            self.fase, self.timer = FASE_NS_Y, 1.2
        elif self.fase == FASE_NS_Y:
            self.fase = FASE_EW_G
            self.recomputar_verde(autos)
        elif self.fase == FASE_EW_G:
            self.fase, self.timer = FASE_EW_Y, 1.2
        else:  # FASE_EW_Y
            self.fase = FASE_NS_G
            self.recomputar_verde(autos)

    def estado_dir(self, d):
        if d in ('N','S'):
            if self.fase == FASE_NS_G: return 'verde'
            if self.fase == FASE_NS_Y: return 'amarillo'
            return 'rojo'
        else:
            if self.fase == FASE_EW_G: return 'verde'
            if self.fase == FASE_EW_Y: return 'amarillo'
            return 'rojo'

control = ControlSemaforo()
autos = []

def spawnear(dt):
    for d in ('N','S','E','W'):
        if random.random() < SPAWN_RATE[d] * dt:
            autos.append(Auto(d))

def ordenar_por_cola(d):
    if d == 'N': key = lambda a: (stop_N - a.rect.bottom)
    elif d == 'S': key = lambda a: (a.rect.top - stop_S)
    elif d == 'E': key = lambda a: (stop_E - a.rect.right)
    else: key = lambda a: (a.rect.left - stop_W)
    return sorted([a for a in autos if a.d == d], key=key)

def mover_autos(dt):
    for d in ('N','S','E','W'):
        lista = ordenar_por_cola(d)
        estado = control.estado_dir(d)
        for i, a in enumerate(lista):
            puede = True
            if d == 'N':
                if estado == 'rojo' and a.rect.bottom + a.vy > stop_N: puede = False
                if estado == 'amarillo' and a.rect.bottom + a.vy > stop_N: puede = False
                if i > 0:
                    delante = lista[i-1]
                    if a.rect.bottom + a.vy > delante.rect.top - GAP:
                        puede = False
                if puede: a.mover()
            elif d == 'S':
                if estado == 'rojo' and a.rect.top + a.vy < stop_S: puede = False
                if estado == 'amarillo' and a.rect.top + a.vy < stop_S: puede = False
                if i > 0:
                    delante = lista[i-1]
                    if a.rect.top + a.vy < delante.rect.bottom + GAP:
                        puede = False
                if puede: a.mover()
            elif d == 'E':
                if estado == 'rojo' and a.rect.right + a.vx > stop_E: puede = False
                if estado == 'amarillo' and a.rect.right + a.vx > stop_E: puede = False
                if i > 0:
                    delante = lista[i-1]
                    if a.rect.right + a.vx > delante.rect.left - GAP:
                        puede = False
                if puede: a.mover()
            else:
                if estado == 'rojo' and a.rect.left + a.vx < stop_W: puede = False
                if estado == 'amarillo' and a.rect.left + a.vx < stop_W: puede = False
                if i > 0:
                    delante = lista[i-1]
                    if a.rect.left + a.vx < delante.rect.right + GAP:
                        puede = False
                if puede: a.mover()

    for a in autos[:]:
        if a.fuera():
            autos.remove(a)

def dibujar_carreteras():
    ventana.fill(VERDE_OSCURO)
    pygame.draw.rect(ventana, GRIS, rect_v)  # vertical
    pygame.draw.rect(ventana, GRIS, rect_h)  # horizontal

    for y in range(0, ALTO, 40):
        pygame.draw.line(ventana, BLANCO, (cx, y), (cx, y + 20), 3)
    for x in range(0, ANCHO, 40):
        pygame.draw.line(ventana, BLANCO, (x, cy), (x + 20, cy), 3)

    for i in range(5):
        pygame.draw.rect(ventana, BLANCO, (cx - MITAD, cy - MITAD - CEBRA + i*10, ANCHO_VIA, 5))

    for i in range(5):
        pygame.draw.rect(ventana, BLANCO, (cx - MITAD, cy + MITAD + i*10, ANCHO_VIA, 5))

    for i in range(5):
        pygame.draw.rect(ventana, BLANCO, (cx - MITAD - CEBRA + i*10, cy - MITAD, 5, ANCHO_VIA))

    for i in range(5):
        pygame.draw.rect(ventana, BLANCO, (cx + MITAD + i*10, cy - MITAD, 5, ANCHO_VIA))

def dibujar_luces():

    def draw_head(x, y, vertical=True, estado='rojo'):
        caja = pygame.Rect(x, y, 20, 50) if vertical else pygame.Rect(x, y, 50, 20)
        pygame.draw.rect(ventana, (40,40,40), caja, border_radius=4)
        if vertical:
            r = 6
            cx0, cy0 = caja.centerx, caja.top + 10
            cx1, cy1 = caja.centerx, caja.centery
            cx2, cy2 = caja.centerx, caja.bottom - 10
            colR = ROJO if estado=='rojo' else (120,50,50)
            colY = AMARILLO if estado=='amarillo' else (110,100,40)
            colG = VERDE if estado=='verde' else (40,90,40)
            pygame.draw.circle(ventana, colR, (cx0, cy0), r)
            pygame.draw.circle(ventana, colY, (cx1, cy1), r)
            pygame.draw.circle(ventana, colG, (cx2, cy2), r)
        else:
            r = 6
            cx0, cy0 = caja.left + 10, caja.centery
            cx1, cy1 = caja.centerx,  caja.centery
            cx2, cy2 = caja.right - 10, caja.centery
            colR = ROJO if estado=='rojo' else (120,50,50)
            colY = AMARILLO if estado=='amarillo' else (110,100,40)
            colG = VERDE if estado=='verde' else (40,90,40)
            pygame.draw.circle(ventana, colR, (cx0, cy0), r)
            pygame.draw.circle(ventana, colY, (cx1, cy1), r)
            pygame.draw.circle(ventana, colG, (cx2, cy2), r)

    draw_head(cx - MITAD - 30, cy - MITAD - 60, True,  control.estado_dir('S'))
    draw_head(cx + MITAD + 10,  cy + MITAD + 10, True,  control.estado_dir('N'))
    draw_head(cx - MITAD - 60, cy + MITAD + 10, False, control.estado_dir('E'))
    draw_head(cx + MITAD + 10,  cy - MITAD - 30, False, control.estado_dir('W'))

def dibujar_autos():
    for a in autos:
        pygame.draw.rect(ventana, a.color, a.rect, border_radius=3)

def overlay_info():
    ns = control.autos_en_cola(autos, 'N') + control.autos_en_cola(autos, 'S')
    ew = control.autos_en_cola(autos, 'E') + control.autos_en_cola(autos, 'W')

control.recomputar_verde(autos)

while True:
    dt = reloj.tick(110) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    spawnear(dt)
    control.actualizar(dt, autos)
    mover_autos(dt)

    dibujar_carreteras()
    dibujar_luces()
    dibujar_autos()
    overlay_info()

    pygame.display.flip()
