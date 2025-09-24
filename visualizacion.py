import sys
import pygame

pygame.init()

ANCHO, ALTO = 1100, 700
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulación de tráfico – Semana 1")

VERDE_OSCURO = (0, 100, 0)
GRIS = (160, 160, 160)
BLANCO = (255, 255, 255)
ROJO = (220, 70, 70)
AMARILLO = (245, 205, 70)
VERDE = (70, 200, 110)

AUTO_1 = (240, 80, 60)
AUTO_2 = (80, 160, 240)
AUTO_3 = (80, 200, 130)
AUTO_4 = (190, 90, 220)
AUTO_5 = (200, 200, 200)

centro_x, centro_y = ANCHO // 2, ALTO // 2
ancho_via = 200
mitad_via = ancho_via // 2
ancho_cebra = 48
desfase_carril = 50

recta_vertical = pygame.Rect(centro_x - mitad_via, 0, ancho_via, ALTO)
recta_horizontal = pygame.Rect(0, centro_y - mitad_via, ANCHO, ancho_via)

pare_oeste = centro_x - mitad_via - ancho_cebra - 6
pare_este = centro_x + mitad_via + ancho_cebra + 6
pare_norte = centro_y - mitad_via - ancho_cebra - 6
pare_sur = centro_y + mitad_via + ancho_cebra + 6

def dibujar_lineas_centrales():

    for y in range(0, centro_y - mitad_via - 10, 28):
        pygame.draw.line(VENTANA, BLANCO, (centro_x, y), (centro_x, y + 16), 3)
    for y in range(centro_y + mitad_via + 10, ALTO, 28):
        pygame.draw.line(VENTANA, BLANCO, (centro_x, y), (centro_x, y + 16), 3)
    for x in range(0, centro_x - mitad_via - 10, 28):
        pygame.draw.line(VENTANA, BLANCO, (x, centro_y), (x + 16, centro_y), 3)
    for x in range(centro_x + mitad_via + 10, ANCHO, 28):
        pygame.draw.line(VENTANA, BLANCO, (x, centro_y), (x + 16, centro_y), 3)


def dibujar_cebra(zona: pygame.Rect, orientacion: str):
    margen = 4
    grosor = 10
    espacio = 8

    if orientacion == "horizontal":
        y = zona.top + margen
        while y + grosor <= zona.bottom - margen:
            pygame.draw.rect(
                VENTANA, BLANCO,
                (zona.left + margen, y, zona.width - 2 * margen, grosor),
                border_radius=2
            )
            y += grosor + espacio
    else:
        x = zona.left + margen
        while x + grosor <= zona.right - margen:
            pygame.draw.rect(
                VENTANA, BLANCO,
                (x, zona.top + margen, grosor, zona.height - 2 * margen),
                border_radius=2
            )
            x += grosor + espacio


def dibujar_cebras():
    zona_arriba = pygame.Rect(centro_x - mitad_via, centro_y - mitad_via - ancho_cebra, ancho_via, ancho_cebra)
    zona_abajo = pygame.Rect(centro_x - mitad_via, centro_y + mitad_via, ancho_via, ancho_cebra)
    dibujar_cebra(zona_arriba, "vertical")
    dibujar_cebra(zona_abajo, "vertical")
    zona_izquierda = pygame.Rect(centro_x - mitad_via - ancho_cebra, centro_y - mitad_via, ancho_cebra, ancho_via)
    zona_derecha = pygame.Rect(centro_x + mitad_via, centro_y - mitad_via, ancho_cebra, ancho_via)
    dibujar_cebra(zona_izquierda, "horizontal")
    dibujar_cebra(zona_derecha, "horizontal")


