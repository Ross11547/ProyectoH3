import os
import sys
import random
import time
from collections import deque

import pygame

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

pos_pygame_x = 60
pos_pygame_y = 60
os.environ["SDL_VIDEO_WINDOW_POS"] = f"{pos_pygame_x},{pos_pygame_y}"

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass

ancho_ventana = 1100
alto_ventana = 700
fps = 60

escala_px_por_metro = 8

def metros_a_pixeles(m):
    return int(m * escala_px_por_metro)

ancho_carril_m = 5
ancho_estacionar_m = 5
carriles_por_sentido = 2

largo_tramo_m = 3
espacio_tramo_m = 3

grosor_borde_px = 3
grosor_separador_px = 3
grosor_guia_px = 3

margen_linea_pare = 6
margen_pare_px = 55

tiempo_amarillo = 3

intervalo_aparicion_seg = 5
cola_maxima_por_carril = 10
distancia_min_autos_m = 1.7
velocidad_min_m_s = 8
velocidad_max_m_s = 15

ancho_auto_m = 3
largo_auto_m = 5

multiplo_creacion_lejos = 8
avance_inicial_seg_min = 0.8
avance_inicial_seg_max = 2

autos_iniciales_por_carril = 3

ancho_cebra_m = 6.5
margen_cebra_px = 4
grosor_barra_cebra = 10
espacio_barra_cebra = 10

verde_fondo = (0, 100, 0)
gris_via = (160, 160, 160)
gris_est = (140, 140, 140)
blanco = (255, 255, 255)
rojo_claro = (220, 70, 70)
rojo_oscuro = (120, 60, 60)
amarillo_claro = (245, 205, 70)
amarillo_oscuro = (120, 110, 60)
verde_claro = (70, 200, 110)
verde_oscuro = (60, 100, 60)

ancho_semaforo_px = 20
alto_semaforo_px = 50

ventana = pygame.display.set_mode((ancho_ventana, alto_ventana))
pygame.display.set_caption("Simulador vehicular — PID control (final)")
reloj = pygame.time.Clock()

last_beep_time = 0
beep_min_interval = 0.12

def cargar_textura(ruta, ancho=None, alto=None, color_relleno=(100, 100, 100)):
    try:
        img = pygame.image.load(ruta).convert()
        if ancho and alto:
            img = pygame.transform.smoothscale(img, (ancho, alto))
        return img
    except (pygame.error, FileNotFoundError):
        surf = pygame.Surface((ancho or 80, alto or 80))
        surf.fill(color_relleno)
        pygame.draw.rect(surf, (180, 180, 180), surf.get_rect(), 2)
        return surf

ruta_texturas = os.path.join("assets", "texturas")
textura_asfalto = cargar_textura(os.path.join(ruta_texturas, "asfalto.jpg"), 80, 80, (70, 70, 70))
textura_ladrillo = cargar_textura(os.path.join(ruta_texturas, "ladrillo.jpg"), 50, 50, (120, 60, 60))
textura_cesped = cargar_textura(os.path.join(ruta_texturas, "pasto.jpg"), 80, 80, (50, 120, 50))

ancho_carril_px = metros_a_pixeles(ancho_carril_m)
ancho_estacionar_px = metros_a_pixeles(ancho_estacionar_m)

largo_tramo_px = metros_a_pixeles(largo_tramo_m)
espacio_tramo_px = metros_a_pixeles(espacio_tramo_m)

ancho_auto_px = metros_a_pixeles(ancho_auto_m)
largo_auto_px = metros_a_pixeles(largo_auto_m)

distancia_min_autos_px = metros_a_pixeles(distancia_min_autos_m)
gap_necesario_px = distancia_min_autos_px + largo_auto_px

vel_min_px_s = int(velocidad_min_m_s * escala_px_por_metro)
vel_max_px_s = int(velocidad_max_m_s * escala_px_por_metro)

ancho_cebra_px = metros_a_pixeles(ancho_cebra_m)

cruce_x = ancho_ventana // 2
cruce_y = alto_ventana // 2

ancho_lado_px = ancho_estacionar_px + carriles_por_sentido * ancho_carril_px
ancho_via_px = 2 * ancho_lado_px
media_via_px = ancho_via_px // 2

rect_libertador_izq = pygame.Rect(0, cruce_y - media_via_px, cruce_x - media_via_px, ancho_via_px)
rect_libertador_der = pygame.Rect(cruce_x + media_via_px, cruce_y - media_via_px,
                                  ancho_ventana - (cruce_x + media_via_px), ancho_via_px)
rect_america_arr = pygame.Rect(cruce_x - media_via_px, 0, ancho_via_px, cruce_y - media_via_px)
rect_america_abj = pygame.Rect(cruce_x - media_via_px, cruce_y + media_via_px,
                               ancho_via_px, alto_ventana - (cruce_y + media_via_px))
rect_cruce = pygame.Rect(cruce_x - media_via_px, cruce_y - media_via_px, ancho_via_px, ancho_via_px)

ancho_vereda = 40
rect_vereda_arr = pygame.Rect(0, cruce_y - media_via_px - ancho_vereda, ancho_ventana, ancho_vereda)
rect_vereda_abj = pygame.Rect(0, cruce_y + media_via_px, ancho_ventana, ancho_vereda)
rect_vereda_izq = pygame.Rect(cruce_x - media_via_px - ancho_vereda, 0, ancho_vereda, alto_ventana)
rect_vereda_der = pygame.Rect(cruce_x + media_via_px, 0, ancho_vereda, alto_ventana)

linea_pare_oeste = cruce_x - media_via_px - margen_pare_px
linea_pare_este = cruce_x + media_via_px + margen_pare_px
linea_pare_norte = cruce_y - media_via_px - margen_pare_px
linea_pare_sur = cruce_y + media_via_px + margen_pare_px

salida_lib_este = cruce_x + media_via_px + 8
salida_lib_oeste = cruce_x - media_via_px - 8
salida_lib_sur = cruce_y + media_via_px + 8
salida_lib_norte = cruce_y - media_via_px - 8

inter_x_izq = cruce_x - media_via_px
inter_x_der = cruce_x + media_via_px
inter_y_sup = cruce_y - media_via_px
inter_y_inf = cruce_y + media_via_px

cebra_arriba = pygame.Rect(inter_x_izq, inter_y_sup - ancho_cebra_px, ancho_via_px, ancho_cebra_px)
cebra_abajo = pygame.Rect(inter_x_izq, inter_y_inf, ancho_via_px, ancho_cebra_px)
cebra_izquierda = pygame.Rect(inter_x_izq - ancho_cebra_px, inter_y_sup, ancho_cebra_px, ancho_via_px)
cebra_derecha = pygame.Rect(inter_x_der, inter_y_sup, ancho_cebra_px, ancho_via_px)

