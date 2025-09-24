import pygame
import sys

#iniciar
pygame.init()
#dimenciones de la pantalla de game
ANCHO = 800
ALTO = 600
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("simulacion de trafico - semana 1")

#colores
NEGRO = (0, 0, 0)
GRIS = (169, 169, 169)
BLANCO = (255, 255, 255)
VERDE_OSCURO = (0, 100, 0)

#reloj FPS control
reloj = pygame.time.Clock()

#bucle principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    #fondo
    ventana.fill(VERDE_OSCURO)
    #DIBUJO DE CALLES
    pygame.draw.rect(ventana, GRIS, (150, 0, 200, ALTO))
    pygame.draw.rect(ventana, GRIS, (0, 250, ANCHO, 200))

    #-------------lineas de carreteras-------------------
    #vertical central
    for y in range(0, ALTO, 40):
        pygame.draw.line(ventana, BLANCO, (250, y), (250, y+20), 3)
    #Linea central horizontal
    for x in range(0, ANCHO, 40):
        pygame.draw.line(ventana, BLANCO, (x, 350), (x+20, 350), 3)

    # --------------grafico lineas de cebra---------------
    #cebra vertical superior
    for i in range(5):
        pygame.draw.rect(ventana, BLANCO, (150, 230 - i * 10, 200, 5))
    #cebra vertical inferior
    for i in range(5):
        pygame.draw.rect(ventana, BLANCO, (150, 450 + i * 10, 200, 5))

    # cebra horizontal izquierda
    for i in range(5):
        pygame.draw.rect(ventana, BLANCO, (150 - i * 10, 250, 5, 200))
    # cebra horizontal derecha
    for i in range(5):
        pygame.draw.rect(ventana, BLANCO, (350 + i * 10, 250, 5, 200))

    #Actualizar pantalla
    pygame.display.flip()
    reloj.tick(60)