def dibujar_lineas_pare():
    pygame.draw.line(VENTANA, BLANCO, (pare_oeste, centro_y - mitad_via), (pare_oeste, centro_y + mitad_via), 6)
    pygame.draw.line(VENTANA, BLANCO, (pare_este, centro_y - mitad_via), (pare_este, centro_y + mitad_via), 6)
    pygame.draw.line(VENTANA, BLANCO, (centro_x - mitad_via, pare_norte), (centro_x + mitad_via, pare_norte), 6)
    pygame.draw.line(VENTANA, BLANCO, (centro_x - mitad_via, pare_sur), (centro_x + mitad_via, pare_sur), 6)


def dibujar_semaforo(x, y, vertical=True, color_activo="rojo"):
    caja = pygame.Rect(x, y, 20, 50) if vertical else pygame.Rect(x, y, 50, 20)
    pygame.draw.rect(VENTANA, (40, 40, 40), caja, border_radius=4)
    radio = 6

    color_r = ROJO if color_activo == "rojo" else (120, 60, 60)
    color_a = AMARILLO if color_activo == "amarillo" else (120, 110, 60)
    color_v = VERDE if color_activo == "verde" else (60, 100, 60)

    if vertical:
        pygame.draw.circle(VENTANA, color_r, (caja.centerx, caja.top + 10), radio)
        pygame.draw.circle(VENTANA, color_a, (caja.centerx, caja.centery), radio)
        pygame.draw.circle(VENTANA, color_v, (caja.centerx, caja.bottom - 10), radio)
    else:
        pygame.draw.circle(VENTANA, color_r, (caja.left + 10, caja.centery), radio)
        pygame.draw.circle(VENTANA, color_a, (caja.centerx, caja.centery), radio)
        pygame.draw.circle(VENTANA, color_v, (caja.right - 10, caja.centery), radio)


def dibujar_auto(x, y, direccion, color):
    largo, ancho = 55, 40
    if direccion in ("N", "S"):
        rect = pygame.Rect(x - ancho // 2, y - largo // 2, ancho, largo)
    else:
        rect = pygame.Rect(x - largo // 2, y - ancho // 2, largo, ancho)
    pygame.draw.rect(VENTANA, color, rect, border_radius=4)


def dibujar_escena():
    VENTANA.fill(VERDE_OSCURO)
    pygame.draw.rect(VENTANA, GRIS, recta_vertical)
    pygame.draw.rect(VENTANA, GRIS, recta_horizontal)

    dibujar_lineas_centrales()
    dibujar_cebras()
    dibujar_lineas_pare()


    dibujar_semaforo(centro_x - mitad_via - 28, centro_y - mitad_via - 64, True,  "rojo")
    dibujar_semaforo(centro_x + mitad_via + 8,   centro_y + mitad_via + 8,   True,  "verde")
    dibujar_semaforo(centro_x - mitad_via - 60,  centro_y + mitad_via + 8,   False, "rojo")
    dibujar_semaforo(centro_x + mitad_via + 8,   centro_y - mitad_via - 32,  False, "verde")


    y_oeste_a_este = centro_y - desfase_carril
    y_este_a_oeste = centro_y + desfase_carril
    x_norte_a_sur = centro_x - desfase_carril
    x_sur_a_norte = centro_x + desfase_carril


    dibujar_auto(pare_oeste - 40, y_oeste_a_este, "E", AUTO_2)
    dibujar_auto(pare_oeste - 120, y_oeste_a_este, "E", AUTO_5)

    dibujar_auto(pare_este + 40, y_este_a_oeste, "O", AUTO_1)
    dibujar_auto(pare_este + 120, y_este_a_oeste, "O", AUTO_3)

    dibujar_auto(x_norte_a_sur, pare_norte - 40, "S", AUTO_4)
    dibujar_auto(x_norte_a_sur, pare_norte - 120, "S", AUTO_2)

    dibujar_auto(x_sur_a_norte, pare_sur + 40, "N", AUTO_5)
    dibujar_auto(x_sur_a_norte, pare_sur + 120, "N", AUTO_1)

reloj = pygame.time.Clock()
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    dibujar_escena()
    pygame.display.flip()
    reloj.tick(60)