def construir_centros(inicio, paso, cantidad, sentido_positivo):
    lista = []
    for i in range(cantidad):
        if sentido_positivo:
            lista.append(inicio + int((i + 0.5) * paso))
        else:
            lista.append(inicio - int((i + 0.5) * paso))
    return lista

america_oe = construir_centros(cruce_y - media_via_px + ancho_estacionar_px, ancho_carril_px, carriles_por_sentido, True)
america_eo = construir_centros(cruce_y + media_via_px - ancho_estacionar_px, ancho_carril_px, carriles_por_sentido, False)
libertador_ns = construir_centros(cruce_x + media_via_px - ancho_estacionar_px, ancho_carril_px, carriles_por_sentido, False)
libertador_sn = construir_centros(cruce_x - media_via_px + ancho_estacionar_px, ancho_carril_px, carriles_por_sentido, True)

def construir_separadores(inicio, paso, cantidad, sentido_positivo):
    lineas = []
    for i in range(1, cantidad):
        lineas.append(inicio + i * paso if sentido_positivo else inicio - i * paso)
    return lineas

america_sep = construir_separadores(cruce_y - media_via_px + ancho_estacionar_px, ancho_carril_px, carriles_por_sentido, True) + \
              construir_separadores(cruce_y + media_via_px - ancho_estacionar_px, ancho_carril_px, carriles_por_sentido, False)

libertador_sep = construir_separadores(cruce_x - media_via_px + ancho_estacionar_px, ancho_carril_px, carriles_por_sentido, True) + \
                 construir_separadores(cruce_x + media_via_px - ancho_estacionar_px, ancho_carril_px, carriles_por_sentido, False)

def cargar_imagen_auto(ruta, ancho, alto):
    try:
        img = pygame.image.load(ruta).convert_alpha()
        return pygame.transform.smoothscale(img, (ancho, alto))
    except (pygame.error, FileNotFoundError):
        surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(surf, (60, 60, 60), surf.get_rect(), border_radius=6)
        pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2, border_radius=6)
        return surf

ruta_autos = os.path.join("assets", "imagen")
sprites_autos = {
    "n": [cargar_imagen_auto(os.path.join(ruta_autos, "auto1.png"), ancho_auto_px, largo_auto_px),
          cargar_imagen_auto(os.path.join(ruta_autos, "auto4.png"), ancho_auto_px, largo_auto_px)],
    "s": [cargar_imagen_auto(os.path.join(ruta_autos, "auto2.png"), ancho_auto_px, largo_auto_px),
          cargar_imagen_auto(os.path.join(ruta_autos, "auto5.png"), ancho_auto_px, largo_auto_px)],
    "o": [cargar_imagen_auto(os.path.join(ruta_autos, "auto3.png"), largo_auto_px, ancho_auto_px),
          cargar_imagen_auto(os.path.join(ruta_autos, "auto7.png"), largo_auto_px, ancho_auto_px)],
    "e": [cargar_imagen_auto(os.path.join(ruta_autos, "auto6.png"), largo_auto_px, ancho_auto_px),
          cargar_imagen_auto(os.path.join(ruta_autos, "auto8.png"), largo_auto_px, ancho_auto_px)],
}

min_verde = 5
max_verde = 50

PID_KP = 2.0    
PID_KI = 0.05   
PID_KD = 0.8   
PID_MAX_ADJ = 25.0  
TOTAL_CYCLE = 60.0  

EARLY_SWITCH_THRESHOLD = 3.0        
MIN_TIME_BETWEEN_SWITCHES = 3.0    

blink_threshold = 2.0               
fase = 0
tiempo_en_fase = 0.0
tiempo_verde_america_base = TOTAL_CYCLE / 2.0
tiempo_verde_libertador_base = TOTAL_CYCLE / 2.0

tiempo_verde_america = tiempo_verde_america_base
tiempo_verde_libertador = tiempo_verde_libertador_base

