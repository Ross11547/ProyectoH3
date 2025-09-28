import sys
import pygame
import time
import random

pygame.init()
#dimenciones de el exe
ancho, alto = 1100, 700
ventana = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Simulación de tráfico – Semana 1")

verde_oscuro = (0, 100, 0)
gris = (160, 160, 160)
blanco = (255, 255, 255)
rojo = (220, 70, 70)
amarillo = (245, 205, 70)
verde = (70, 200, 110)

# Colores extra
asfalto = (50, 50, 50)
texto_blanco = (255, 255, 255)
texto_amarillo = (255, 220, 80)
panel_bg = (0, 0, 0, 150)  # fondo semitransparente para métricas


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

rutas = {
    "Norte": ["Sur", "Oeste", "Este"],
    "Sur": ["Norte", "Este", "Oeste"],
    "Este": ["Oeste", "Norte", "Sur"],
    "Oeste": ["Este", "Sur", "Norte"]
}

# Imagen de Autos Ordenados de aca deben de sacar los
pygame.image.load('assets/imagen/CarUp.png')
pygame.image.load('assets/imagen/Carup2.png')
pygame.image.load('assets/imagen/carLef1.png')
pygame.image.load('assets/imagen/CarLeft.png')
pygame.image.load('assets/imagen/carDo1.png')
pygame.image.load('assets/imagen/carDo2.png')
pygame.image.load('assets/imagen/carrigth1.png')
pygame.image.load('assets/imagen/CarRigth.png')

# Cargar y escalar imágenes de autos
# Autos hacia arriba
cars_up = [
    pygame.transform.scale(pygame.image.load('assets/imagen/CarUp.png'), (40, 70)),
    pygame.transform.scale(pygame.image.load('assets/imagen/Carup2.png'), (40, 70))
]

# Autos hacia abajo
cars_down = [
    pygame.transform.scale(pygame.image.load('assets/imagen/carDo1.png'), (40, 70)),
    pygame.transform.scale(pygame.image.load('assets/imagen/carDo2.png'), (40, 70))
]

# Autos hacia la izquierda
cars_left = [
    pygame.transform.scale(pygame.image.load('assets/imagen/CarLeft.png'), (70, 40)),
    pygame.transform.scale(pygame.image.load('assets/imagen/carLef1.png'), (70, 40))
]

# Autos hacia la derecha
cars_right = [
    pygame.transform.scale(pygame.image.load('assets/imagen/CarRigth.png'), (70, 40)),
    pygame.transform.scale(pygame.image.load('assets/imagen/carrigth1.png'), (70, 40))
]


def generar_auto(id_auto, entrada):
    salida = random.choice(rutas[entrada])
    velocidad = random.randint(30, 60)

    if entrada == "Norte":
        imagen = random.choice(cars_down)   # bajan hacia el sur
    elif entrada == "Sur":
        imagen = random.choice(cars_up)     # suben hacia el norte
    elif entrada == "Oeste":
        imagen = random.choice(cars_right)  # van a la derecha
    else:  # Este
        imagen = random.choice(cars_left)   # van a la izquierda

    return {
        "id": id_auto,
        "entrada": entrada,
        "salida": salida,
        "velocidad": velocidad,
        "imagen": imagen
    }


def generar_carriles():
    carriles = {}
    id_auto = 1
    for entrada in rutas.keys():
        num_autos = random.randint(2, 5)  # menos autos, pero más realista
        autos = [generar_auto(id_auto + i, entrada) for i in range(num_autos)]
        carriles[entrada] = autos
        id_auto += num_autos
    return carriles


carriles = generar_carriles()

def contar_orientaciones(carriles):
    vertical = len(carriles["Norte"]) + len(carriles["Sur"])
    horizontal = len(carriles["Este"]) + len(carriles["Oeste"])
    return vertical, horizontal

vertical_count, horizontal_count = contar_orientaciones(carriles)

if vertical_count >= horizontal_count:
    semaforos = {"vertical": "verde", "horizontal": "rojo"}
    duracion_actual = max(vertical_count * 3, 3)
else:
    semaforos = {"vertical": "rojo", "horizontal": "verde"}
    duracion_actual = max(horizontal_count * 3, 3)

tiempo_cambio = time.time()

def actualizar_semaforos(carriles):
    global tiempo_cambio, duracion_actual, semaforos
    if time.time() - tiempo_cambio >= duracion_actual:
        v_count, h_count = contar_orientaciones(carriles)
        if semaforos["vertical"] == "verde":
            semaforos["vertical"] = "rojo"
            semaforos["horizontal"] = "verde"
            duracion_actual = max(h_count * 3, 3)
            orientation = "horizontal"
        else:
            semaforos["vertical"] = "verde"
            semaforos["horizontal"] = "rojo"
            duracion_actual = max(v_count * 3, 3)
            orientation = "vertical"
        tiempo_cambio = time.time()
        print(f"Cambio -> verde: {orientation} | duracion: {duracion_actual}s | v={v_count} h={h_count}")

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
            pygame.draw.rect(ventana, blanco, (zona.left + margen, y, zona.width - 2 * margen, grosor), border_radius=1)
            y += grosor + espacio
    else:
        x = zona.left + margen
        while x + grosor <= zona.right - margen:
            pygame.draw.rect(ventana, blanco, (x, zona.top + margen, grosor, zona.height - 2 * margen), border_radius=1)
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




