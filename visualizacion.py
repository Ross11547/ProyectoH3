import sys
import pygame

pygame.init()

ancho, alto = 1100, 700
ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Simulación de tráfico – Semana 1")

verde_oscuro = (0, 100, 0)
gris = (160, 160, 160)
blanco = (255, 255, 255)
rojo = (220, 70, 70)
amarillo = (245, 205, 70)
verde = (70, 200, 110)

color_auto1 = (240, 80, 60)
color_auto2 = (80, 160, 240)
color_auto3 = (80, 200, 130)
color_auto4 = (190, 90, 220)
color_auto5 = (200, 200, 200)

centro_x, centro_y = ancho // 2, alto // 2
ancho_via = 200
mitad_via = ancho_via // 2
ancho_cebra = 48
desfase_carril = 50

recta_vertical = pygame.Rect(centro_x - mitad_via, 0, ancho_via, alto)
recta_horizontal = pygame.Rect(0, centro_y - mitad_via, ancho, ancho_via)

pare_oeste = centro_x - mitad_via - ancho_cebra - 6
pare_este = centro_x + mitad_via + ancho_cebra + 6
pare_norte = centro_y - mitad_via - ancho_cebra - 6
pare_sur = centro_y + mitad_via + ancho_cebra + 6


def dibujar_lineas_centrales():
    longitud_linea = 20
    espacios = 20
    grosor = 5

    for y in range(0, centro_y - mitad_via - 50, longitud_linea + espacios):
        pygame.draw.line(ventana, blanco, (centro_x, y), (centro_x, y + longitud_linea), grosor)

    for y in range(centro_y + mitad_via + 70, alto, longitud_linea + espacios):
        pygame.draw.line(ventana, blanco, (centro_x, y), (centro_x, y + longitud_linea), grosor)

    for x in range(0, centro_x - mitad_via - 50, longitud_linea + espacios):
        pygame.draw.line(ventana, blanco, (x, centro_y), (x + longitud_linea, centro_y), grosor)

    for x in range(centro_x + mitad_via + 70, ancho, longitud_linea + espacios):
        pygame.draw.line(ventana, blanco, (x, centro_y), (x + longitud_linea, centro_y), grosor)


def dibujar_cebra(zona: pygame.Rect, orientacion: str):
    margen = 4
    grosor = 12
    espacio = 10

    if orientacion == "horizontal":
        y = zona.top + margen
        while y + grosor <= zona.bottom - margen:
            pygame.draw.rect(
                ventana, blanco,
                (zona.left + margen, y, zona.width - 2 * margen, grosor),
                border_radius=1
            )
            y += grosor + espacio
    else:
        x = zona.left + margen
        while x + grosor <= zona.right - margen:
            pygame.draw.rect(
                ventana, blanco,
                (x, zona.top + margen, grosor, zona.height - 2 * margen),
                border_radius=1
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
    pygame.draw.line(ventana, blanco, (pare_oeste, centro_y - mitad_via), (pare_oeste, centro_y + mitad_via), 7)
    pygame.draw.line(ventana, blanco, (pare_este, centro_y - mitad_via), (pare_este, centro_y + mitad_via), 7)
    pygame.draw.line(ventana, blanco, (centro_x - mitad_via, pare_norte), (centro_x + mitad_via, pare_norte), 7)
    pygame.draw.line(ventana, blanco, (centro_x - mitad_via, pare_sur), (centro_x + mitad_via, pare_sur), 7)


def dibujar_semaforo(x, y, vertical=True, color_activo="rojo"):
    caja = pygame.Rect(x, y, 20, 50) if vertical else pygame.Rect(x, y, 50, 20)
    pygame.draw.rect(ventana, (0, 0, 0), caja, border_radius=2)
    radio = 6

    color_r = rojo if color_activo == "rojo" else (120, 60, 60)
    color_a = amarillo if color_activo == "amarillo" else (120, 110, 60)
    color_v = verde if color_activo == "verde" else (60, 100, 60)

    if vertical:
        pygame.draw.circle(ventana, color_r, (caja.centerx, caja.top + 10), radio)
        pygame.draw.circle(ventana, color_a, (caja.centerx, caja.centery), radio)
        pygame.draw.circle(ventana, color_v, (caja.centerx, caja.bottom - 10), radio)
    else:
        pygame.draw.circle(ventana, color_r, (caja.left + 10, caja.centery), radio)
        pygame.draw.circle(ventana, color_a, (caja.centerx, caja.centery), radio)
        pygame.draw.circle(ventana, color_v, (caja.right - 10, caja.centery), radio)


def dibujar_auto(x, y, direccion, color):
    largo_auto, ancho_auto = 65, 40
    if direccion in ("N", "S"):
        rect = pygame.Rect(x - ancho_auto // 2, y - largo_auto // 2, ancho_auto, largo_auto)
    else:
        rect = pygame.Rect(x - largo_auto // 2, y - ancho_auto // 2, largo_auto, ancho_auto)
    pygame.draw.rect(ventana, color, rect, border_radius=2)


def dibujar_escena():
    ventana.fill(verde_oscuro)
    pygame.draw.rect(ventana, gris, recta_vertical)
    pygame.draw.rect(ventana, gris, recta_horizontal)

    dibujar_lineas_centrales()
    dibujar_cebras()
    dibujar_lineas_pare()

    dibujar_semaforo(centro_x - mitad_via - 28, centro_y - mitad_via - 64, True, "rojo")
    dibujar_semaforo(centro_x + mitad_via + 8,  centro_y + mitad_via + 8,  True, "verde")
    dibujar_semaforo(centro_x - mitad_via - 60, centro_y + mitad_via + 8,  False, "rojo")
    dibujar_semaforo(centro_x + mitad_via + 8,  centro_y - mitad_via - 32, False, "verde")

    y_oeste_a_este = centro_y - desfase_carril
    y_este_a_oeste = centro_y + desfase_carril
    x_norte_a_sur = centro_x - desfase_carril
    x_sur_a_norte = centro_x + desfase_carril

    dibujar_auto(pare_oeste - 40,  y_oeste_a_este, "E", color_auto2)
    dibujar_auto(pare_oeste - 120, y_oeste_a_este, "E", color_auto5)
    dibujar_auto(pare_este + 40,  y_este_a_oeste, "O", color_auto1)
    dibujar_auto(pare_este + 120, y_este_a_oeste, "O", color_auto3)
    dibujar_auto(x_norte_a_sur, pare_norte - 40,  "S", color_auto4)
    dibujar_auto(x_norte_a_sur, pare_norte - 120, "S", color_auto2)
    dibujar_auto(x_sur_a_norte, pare_sur + 40,  "N", color_auto5)
    dibujar_auto(x_sur_a_norte, pare_sur + 120, "N", color_auto1)

reloj = pygame.time.Clock()
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    dibujar_escena()
    pygame.display.flip()
    reloj.tick()