class PID:
    def __init__(self, kp, ki, kd, out_min=-PID_MAX_ADJ, out_max=PID_MAX_ADJ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev_error = 0.0
        self.out_min = out_min
        self.out_max = out_max

    def update(self, error, dt):
        if dt <= 0:
            return 0.0
        max_int = 1000.0
        self.integral += error * dt
        if self.integral > max_int: self.integral = max_int
        if self.integral < -max_int: self.integral = -max_int
        derivative = (error - self.prev_error) / dt
        out = self.kp * error + self.ki * self.integral + self.kd * derivative
        if out > self.out_max: out = self.out_max
        if out < self.out_min: out = self.out_min
        self.prev_error = error
        return out

pid_controller = PID(PID_KP, PID_KI, PID_KD, -PID_MAX_ADJ, PID_MAX_ADJ)
disparador_por_sentido = 10
disparador_total = 18
forzar_cambio_restante = 5

def contar_parados_por_carril():
    res = {"oeste":[0]*carriles_por_sentido,"este":[0]*carriles_por_sentido,"norte":[0]*carriles_por_sentido,"sur":[0]*carriles_por_sentido}
    for entrada in ("oeste","este","norte","sur"):
        for c in range(carriles_por_sentido):
            total = 0
            for a in colas[entrada][c]:
                if entrada == "oeste":
                    if a.punta_pos() < (cebra_izquierda.left - 4) and not a.entro_cruce:
                        total += 1
                elif entrada == "este":
                    if a.punta_pos() > (cebra_derecha.right + 4) and not a.entro_cruce:
                        total += 1
                elif entrada == "norte":
                    if a.punta_pos() < (cebra_arriba.top - 4) and not a.entro_cruce:
                        total += 1
                else:
                    if a.punta_pos() > (cebra_abajo.bottom + 4) and not a.entro_cruce:
                        total += 1
            res[entrada][c] = total
    return res

def contar_conteos_parados():
    p = contar_parados_por_carril()
    return {"oeste": sum(p["oeste"]), "este": sum(p["este"]), "norte": sum(p["norte"]), "sur": sum(p["sur"])}

def estado_semaforo():
    if fase == 0:   return "verde", "rojo"
    if fase == 1:   return "amarillo", "rojo"
    if fase == 2:   return "rojo", "verde"
    return "rojo", "amarillo"

def direccion_en_verde(dir_auto):
    color_america, color_libertador = estado_semaforo()
    if dir_auto in ("e", "o"):  return color_america == "verde"
    if dir_auto in ("n", "s"):  return color_libertador == "verde"
    return False

class Auto:
    def __init__(self, x_inicial, y_inicial, direccion, vel_px_s):
        self.x = float(x_inicial)
        self.y = float(y_inicial)
        self.direccion = direccion
        self.vel_px_por_frame = float(vel_px_s) / float(fps)
        self.img = random.choice(sprites_autos[direccion])
        self.entro_cruce = False

    def punta_pos(self):
        mitad_largo = largo_auto_px // 2
        if self.direccion == "e":  return self.x + mitad_largo
        if self.direccion == "o":  return self.x - mitad_largo
        if self.direccion == "s":  return self.y + mitad_largo
        return self.y - mitad_largo

    def actualizar(self, auto_delante):
        puede_avanzar = True
        mitad_largo = largo_auto_px // 2
        vel = self.vel_px_por_frame

        if self.direccion == "e":
            pos_pare = cebra_izquierda.left - 4;  pos_salida = salida_lib_este;  punta = self.x + mitad_largo
        elif self.direccion == "o":
            pos_pare = cebra_derecha.right + 4;   pos_salida = salida_lib_oeste; punta = self.x - mitad_largo
        elif self.direccion == "s":
            pos_pare = cebra_arriba.top - 4;      pos_salida = salida_lib_sur;   punta = self.y + mitad_largo
        else:
            pos_pare = cebra_abajo.bottom + 4;    pos_salida = salida_lib_norte; punta = self.y - mitad_largo

        if auto_delante is not None:
            if self.direccion == "e" and (auto_delante.x - self.x) < gap_necesario_px: puede_avanzar = False
            if self.direccion == "o" and (self.x - auto_delante.x) < gap_necesario_px: puede_avanzar = False
            if self.direccion == "s" and (auto_delante.y - self.y) < gap_necesario_px: puede_avanzar = False
            if self.direccion == "n" and (self.y - auto_delante.y) < gap_necesario_px: puede_avanzar = False

        if not self.entro_cruce:
            if not direccion_en_verde(self.direccion):
                dist = (pos_pare - punta) if self.direccion in ("e", "s") else (punta - pos_pare)
                if 0 <= dist <= max(1.0, vel * 1.5): puede_avanzar = False

            if direccion_en_verde(self.direccion) and auto_delante is not None:
                if self.direccion == "e" and punta >= pos_pare and auto_delante.x < (pos_salida + gap_necesario_px): puede_avanzar = False
                if self.direccion == "o" and punta <= pos_pare and auto_delante.x > (pos_salida - gap_necesario_px): puede_avanzar = False
                if self.direccion == "s" and punta >= pos_pare and auto_delante.y < (pos_salida + gap_necesario_px): puede_avanzar = False
                if self.direccion == "n" and punta <= pos_pare and auto_delante.y > (pos_salida - gap_necesario_px): puede_avanzar = False

        if puede_avanzar:
            if self.direccion == "e":   self.x += vel
            elif self.direccion == "o": self.x -= vel
            elif self.direccion == "s": self.y += vel
            else:                       self.y -= vel

            if not self.entro_cruce:
                if self.direccion == "e" and self.x + mitad_largo >= pos_pare and direccion_en_verde(self.direccion): self.entro_cruce = True
                if self.direccion == "o" and self.x - mitad_largo <= pos_pare and direccion_en_verde(self.direccion): self.entro_cruce = True
                if self.direccion == "s" and self.y + mitad_largo >= pos_pare and direccion_en_verde(self.direccion): self.entro_cruce = True
                if self.direccion == "n" and self.y - mitad_largo <= pos_pare and direccion_en_verde(self.direccion): self.entro_cruce = True

    def dibujar(self, surf):
        rect = self.img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(self.img, rect)

entradas = ["oeste", "este", "norte", "sur"]
colas = {}
temporizadores = {}

def iniciar_estructuras():
    for entrada in entradas:
        colas[entrada] = []
        temporizadores[entrada] = []
        for _ in range(carriles_por_sentido):
            colas[entrada].append([])
            temporizadores[entrada].append(0.0)
iniciar_estructuras()

def promedio(lista):
    if len(lista) == 0: return 0
    return int(sum(lista) / len(lista))

def ajustar_por_ultimo(lista, direccion, x0, y0):
    if len(lista) > 0:
        u = lista[-1]
        if direccion == "e" and x0 > (u.x - gap_necesario_px): x0 = u.x - gap_necesario_px
        if direccion == "o" and x0 < (u.x + gap_necesario_px): x0 = u.x + gap_necesario_px
        if direccion == "s" and y0 > (u.y - gap_necesario_px): y0 = u.y - gap_necesario_px
        if direccion == "n" and y0 < (u.y + gap_necesario_px): y0 = u.y + gap_necesario_px
    return x0, y0

def limitar_margen_visible(x0, y0, direccion):
    margen = 2 * largo_auto_px - 2
    if direccion == "e" and x0 < -margen: x0 = -margen
    if direccion == "o" and x0 > ancho_ventana + margen: x0 = ancho_ventana + margen
    if direccion == "s" and y0 < -margen: y0 = -margen
    if direccion == "n" and y0 > alto_ventana + margen: y0 = alto_ventana + margen
    return x0, y0

def posicion_aparicion(entrada, i_carril):
    d = multiplo_creacion_lejos * largo_auto_px
    if entrada == "oeste": return cruce_x - media_via_px - d, america_oe[i_carril], "e"
    if entrada == "este":  return cruce_x + media_via_px + d, america_eo[i_carril], "o"
    if entrada == "norte": return libertador_ns[i_carril], cruce_y - media_via_px - d, "s"
    return libertador_sn[i_carril], cruce_y + media_via_px + d, "n"

def aplicar_avance_inicial(x0, y0, direccion, vel_px_s):
    t = random.uniform(avance_inicial_seg_min, avance_inicial_seg_max)
    d = vel_px_s * t
    if direccion == "e":   x0 -= d
    elif direccion == "o": x0 += d
    elif direccion == "s": y0 -= d
    else:                  y0 += d
    return limitar_margen_visible(x0, y0, direccion)

def intentar_aparicion(dt):
    for entrada in entradas:
        for c in range(carriles_por_sentido):
            lista = colas[entrada][c]
            if len(lista) < cola_maxima_por_carril:
                temporizadores[entrada][c] += dt
                if temporizadores[entrada][c] >= intervalo_aparicion_seg:
                    temporizadores[entrada][c] = 0.0
                    x0, y0, dir0 = posicion_aparicion(entrada, c)
                    vel = random.randint(vel_min_px_s, vel_max_px_s)
                    x0, y0 = aplicar_avance_inicial(x0, y0, dir0, vel)
                    x0, y0 = ajustar_por_ultimo(lista, dir0, x0, y0)
                    lista.append(Auto(x0, y0, dir0, vel))

def sembrar_autos_iniciales():
    lim_x_min = -2 * largo_auto_px + 4
    lim_x_max = ancho_ventana + 2 * largo_auto_px - 4
    lim_y_min = -2 * largo_auto_px + 4
    lim_y_max = alto_ventana + 2 * largo_auto_px - 4
    por = autos_iniciales_por_carril

    for c in range(carriles_por_sentido):
        x_base = max(linea_pare_oeste - 2 * largo_auto_px, lim_x_min)
        for i in range(por):
            x0 = max(x_base - i * gap_necesario_px, lim_x_min)
            y0 = america_oe[c]
            vel = random.randint(vel_min_px_s, vel_max_px_s)
            colas["oeste"][c].append(Auto(x0, y0, "e", vel))

    for c in range(carriles_por_sentido):
        x_base = min(linea_pare_este + 2 * largo_auto_px, lim_x_max)
        for i in range(por):
            x0 = min(x_base + i * gap_necesario_px, lim_x_max)
            y0 = america_eo[c]
            vel = random.randint(vel_min_px_s, vel_max_px_s)
            colas["este"][c].append(Auto(x0, y0, "o", vel))

    for c in range(carriles_por_sentido):
        y_base = max(linea_pare_norte - 2 * largo_auto_px, lim_y_min)
        for i in range(por):
            y0 = max(y_base - i * gap_necesario_px, lim_y_min)
            x0 = libertador_ns[c]
            vel = random.randint(vel_min_px_s, vel_max_px_s)
            colas["norte"][c].append(Auto(x0, y0, "s", vel))

    for c in range(carriles_por_sentido):
        y_base = min(linea_pare_sur + 2 * largo_auto_px, lim_y_max)
        for i in range(por):
            y0 = min(y_base + i * gap_necesario_px, lim_y_max)
            x0 = libertador_sn[c]
            vel = random.randint(vel_min_px_s, vel_max_px_s)
            colas["sur"][c].append(Auto(x0, y0, "n", vel))

pasaron_america = 0
pasaron_libertador = 0

series_tiempo = deque(maxlen=300)
serie_existentes_america = deque(maxlen=300)
serie_existentes_lib = deque(maxlen=300)
serie_pasaron_america = deque(maxlen=300)
serie_pasaron_lib = deque(maxlen=300)
serie_parados_america = deque(maxlen=300)
serie_parados_lib = deque(maxlen=300)

ultimo_tiempo_stats = 0.0
t0_series = None

graf = None

blink_interval = 0.5
blink_acc = 0.0
blink_state = False

prev_tiempo_verde_america = tiempo_verde_america
prev_tiempo_verde_libertador = tiempo_verde_libertador

last_phase_change_time = time.time()
last_pid_out = 0.0

beep_sound = None
def crear_beep_opcional():
    global beep_sound
    try:
        import numpy as np
        sr = 22050
        freq = 900
        dur = 0.12
        t = np.linspace(0, dur, int(sr * dur), False)
        tone = (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
        stereo = np.column_stack((tone, tone))
        beep_sound = pygame.sndarray.make_sound(stereo.copy())
        try:
            beep_sound.set_volume(0.2)
        except Exception:
            pass
    except Exception:
        beep_sound = None

def play_beep_once():
    global last_beep_time
    try:
        if beep_sound:
            ahora = time.time()
            if ahora - last_beep_time >= beep_min_interval:
                last_beep_time = ahora
                try:
                    beep_sound.stop()
                except Exception:
                    pass
                beep_sound.play()
    except Exception:
        pass

def debe_parpadear(color, restante):
    if color != "verde":
        return False
    return (restante > 0) and (restante <= blink_threshold)

def posicionar_figura(fig, x, y):
    try:
        m = fig.canvas.manager
        if hasattr(m, "window") and hasattr(m.window, "wm_geometry"):
            m.window.wm_geometry(f"+{x}+{y}")
            return
        if hasattr(m, "window") and hasattr(m.window, "move"):
            m.window.move(x, y)
            return
    except Exception:
        pass

def iniciar_graficas():
    global graf
    plt.ion()
    fig, axs = plt.subplots(3, 1, figsize=(8, 7))
    (l_exist_a,) = axs[0].plot([], [], label="América", linewidth=2)
    (l_exist_l,) = axs[0].plot([], [], label="Libertador", linewidth=2)
    axs[0].set_title("Autos existentes"); axs[0].legend(); axs[0].grid(True)

    (l_pass_a,) = axs[1].plot([], [], label="América", linewidth=2)
    (l_pass_l,) = axs[1].plot([], [], label="Libertador", linewidth=2)
    axs[1].set_title("Autos que pasaron (acumulado)"); axs[1].legend(); axs[1].grid(True)

    (l_stop_a,) = axs[2].plot([], [], label="América", linewidth=2)
    (l_stop_l,) = axs[2].plot([], [], label="Libertador", linewidth=2)
    axs[2].set_title("Autos parados (antes cebra)"); axs[2].legend(); axs[2].grid(True)

    for ax in axs:
        ax.set_xlim(0, 60)
        ax.set_autoscaley_on(True)

    plt.tight_layout()
    plt.show(block=False)

    x = pos_pygame_x + ancho_ventana + 20
    y = pos_pygame_y
    posicionar_figura(fig, x, y)

    graf = {
        "fig": fig, "axs": axs,
        "l_exist_a": l_exist_a, "l_exist_l": l_exist_l,
        "l_pass_a": l_pass_a, "l_pass_l": l_pass_l,
        "l_stop_a": l_stop_a, "l_stop_l": l_stop_l
    }

def actualizar_graficas():
    if not graf:
        return
    fig = graf["fig"]
    if not plt.fignum_exists(fig.number):
        return
    try:
        t = list(series_tiempo)
        xa = list(serie_existentes_america)
        xl = list(serie_existentes_lib)
        pa = list(serie_pasaron_america)
        pl = list(serie_pasaron_lib)
        sa = list(serie_parados_america)
        sl = list(serie_parados_lib)

        if t:
            t0 = t[0]
            t = [ti - t0 for ti in t]
            xmax = max(60, t[-1])
            xmin = max(0, xmax - 60)
            for ax in graf["axs"]:
                ax.set_xlim(xmin, xmax)

        graf["l_exist_a"].set_data(t, xa)
        graf["l_exist_l"].set_data(t, xl)
        graf["axs"][0].relim(); graf["axs"][0].autoscale_view()

        graf["l_pass_a"].set_data(t, pa)
        graf["l_pass_l"].set_data(t, pl)
        graf["axs"][1].relim(); graf["axs"][1].autoscale_view()

        graf["l_stop_a"].set_data(t, sa)
        graf["l_stop_l"].set_data(t, sl)
        graf["axs"][2].relim(); graf["axs"][2].autoscale_view()

        fig.canvas.draw_idle()
        fig.canvas.flush_events()
    except Exception:
        pass

def dibujar_textura(surf, textura, rect):
    tw, th = textura.get_size()
    for x in range(rect.left, rect.right, tw):
        for y in range(rect.top, rect.bottom, th):
            surf.blit(textura, (x, y))

def pintar_base():
    for x in range(0, ventana.get_width(), textura_cesped.get_width()):
        for y in range(0, ventana.get_height(), textura_cesped.get_height()):
            ventana.blit(textura_cesped, (x, y))

    dibujar_textura(ventana, textura_ladrillo, rect_vereda_arr)
    dibujar_textura(ventana, textura_ladrillo, rect_vereda_abj)
    dibujar_textura(ventana, textura_ladrillo, rect_vereda_izq)
    dibujar_textura(ventana, textura_ladrillo, rect_vereda_der)

    dibujar_textura(ventana, textura_asfalto, rect_libertador_izq)
    dibujar_textura(ventana, textura_asfalto, rect_libertador_der)
    dibujar_textura(ventana, textura_asfalto, rect_america_arr)
    dibujar_textura(ventana, textura_asfalto, rect_america_abj)
    pygame.draw.rect(ventana, gris_via, rect_cruce)

    pygame.draw.rect(ventana, gris_est, (0, cruce_y - media_via_px, ancho_ventana, ancho_estacionar_px))
    pygame.draw.rect(ventana, gris_est, (0, cruce_y + media_via_px - ancho_estacionar_px, ancho_ventana, ancho_estacionar_px))
    pygame.draw.rect(ventana, gris_est, (cruce_x - media_via_px, 0, ancho_estacionar_px, alto_ventana))
    pygame.draw.rect(ventana, gris_est, (cruce_x + media_via_px - ancho_estacionar_px, 0, ancho_estacionar_px, alto_ventana))

def dibujar_dashes_h(y, x_ini, x_fin, grosor):
    if x_fin <= x_ini:
        return
    x = x_ini
    while x < x_fin:
        x2 = min(x + largo_tramo_px, x_fin)
        pygame.draw.line(ventana, blanco, (x, y), (x2, y), grosor)
        x = x2 + espacio_tramo_px

def dibujar_dashes_v(x, y_ini, y_fin, grosor):
    if y_fin <= y_ini:
        return
    y = y_ini
    while y < y_fin:
        y2 = min(y + largo_tramo_px, y_fin)
        pygame.draw.line(ventana, blanco, (x, y), (x, y2), grosor)
        y = y2 + espacio_tramo_px

def linea_h_respetando_pare(y, grosor):
    pygame.draw.line(ventana, blanco, (0, y), (linea_pare_oeste - margen_linea_pare, y), grosor)
    pygame.draw.line(ventana, blanco, (linea_pare_este + margen_linea_pare, y), (ancho_ventana, y), grosor)

def linea_v_respetando_pare(x, grosor):
    pygame.draw.line(ventana, blanco, (x, 0), (x, linea_pare_norte - margen_linea_pare), grosor)
    pygame.draw.line(ventana, blanco, (x, linea_pare_sur + margen_linea_pare), (x, alto_ventana), grosor)

def pintar_bordes_y_separadores():
    linea_h_respetando_pare(america_oe[0], grosor_borde_px)
    linea_h_respetando_pare(america_eo[0], grosor_borde_px)
    linea_v_respetando_pare(libertador_sn[0], grosor_borde_px)
    linea_v_respetando_pare(libertador_ns[0], grosor_borde_px)
    for y in america_sep:
        linea_h_respetando_pare(y, grosor_separador_px)
    for x in libertador_sep:
        linea_v_respetando_pare(x, grosor_separador_px)

def pintar_guias_dentro_de_carril():
    for y in america_oe:
        dibujar_dashes_h(y, 0, linea_pare_oeste - margen_linea_pare, grosor_guia_px)
        dibujar_dashes_h(y, linea_pare_este + margen_linea_pare, ancho_ventana, grosor_guia_px)
    for y in america_eo:
        dibujar_dashes_h(y, 0, linea_pare_oeste - margen_linea_pare, grosor_guia_px)
        dibujar_dashes_h(y, linea_pare_este + margen_linea_pare, ancho_ventana, grosor_guia_px)
    for x in libertador_ns:
        dibujar_dashes_v(x, 0, linea_pare_norte - margen_linea_pare, grosor_guia_px)
        dibujar_dashes_v(x, linea_pare_sur + margen_linea_pare, alto_ventana, grosor_guia_px)
    for x in libertador_sn:
        dibujar_dashes_v(x, 0, linea_pare_norte - margen_linea_pare, grosor_guia_px)
        dibujar_dashes_v(x, linea_pare_sur + margen_linea_pare, alto_ventana, grosor_guia_px)

def pintar_cebra_rect(zona, orientacion):
    if orientacion == "h":
        pos = zona.top + margen_cebra_px; limite = zona.bottom - margen_cebra_px
        while pos + grosor_barra_cebra <= limite:
            pygame.draw.rect(ventana, blanco, (zona.left + margen_cebra_px, pos, zona.width - 2 * margen_cebra_px, grosor_barra_cebra))
            pos += (grosor_barra_cebra + espacio_barra_cebra)
    else:
        pos = zona.left + margen_cebra_px; limite = zona.right - margen_cebra_px
        while pos + grosor_barra_cebra <= limite:
            pygame.draw.rect(ventana, blanco, (pos, zona.top + margen_cebra_px, grosor_barra_cebra, zona.height - 2 * margen_cebra_px))
            pos += (grosor_barra_cebra + espacio_barra_cebra)

def pintar_cebras():
    pintar_cebra_rect(cebra_arriba, "v")
    pintar_cebra_rect(cebra_abajo, "v")
    pintar_cebra_rect(cebra_izquierda, "h")
    pintar_cebra_rect(cebra_derecha, "h")

rutas_elementos_posibles = [
    os.path.join("assets", "mobiliario")
]

def buscar_elemento(nombre_png):
    for base in rutas_elementos_posibles:
        ruta = os.path.join(base, nombre_png)
        if os.path.exists(ruta):
            return ruta
    return None

def cargar_elemento(nombre_png, ancho, alto, color_fallback=(200, 200, 200)):
    ruta = buscar_elemento(nombre_png)
    try:
        if ruta is None:
            raise FileNotFoundError
        img = pygame.image.load(ruta).convert_alpha()
        return pygame.transform.smoothscale(img, (ancho, alto))
    except (pygame.error, FileNotFoundError):
        surf = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        pygame.draw.rect(surf, color_fallback, surf.get_rect(), border_radius=6)
        pygame.draw.rect(surf, (80, 80, 80), surf.get_rect(), 2, border_radius=6)
        return surf

img_banquito = cargar_elemento("banquito.png", 40, 20)
img_farol    = cargar_elemento("farol.png", 18, 90)
img_arbol    = cargar_elemento("arbol.png", 50, 50)

img_banquito_h = img_banquito
img_banquito_v = pygame.transform.rotate(img_banquito, 90)

objetos_cesped = []

def agregar_banquito(x, y, orient="h"):
    img = img_banquito_h if orient == "h" else img_banquito_v
    objetos_cesped.append((img, x, y))

def agregar_farol(x, y):
    objetos_cesped.append((img_farol, x, y))

def agregar_arbol(x, y):
    objetos_cesped.append((img_arbol, x, y))

def zona_verde_superior_izquierda():
    return pygame.Rect(0, 0, rect_vereda_izq.left, rect_vereda_arr.top)

def zona_verde_superior_derecha():
    return pygame.Rect(rect_vereda_der.right, 0,
                       ancho_ventana - rect_vereda_der.right, rect_vereda_arr.top)

def zona_verde_inferior_izquierda():
    return pygame.Rect(0, rect_vereda_abj.bottom,
                       rect_vereda_izq.left, alto_ventana - rect_vereda_abj.bottom)

def zona_verde_inferior_derecha():
    return pygame.Rect(rect_vereda_der.right, rect_vereda_abj.bottom,
                       ancho_ventana - rect_vereda_der.right, alto_ventana - rect_vereda_abj.bottom)

def colocar_muchos_en_rect(rect, cant_arboles, cant_bancos, cant_faroles):
    margen = 16

    i = 0
    while i < cant_arboles:
        x = random.randint(rect.left + margen, rect.right - margen)
        y = random.randint(rect.top + margen, rect.bottom - margen)
        agregar_arbol(x, y)
        i += 1

    i = 0

def puntos_equiespaciados(inicio, fin, n):

    if n <= 0:
        return []
    if n == 1:
        return [int((inicio + fin) / 2)]
    paso = (fin - inicio) / float(n - 1)
    lista = []
    i = 0
    while i < n:
        lista.append(int(inicio + i * paso))
        i += 1
    return lista

def equiespaciados_segmento(a, b, n):
    if n <= 0 or b - a < 2: return []
    if n == 1: return [int((a + b) / 2)]
    paso = (b - a) / float(n + 1)
    return [int(a + (i + 1) * paso) for i in range(n)]

def distribuir_en_dos_segmentos(a1, b1, a2, b2, n):
    l1 = max(0, b1 - a1); l2 = max(0, b2 - a2)
    if n <= 0: return [], []
    if l1 == 0: return [], equiespaciados_segmento(a2, b2, n)
    if l2 == 0: return equiespaciados_segmento(a1, b1, n), []
    n1 = round(n * l1 / float(l1 + l2)); n1 = max(0, min(n, n1)); n2 = n - n1
    return equiespaciados_segmento(a1, b1, n1), equiespaciados_segmento(a2, b2, n2)


def colocar_bancos_y_faroles_en_veredas(
    n_horizontal=3,
    n_vertical=2,
    margen=60, separacion=24, margen_cruce=28
):

    for rect in (rect_vereda_arr, rect_vereda_abj):
        xs_izq, xs_der = distribuir_en_dos_segmentos(
            rect.left + margen, inter_x_izq - margen_cruce,
            inter_x_der + margen_cruce, rect.right - margen,
            n_horizontal
        )
        y = rect.centery
        for x in xs_izq + xs_der:
            agregar_banquito(x - separacion, y, orient="h")
            agregar_farol  (x + separacion, y)

    rect = rect_vereda_izq
    ys_sup, ys_inf = distribuir_en_dos_segmentos(
        rect.top + margen, inter_y_sup - margen_cruce,
        inter_y_inf + margen_cruce, rect.bottom - margen,
        n_vertical
    )
    cx = rect.centerx
    for y in ys_sup + ys_inf:
        agregar_banquito(cx - separacion, y, orient="v")
        agregar_farol  (cx + separacion, y)

    rect = rect_vereda_der
    ys_sup, ys_inf = distribuir_en_dos_segmentos(
        rect.top + margen, inter_y_sup - margen_cruce,
        inter_y_inf + margen_cruce, rect.bottom - margen,
        n_vertical
    )
    cx = rect.centerx
    for y in ys_sup + ys_inf:
        agregar_farol  (cx - separacion, y)
        agregar_banquito(cx + separacion, y, orient="v")


def poblar_cesped():
    objetos_cesped.clear()

    arboles_por_zona = 45
    bancos_por_zona = 20
    faroles_por_zona = 15
    colocar_muchos_en_rect(
        zona_verde_superior_izquierda(),
        arboles_por_zona, bancos_por_zona, faroles_por_zona
    )
    colocar_muchos_en_rect(
        zona_verde_superior_derecha(),
        arboles_por_zona, bancos_por_zona, faroles_por_zona
    )
    colocar_muchos_en_rect(
        zona_verde_inferior_izquierda(),
        arboles_por_zona, bancos_por_zona,
        faroles_por_zona
    )
    colocar_muchos_en_rect(
        zona_verde_inferior_derecha(),
        arboles_por_zona, bancos_por_zona,
        faroles_por_zona
    )
    colocar_bancos_y_faroles_en_veredas(
        n_horizontal=3,
        n_vertical=2,
        margen=60, separacion=24, margen_cruce=28
    )

def dibujar_objetos_cesped():
    for img, x, y in objetos_cesped:
        ventana.blit(img, img.get_rect(center=(int(x), int(y))))

def dibujar_semaforo(px, py, es_vertical, color, blink=False, blink_visible=True):
    caja = pygame.Rect(px, py, ancho_semaforo_px, alto_semaforo_px) if es_vertical \
           else pygame.Rect(px, py, alto_semaforo_px, ancho_semaforo_px)

    pygame.draw.rect(ventana, (0, 0, 0), caja, border_radius=3)
    radio = 5

    if color == "rojo":
        c_rojo, c_amarillo, c_verde = rojo_claro, amarillo_oscuro, verde_oscuro
    elif color == "amarillo":
        c_rojo, c_amarillo, c_verde = rojo_oscuro, amarillo_claro, verde_oscuro
    else:
        if blink and not blink_visible:
            c_rojo, c_amarillo, c_verde = rojo_oscuro, amarillo_oscuro, verde_oscuro
        else:
            c_rojo, c_amarillo, c_verde = rojo_oscuro, amarillo_oscuro, verde_claro

    if es_vertical:
        pygame.draw.circle(ventana, c_rojo, (caja.centerx, caja.top + 12), radio)
        pygame.draw.circle(ventana, c_amarillo, (caja.centerx, caja.centery), radio)
        pygame.draw.circle(ventana, c_verde, (caja.centerx, caja.bottom - 12), radio)
    else:
        pygame.draw.circle(ventana, c_rojo, (caja.left + 12, caja.centery), radio)
        pygame.draw.circle(ventana, c_amarillo, (caja.centerx, caja.centery), radio)
        pygame.draw.circle(ventana, c_verde, (caja.right - 12, caja.centery), radio)

def pintar_semaforos():
    color_america, color_libertador = estado_semaforo()
    x_centro_n = promedio(libertador_ns)
    x_centro_s = promedio(libertador_sn)
    y_centro_e = promedio(america_oe)
    y_centro_o = promedio(america_eo)
    margen = 8

    restante_america = max(0.0, tiempo_verde_america - tiempo_en_fase) if color_america == "verde" else 0.0
    restante_lib = max(0.0, tiempo_verde_libertador - tiempo_en_fase) if color_libertador == "verde" else 0.0

    blink_america = debe_parpadear(color_america, restante_america)
    blink_lib = debe_parpadear(color_libertador, restante_lib)

    dibujar_semaforo(int(x_centro_n - alto_semaforo_px / 2),
                     int(linea_pare_norte - ancho_semaforo_px - margen),
                     False, color_libertador, blink=blink_lib, blink_visible=blink_state)

    dibujar_semaforo(int(x_centro_s - alto_semaforo_px / 2),
                     int(linea_pare_sur + margen),
                     False, color_libertador, blink=blink_lib, blink_visible=blink_state)

    dibujar_semaforo(int(linea_pare_oeste - ancho_semaforo_px - margen),
                     int(y_centro_e - alto_semaforo_px / 2),
                     True, color_america, blink=blink_america, blink_visible=blink_state)

    dibujar_semaforo(int(linea_pare_este + margen),
                     int(y_centro_o - alto_semaforo_px / 2),
                     True, color_america, blink=blink_america, blink_visible=blink_state)
    if (blink_america and color_america == "verde") or (blink_lib and color_libertador == "verde"):
        cx = cruce_x
        cy = linea_pare_norte + (linea_pare_sur - linea_pare_norte) // 2
        radio = 10 + (5 if blink_state else 0)
        pygame.draw.circle(ventana, (255, 220, 40) if blink_state else (200, 120, 10), (cx, cy), radio, 3)

def dibujar_panel_info():
    panel_w, panel_h = 360, 260
    panel_x, panel_y = ancho_ventana - panel_w - 10, 10
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    s.fill((20, 20, 20, 180))
    ventana.blit(s, (panel_x, panel_y))
    pygame.draw.rect(ventana, blanco, panel_rect, 2)

    font = pygame.font.SysFont(None, 18)
    conteos = contar_conteos_parados()
    lineas = [
        f"Conteos (antes cebra):",
        f" Oeste:  {conteos['oeste']} autos",
        f" Este:   {conteos['este']} autos",
        f" Norte:  {conteos['norte']} autos",
        f" Sur:    {conteos['sur']} autos",
        f"América base:     {int(round(tiempo_verde_america_base))} s",
        f"América activa:   {int(round(tiempo_verde_america))} s",
        f"Libertador base:  {int(round(tiempo_verde_libertador_base))} s",
        f"Libertador activa:{int(round(tiempo_verde_libertador))} s",
        ""
    ]

    if fase == 0:
        restante = max(0, int(tiempo_verde_america - tiempo_en_fase))
        lineas += ["Fase: América VERDE", f"Queda: {restante} s"]
    elif fase == 1:
        restante = max(0, int(tiempo_amarillo - tiempo_en_fase))
        lineas += ["Fase: Amarillo América", f"Queda: {restante} s"]
    elif fase == 2:
        restante = max(0, int(tiempo_verde_libertador - tiempo_en_fase))
        lineas += ["Fase: Libertador VERDE", f"Queda: {restante} s"]
    else:
        restante = max(0, int(tiempo_amarillo - tiempo_en_fase))
        lineas += ["Fase: Amarillo Libertador", f"Queda: {restante} s"]

    conteos_totales = contar_parados_por_carril()
    total_lib = sum(conteos_totales["norte"]) + sum(conteos_totales["sur"])
    total_amer = sum(conteos_totales["oeste"]) + sum(conteos_totales["este"])
    error = total_lib - total_amer
    lineas.append("")
    y = panel_y + 8
    for ln in lineas:
        ventana.blit(font.render(ln, True, blanco), (panel_x + 8, y))
        y += 18

def avanzar_fase(dt):
    global fase, tiempo_en_fase, tiempo_verde_america, tiempo_verde_libertador
    global tiempo_verde_america_base, tiempo_verde_libertador_base
    global prev_tiempo_verde_america, prev_tiempo_verde_libertador
    global last_phase_change_time, last_pid_out

    tiempo_en_fase += dt
    parados_por_carril = contar_parados_por_carril()
    total_lib = sum(parados_por_carril["norte"]) + sum(parados_por_carril["sur"])
    total_america = sum(parados_por_carril["oeste"]) + sum(parados_por_carril["este"])
    error = float(total_lib - total_america)
    pid_out = pid_controller.update(error, dt)
    last_pid_out = pid_out
    base_nominal = TOTAL_CYCLE / 2.0
    america_new = base_nominal - pid_out
    america_new = max(min_verde, min(max_verde, america_new))
    libertador_new = TOTAL_CYCLE - america_new
    libertador_new = max(min_verde, min(max_verde, libertador_new))
    suma = america_new + libertador_new
    if suma != TOTAL_CYCLE:
        diff = TOTAL_CYCLE - suma
        if diff > 0:
            if america_new < max_verde:
                add = min(diff, max_verde - america_new)
                america_new += add
                diff -= add
            if diff > 0 and libertador_new < max_verde:
                add = min(diff, max_verde - libertador_new)
                libertador_new += add
                diff -= add
        else:
            diff = -diff
            if america_new > min_verde:
                sub = min(diff, america_new - min_verde)
                america_new -= sub
                diff -= sub
            if diff > 0 and libertador_new > min_verde:
                sub = min(diff, libertador_new - min_verde)
                libertador_new -= sub
                diff -= sub

    tiempo_verde_america_base = america_new
    tiempo_verde_libertador_base = libertador_new

    ahora = time.time()
    if tiempo_verde_america_base < prev_tiempo_verde_america:
        pass
    if tiempo_verde_libertador_base < prev_tiempo_verde_libertador:
        pass
    prev_tiempo_verde_america = tiempo_verde_america_base
    prev_tiempo_verde_libertador = tiempo_verde_libertador_base
    if (ahora - last_phase_change_time) >= MIN_TIME_BETWEEN_SWITCHES:
        if fase == 0:
            if tiempo_en_fase >= min_verde and pid_out > EARLY_SWITCH_THRESHOLD:
                fase, tiempo_en_fase = 1, 0.0
                last_phase_change_time = ahora
                return
        if fase == 2:
            if tiempo_en_fase >= min_verde and pid_out < -EARLY_SWITCH_THRESHOLD:
                fase, tiempo_en_fase = 3, 0.0
                last_phase_change_time = ahora
                return
    if fase == 0 and tiempo_en_fase >= tiempo_verde_america:
        fase, tiempo_en_fase = 1, 0.0
        last_phase_change_time = time.time()
    elif fase == 1 and tiempo_en_fase >= tiempo_amarillo:
        fase, tiempo_en_fase = 2, 0.0
        tiempo_verde_libertador = tiempo_verde_libertador_base
        last_phase_change_time = time.time()
    elif fase == 2 and tiempo_en_fase >= tiempo_verde_libertador:
        fase, tiempo_en_fase = 3, 0.0
        last_phase_change_time = time.time()
    elif fase == 3 and tiempo_en_fase >= tiempo_amarillo:
        fase, tiempo_en_fase = 0, 0.0
        tiempo_verde_america = tiempo_verde_america_base
        last_phase_change_time = time.time()

def actualizar_lista(lista):
    global pasaron_america, pasaron_libertador
    for i, auto in enumerate(lista):
        auto_delante = lista[i - 1] if i > 0 else None
        auto.actualizar(auto_delante)
    nueva = []
    for a in lista:
        dentro = (-2 * largo_auto_px < a.x < ancho_ventana + 2 * largo_auto_px) and (-2 * largo_auto_px < a.y < alto_ventana + 2 * largo_auto_px)
        if dentro:
            nueva.append(a)
        else:
            if a.direccion in ("e", "o"): pasaron_america += 1
            else:                         pasaron_libertador += 1
    return nueva

def actualizar_autos():
    for entrada in entradas:
        for c in range(carriles_por_sentido):
            colas[entrada][c] = actualizar_lista(colas[entrada][c])

def dibujar_autos():
    for entrada in entradas:
        for c in range(carriles_por_sentido):
            for auto in colas[entrada][c]:
                auto.dibujar(ventana)

def pintar_escena():
    pintar_base()
    dibujar_objetos_cesped()
    pintar_bordes_y_separadores()
    pintar_guias_dentro_de_carril()
    pintar_cebras()

    pygame.draw.line(ventana, blanco, (inter_x_izq + 8, linea_pare_norte), (inter_x_der - 8, linea_pare_norte), 5)
    pygame.draw.line(ventana, blanco, (inter_x_izq + 8, linea_pare_sur), (inter_x_der - 8, linea_pare_sur), 5)
    pygame.draw.line(ventana, blanco, (linea_pare_oeste, inter_y_sup + 8), (linea_pare_oeste, inter_y_inf - 8), 5)
    pygame.draw.line(ventana, blanco, (linea_pare_este, inter_y_sup + 8), (linea_pare_este, inter_y_inf - 8), 5)

    dibujar_autos()
    pintar_semaforos()
    dibujar_panel_info()

def main():
    global tiempo_verde_america_base, tiempo_verde_libertador_base, tiempo_verde_america, tiempo_verde_libertador, ultimo_tiempo_stats, t0_series
    global blink_acc, blink_state, prev_tiempo_verde_america, prev_tiempo_verde_libertador, last_phase_change_time

    poblar_cesped()
    sembrar_autos_iniciales()

    crear_beep_opcional()

    iniciar_graficas()
    ultimo_tiempo_stats = time.time()
    t0_series = ultimo_tiempo_stats

    prev_tiempo_verde_america = tiempo_verde_america
    prev_tiempo_verde_libertador = tiempo_verde_libertador

    last_phase_change_time = time.time()

    while True:
        dt = reloj.tick(fps) / 1000.0
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        blink_acc += dt
        if blink_acc >= blink_interval:
            blink_acc -= blink_interval
            blink_state = not blink_state

            color_america, color_libertador = estado_semaforo()
            restante_america = max(0.0, tiempo_verde_america - tiempo_en_fase) if color_america == "verde" else 0.0
            restante_lib = max(0.0, tiempo_verde_libertador - tiempo_en_fase) if color_libertador == "verde" else 0.0

            blink_america = debe_parpadear(color_america, restante_america)
            blink_lib = debe_parpadear(color_libertador, restante_lib)

            if blink_state and (blink_america or blink_lib):
                play_beep_once()

        avanzar_fase(dt)
        intentar_aparicion(dt)
        actualizar_autos()

        ahora = time.time()

        if ahora - ultimo_tiempo_stats >= 1.0:
            ultimo_tiempo_stats = ahora
            existentes_america = sum(len(colas["oeste"][c]) + len(colas["este"][c])
                                     for c in range(carriles_por_sentido))
            existentes_lib = sum(len(colas["norte"][c]) + len(colas["sur"][c])
                                 for c in range(carriles_por_sentido))
            conteos = contar_conteos_parados()
            parados_america = conteos["oeste"] + conteos["este"]
            parados_lib = conteos["norte"] + conteos["sur"]

            series_tiempo.append(ahora)
            serie_existentes_america.append(existentes_america)
            serie_existentes_lib.append(existentes_lib)
            serie_pasaron_america.append(pasaron_america)
            serie_pasaron_lib.append(pasaron_libertador)
            serie_parados_america.append(parados_america)
            serie_parados_lib.append(parados_lib)

            actualizar_graficas()

        ventana.fill((0, 0, 0))
        pintar_escena()
        pygame.display.flip()

if __name__ == "__main__":
    main()