def dibujar_autos(carriles):
    separacion = 120  # más espacio entre autos
    for entrada, autos in carriles.items():
        for i, auto in enumerate(autos):
            img = auto["imagen"]
            rect = img.get_rect()

            if entrada == "Oeste":
                x = pare_oeste - separacion * (i + 1)
                y = centro_y - desfase_carril if i % 2 == 0 else centro_y + desfase_carril
                rect.center = (x, y)
            elif entrada == "Este":
                x = pare_este + separacion * (i + 1)
                y = centro_y + desfase_carril if i % 2 == 0 else centro_y - desfase_carril
                rect.center = (x, y)
            elif entrada == "Norte":
                x = centro_x - desfase_carril if i % 2 == 0 else centro_x + desfase_carril
                y = pare_norte - separacion * (i + 1)
                rect.center = (x, y)
            elif entrada == "Sur":
                x = centro_x + desfase_carril if i % 2 == 0 else centro_x - desfase_carril
                y = pare_sur + separacion * (i + 1)
                rect.center = (x, y)

            ventana.blit(img, rect)



def dibujar_conteo_autos(carriles):
    font = pygame.font.SysFont(None, 28)
    y = 10
    for entrada, autos in carriles.items():
        texto = f"{entrada}: {len(autos)} autos"
        img = font.render(texto, True, blanco)
        ventana.blit(img, (10, y))
        y += 26
    restante = max(0, int(duracion_actual - (time.time() - tiempo_cambio)))
    info = f"Quedan: {restante}s"
    ventana.blit(font.render(info, True, blanco), (10, y))

def dibujar_metricas(carriles):
    font_titulo = pygame.font.SysFont("Arial", 28, bold=True)
    font_texto = pygame.font.SysFont("Arial", 22)

    # Panel negro semitransparente
    panel = pygame.Surface((280, 220), pygame.SRCALPHA)
    panel.fill(panel_bg)

    # Datos
    vertical_count, horizontal_count = contar_orientaciones(carriles)
    total_autos = sum(len(autos) for autos in carriles.values())
    restante = max(0, int(duracion_actual - (time.time() - tiempo_cambio)))
    luz_vertical = semaforos["vertical"]
    luz_horizontal = semaforos["horizontal"]

    # Escribir datos
    y = 10
    panel.blit(font_titulo.render("📊 Métricas", True, texto_amarillo), (10, y))
    y += 35
    panel.blit(font_texto.render(f"Total autos: {total_autos}", True, texto_blanco), (10, y))
    y += 28
    panel.blit(font_texto.render(f"Vertical: {vertical_count}", True, texto_blanco), (10, y))
    y += 28
    panel.blit(font_texto.render(f"Horizontal: {horizontal_count}", True, texto_blanco), (10, y))
    y += 28
    panel.blit(font_texto.render(f"Semáforo V: {luz_vertical}", True, texto_blanco), (10, y))
    y += 28
    panel.blit(font_texto.render(f"Semáforo H: {luz_horizontal}", True, texto_blanco), (10, y))
    y += 28
    panel.blit(font_texto.render(f"⏱ Quedan: {restante}s", True, texto_amarillo), (10, y))

    # Dibujar en pantalla (arriba derecha)
    ventana.blit(panel, (ancho - 290, 10))

def dibujar_escena(carriles):
    ventana.fill(asfalto)  # mejor color de fondo
    pygame.draw.rect(ventana, gris, recta_vertical)
    pygame.draw.rect(ventana, gris, recta_horizontal)
    dibujar_lineas_centrales()
    dibujar_cebras()
    dibujar_lineas_pare()
    dibujar_semaforo(centro_x - mitad_via - 28, centro_y - mitad_via - 64, True, semaforos["vertical"])
    dibujar_semaforo(centro_x + mitad_via + 8,  centro_y + mitad_via + 8,  True, semaforos["vertical"])
    dibujar_semaforo(centro_x - mitad_via - 60, centro_y + mitad_via + 8,  False, semaforos["horizontal"])
    dibujar_semaforo(centro_x + mitad_via + 8,  centro_y - mitad_via - 32, False, semaforos["horizontal"])
    dibujar_autos(carriles)
    dibujar_metricas(carriles)  # 👈 agregado


reloj = pygame.time.Clock()
print(f"Inicial -> verde: {'vertical' if semaforos['vertical']=='verde' else 'horizontal'} | duracion: {duracion_actual}s")
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    actualizar_semaforos(carriles)
    dibujar_escena(carriles)
    pygame.display.flip()
    reloj.tick(30)
