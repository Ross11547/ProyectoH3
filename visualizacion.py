import os
import sys
import random
import pygame

pygame.init()

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
distancia_min_autos_m = 6.0
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

carpeta_imagenes = os.path.join("assets", "imagen")

ventana = pygame.display.set_mode((ancho_ventana, alto_ventana))
pygame.display.set_caption("Simulador Vehicular América y Libertador - Semana 2")
reloj = pygame.time.Clock()

ancho_carril_px = metros_a_pixeles(ancho_carril_m)
ancho_estacionar_px = metros_a_pixeles(ancho_estacionar_m)

largo_tramo_px = metros_a_pixeles(largo_tramo_m)
espacio_tramo_px = metros_a_pixeles(espacio_tramo_m)

ancho_auto_px = metros_a_pixeles(ancho_auto_m)
largo_auto_px = metros_a_pixeles(largo_auto_m)

distancia_min_autos_px = metros_a_pixeles(distancia_min_autos_m)
vel_min_px_s = int(velocidad_min_m_s * escala_px_por_metro)
vel_max_px_s = int(velocidad_max_m_s * escala_px_por_metro)

ancho_cebra_px = metros_a_pixeles(ancho_cebra_m)

cruce_x = ancho_ventana // 2
cruce_y = alto_ventana // 2

ancho_lado_px = ancho_estacionar_px + carriles_por_sentido * ancho_carril_px
ancho_via_px = 2 * ancho_lado_px
media_via_px = ancho_via_px // 2

rect_libertador = pygame.Rect(cruce_x - media_via_px, 0, ancho_via_px, alto_ventana)
rect_america = pygame.Rect(0, cruce_y - media_via_px, ancho_ventana, ancho_via_px)

y_america_sup = cruce_y - media_via_px + ancho_estacionar_px
y_america_inf = cruce_y + media_via_px - ancho_estacionar_px
x_lib_izq = cruce_x - media_via_px + ancho_estacionar_px
x_lib_der = cruce_x + media_via_px - ancho_estacionar_px

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
    i = 0
    while i < cantidad:
        if sentido_positivo:
            lista.append(inicio + int((i + 0.5) * paso))
        else:
            lista.append(inicio - int((i + 0.5) * paso))
        i += 1
    return lista

america_oe = construir_centros(y_america_sup, ancho_carril_px, carriles_por_sentido, True)
america_eo = construir_centros(y_america_inf, ancho_carril_px, carriles_por_sentido, False)
libertador_ns = construir_centros(x_lib_der, ancho_carril_px, carriles_por_sentido, False)
libertador_sn = construir_centros(x_lib_izq, ancho_carril_px, carriles_por_sentido, True)

def construir_separadores(inicio, paso, cantidad, sentido_positivo):
    lineas = []
    i = 1
    while i < cantidad:
        if sentido_positivo:
            lineas.append(inicio + i * paso)
        else:
            lineas.append(inicio - i * paso)
        i += 1
    return lineas

def linea_h_respetando_pare(y, grosor):
    pygame.draw.line(ventana, blanco, (0, y), (linea_pare_oeste - margen_linea_pare, y), grosor)
    pygame.draw.line(ventana, blanco, (linea_pare_este + margen_linea_pare, y), (ancho_ventana, y), grosor)

def linea_v_respetando_pare(x, grosor):
    pygame.draw.line(ventana, blanco, (x, 0), (x, linea_pare_norte - margen_linea_pare), grosor)
    pygame.draw.line(ventana, blanco, (x, linea_pare_sur + margen_linea_pare), (x, alto_ventana), grosor)

america_sep = construir_separadores(y_america_sup, ancho_carril_px, carriles_por_sentido, True) \
            + construir_separadores(y_america_inf, ancho_carril_px, carriles_por_sentido, False)

libertador_sep = construir_separadores(x_lib_izq, ancho_carril_px, carriles_por_sentido, True) \
               + construir_separadores(x_lib_der, ancho_carril_px, carriles_por_sentido, False)

def cargar_imagen(nombre):
    ruta = os.path.join(carpeta_imagenes, nombre)
    try:
        return pygame.image.load(ruta).convert_alpha()
    except Exception:
        img = pygame.Surface((largo_auto_px, ancho_auto_px), pygame.SRCALPHA)
        pygame.draw.rect(img, (60, 60, 60), img.get_rect(), border_radius=6)
        pygame.draw.rect(img, (255, 255, 255), img.get_rect(), 2, border_radius=6)
        return img

sprites = {
    "n": [cargar_imagen("auto1.png"), cargar_imagen("auto4.png")],
    "s": [cargar_imagen("auto2.png"), cargar_imagen("auto5.png")],
    "o": [cargar_imagen("auto3.png"), cargar_imagen("auto7.png")],
    "e": [cargar_imagen("auto6.png"), cargar_imagen("auto8.png")],
}

def escalar_sprites():
    direcciones = ["n", "s", "o", "e"]
    i = 0
    while i < len(direcciones):
        d = direcciones[i]
        nuevas = []
        j = 0
        while j < len(sprites[d]):
            img = sprites[d][j]
            if d == "n" or d == "s":
                nuevas.append(pygame.transform.smoothscale(img, (ancho_auto_px, largo_auto_px)))
            else:
                nuevas.append(pygame.transform.smoothscale(img, (largo_auto_px, ancho_auto_px)))
            j += 1
        sprites[d] = nuevas
        i += 1

escalar_sprites()

min_green = 3
max_green = 60
reduction_per_opposing_car = 2

fase = 0
tiempo_en_fase = 0.0

tiempo_verde_america_base = 6
tiempo_verde_libertador_base = 6
tiempo_verde_america = 6
tiempo_verde_libertador = 6

def avanzar_fase(dt):
    global fase, tiempo_en_fase, tiempo_verde_america, tiempo_verde_libertador
    tiempo_en_fase += dt

    if fase == 0 and tiempo_en_fase >= tiempo_verde_america:
        fase = 1
        tiempo_en_fase = 0.0
    elif fase == 1 and tiempo_en_fase >= tiempo_amarillo:
        fase = 2
        tiempo_en_fase = 0.0
        conteos = contar_conteos()
        total_lib = conteos["norte"] + conteos["sur"]
        total_america = conteos["oeste"] + conteos["este"]
        base = max(total_lib * 3, min_green)
        reduction = total_america * reduction_per_opposing_car
        ajustado = max(min_green, base - min(reduction, base - min_green))
        ajustado = min(max_green, ajustado)
        set_libertador_times(base, ajustado)
    elif fase == 2 and tiempo_en_fase >= tiempo_verde_libertador:
        fase = 3
        tiempo_en_fase = 0.0
    elif fase == 3 and tiempo_en_fase >= tiempo_amarillo:
        fase = 0
        tiempo_en_fase = 0.0
        conteos = contar_conteos()
        total_america = conteos["oeste"] + conteos["este"]
        total_lib = conteos["norte"] + conteos["sur"]
        base = max(total_america * 3, min_green)
        reduction = total_lib * reduction_per_opposing_car
        ajustado = max(min_green, base - min(reduction, base - min_green))
        ajustado = min(max_green, ajustado)
        set_america_times(base, ajustado)

def set_libertador_times(base, ajustado):
    global tiempo_verde_libertador_base, tiempo_verde_libertador
    tiempo_verde_libertador_base = base
    tiempo_verde_libertador = ajustado

def set_america_times(base, ajustado):
    global tiempo_verde_america_base, tiempo_verde_america
    tiempo_verde_america_base = base
    tiempo_verde_america = ajustado

def estado_semaforo():
    if fase == 0:
        return "verde", "rojo"
    elif fase == 1:
        return "amarillo", "rojo"
    elif fase == 2:
        return "rojo", "verde"
    else:
        return "rojo", "amarillo"

def esta_en_verde(direccion):
    color_america, color_libertador = estado_semaforo()
    if (direccion == "e" or direccion == "o") and color_america == "verde":
        return True
    if (direccion == "n" or direccion == "s") and color_libertador == "verde":
        return True
    return False

class Auto:
    def __init__(self, x_inicial, y_inicial, direccion, vel_px_s):
        self.x = float(x_inicial)
        self.y = float(y_inicial)
        self.direccion = direccion
        self.vel_px_por_frame = float(vel_px_s) / float(fps)
        opciones = sprites[direccion]
        self.img = opciones[random.randint(0, len(opciones) - 1)]
        self.entro_cruce = False

    def actualizar(self, auto_delante):
        puede_avanzar = True
        mitad_largo = largo_auto_px // 2
        vel = self.vel_px_por_frame

        if self.direccion == "e":
            punta = self.x + mitad_largo
            pos_pare = linea_pare_oeste
            pos_salida = salida_lib_este
        elif self.direccion == "o":
            punta = self.x - mitad_largo
            pos_pare = linea_pare_este
            pos_salida = salida_lib_oeste
        elif self.direccion == "s":
            punta = self.y + mitad_largo
            pos_pare = linea_pare_norte
            pos_salida = salida_lib_sur
        else:
            punta = self.y - mitad_largo
            pos_pare = linea_pare_sur
            pos_salida = salida_lib_norte

        if auto_delante is not None:
            if self.direccion == "e" and (auto_delante.x - self.x) < distancia_min_autos_px:
                puede_avanzar = False
            elif self.direccion == "o" and (self.x - auto_delante.x) < distancia_min_autos_px:
                puede_avanzar = False
            elif self.direccion == "s" and (auto_delante.y - self.y) < distancia_min_autos_px:
                puede_avanzar = False
            elif self.direccion == "n" and (self.y - auto_delante.y) < distancia_min_autos_px:
                puede_avanzar = False

        if not self.entro_cruce:
            if not esta_en_verde(self.direccion):
                if self.direccion == "e" or self.direccion == "s":
                    dist = pos_pare - punta
                else:
                    dist = punta - pos_pare
                margen = vel
                if margen < 1.0:
                    margen = 1.0
                if dist >= 0 and dist <= margen:
                    puede_avanzar = False
            if esta_en_verde(self.direccion) and auto_delante is not None:
                if self.direccion == "e" and punta >= pos_pare and auto_delante.x < (pos_salida + distancia_min_autos_px):
                    puede_avanzar = False
                if self.direccion == "o" and punta <= pos_pare and auto_delante.x > (pos_salida - distancia_min_autos_px):
                    puede_avanzar = False
                if self.direccion == "s" and punta >= pos_pare and auto_delante.y < (pos_salida + distancia_min_autos_px):
                    puede_avanzar = False
                if self.direccion == "n" and punta <= pos_pare and auto_delante.y > (pos_salida - distancia_min_autos_px):
                    puede_avanzar = False
        if puede_avanzar:
            if self.direccion == "e":
                self.x += vel
            elif self.direccion == "o":
                self.x -= vel
            elif self.direccion == "s":
                self.y += vel
            else:
                self.y -= vel
            if not self.entro_cruce:
                if self.direccion == "e" and self.x + mitad_largo >= pos_pare:
                    self.entro_cruce = True
                if self.direccion == "o" and self.x - mitad_largo <= pos_pare:
                    self.entro_cruce = True
                if self.direccion == "s" and self.y + mitad_largo >= pos_pare:
                    self.entro_cruce = True
                if self.direccion == "n" and self.y - mitad_largo <= pos_pare:
                    self.entro_cruce = True

    def dibujar(self, surf):
        rect = self.img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(self.img, rect)

entradas = ["oeste", "este", "norte", "sur"]
colas = {}
temporizadores = {}

def iniciar_estructuras():
    i_e = 0
    while i_e < len(entradas):
        entrada = entradas[i_e]
        colas[entrada] = []
        temporizadores[entrada] = []
        c = 0
        while c < carriles_por_sentido:
            colas[entrada].append([])
            temporizadores[entrada].append(0.0)
            c += 1
        i_e += 1

iniciar_estructuras()

def promedio(lista):
    if len(lista) == 0:
        return 0
    s = 0
    i = 0
    while i < len(lista):
        s += lista[i]
        i += 1
    return int(s / len(lista))

def ajustar_por_ultimo(lista, direccion, x0, y0):
    if len(lista) > 0:
        u = lista[-1]
        if direccion == "e" and x0 > (u.x - distancia_min_autos_px):
            x0 = u.x - distancia_min_autos_px
        if direccion == "o" and x0 < (u.x + distancia_min_autos_px):
            x0 = u.x + distancia_min_autos_px
        if direccion == "s" and y0 > (u.y - distancia_min_autos_px):
            y0 = u.y - distancia_min_autos_px
        if direccion == "n" and y0 < (u.y + distancia_min_autos_px):
            y0 = u.y + distancia_min_autos_px
        return x0, y0
    return x0, y0

def limitar_margen_visible(x0, y0, direccion):
    margen = 2 * largo_auto_px - 2
    if direccion == "e" and x0 < -margen:
        x0 = -margen
    if direccion == "o" and x0 > ancho_ventana + margen:
        x0 = ancho_ventana + margen
    if direccion == "s" and y0 < -margen:
        y0 = -margen
    if direccion == "n" and y0 > alto_ventana + margen:
        y0 = alto_ventana + margen
    return x0, y0

def posicion_aparicion(entrada, i_carril):
    d = multiplo_creacion_lejos * largo_auto_px
    if entrada == "oeste":
        return cruce_x - media_via_px - d, america_oe[i_carril], "e"
    if entrada == "este":
        return cruce_x + media_via_px + d, america_eo[i_carril], "o"
    if entrada == "norte":
        return libertador_ns[i_carril], cruce_y - media_via_px - d, "s"
    else:
        return libertador_sn[i_carril], cruce_y + media_via_px + d, "n"

def aplicar_avance_inicial(x0, y0, direccion, vel_px_s):
    t = random.uniform(avance_inicial_seg_min, avance_inicial_seg_max)
    d = vel_px_s * t
    if direccion == "e":
        x0 -= d
    elif direccion == "o":
        x0 += d
    elif direccion == "s":
        y0 -= d
    else:
        y0 += d
    return limitar_margen_visible(x0, y0, direccion)

def intentar_aparicion(dt):
    i_e = 0
    while i_e < len(entradas):
        entrada = entradas[i_e]
        c = 0
        while c < carriles_por_sentido:
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
            c += 1
        i_e += 1

def sembrar_autos_iniciales():
    lim_x_min = -2 * largo_auto_px + 4
    lim_x_max = ancho_ventana + 2 * largo_auto_px - 4
    lim_y_min = -2 * largo_auto_px + 4
    lim_y_max = alto_ventana + 2 * largo_auto_px - 4

    por = autos_iniciales_por_carril
    separacion = distancia_min_autos_px + largo_auto_px

    c = 0
    while c < carriles_por_sentido:
        i = 0
        x_base = max(linea_pare_oeste - 2 * largo_auto_px, lim_x_min)
        while i < por:
            x0 = max(x_base - i * separacion, lim_x_min)
            y0 = america_oe[c]
            vel = random.randint(vel_min_px_s, vel_max_px_s)
            colas["oeste"][c].append(Auto(x0, y0, "e", vel))
            i += 1
        c += 1

    c = 0
    while c < carriles_por_sentido:
        i = 0
        x_base = min(linea_pare_este + 2 * largo_auto_px, lim_x_max)
        while i < por:
            x0 = min(x_base + i * separacion, lim_x_max)
            y0 = america_eo[c]
            vel = random.randint(vel_min_px_s, vel_max_px_s)
            colas["este"][c].append(Auto(x0, y0, "o", vel))
            i += 1
        c += 1

    c = 0
    while c < carriles_por_sentido:
        i = 0
        y_base = max(linea_pare_norte - 2 * largo_auto_px, lim_y_min)
        while i < por:
            y0 = max(y_base - i * separacion, lim_y_min)
            x0 = libertador_ns[c]
            vel = random.randint(vel_min_px_s, vel_max_px_s)
            colas["norte"][c].append(Auto(x0, y0, "s", vel))
            i += 1
        c += 1

    c = 0
    while c < carriles_por_sentido:
        i = 0
        y_base = min(linea_pare_sur + 2 * largo_auto_px, lim_y_max)
        while i < por:
            y0 = min(y_base + i * separacion, lim_y_max)
            x0 = libertador_sn[c]
            vel = random.randint(vel_min_px_s, vel_max_px_s)
            colas["sur"][c].append(Auto(x0, y0, "n", vel))
            i += 1
        c += 1

def actualizar_lista(lista):
    i = 0
    while i < len(lista):
        auto = lista[i]
        auto_delante = lista[i - 1] if i > 0 else None
        auto.actualizar(auto_delante)
        i += 1
    nueva = []
    j = 0
    while j < len(lista):
        a = lista[j]
        if (-2 * largo_auto_px < a.x < ancho_ventana + 2 * largo_auto_px) and \
           (-2 * largo_auto_px < a.y < alto_ventana + 2 * largo_auto_px):
            nueva.append(a)
        j += 1
    return nueva

def actualizar_autos():
    i_e = 0
    while i_e < len(entradas):
        entrada = entradas[i_e]
        c = 0
        while c < carriles_por_sentido:
            colas[entrada][c] = actualizar_lista(colas[entrada][c])
            c += 1
        i_e += 1

def dibujar_autos():
    i_e = 0
    while i_e < len(entradas):
        entrada = entradas[i_e]
        c = 0
        while c < carriles_por_sentido:
            lista = colas[entrada][c]
            j = 0
            while j < len(lista):
                lista[j].dibujar(ventana)
                j += 1
            c += 1
        i_e += 1

def pintar_base():
    ventana.fill(verde_fondo)
    pygame.draw.rect(ventana, gris_via, rect_libertador)
    pygame.draw.rect(ventana, gris_via, rect_america)

    pygame.draw.rect(ventana, gris_est, (0, cruce_y - media_via_px, ancho_ventana, ancho_estacionar_px))
    pygame.draw.rect(ventana, gris_est, (0, cruce_y + media_via_px - ancho_estacionar_px, ancho_ventana, ancho_estacionar_px))
    pygame.draw.rect(ventana, gris_est, (cruce_x - media_via_px, 0, ancho_estacionar_px, alto_ventana))
    pygame.draw.rect(ventana, gris_est, (cruce_x + media_via_px - ancho_estacionar_px, 0, ancho_estacionar_px, alto_ventana))

def dibujar_dashes_h_segmento(y, x_inicio, x_fin, grosor):
    if x_fin <= x_inicio:
        return
    x = x_inicio
    while x < x_fin:
        x2 = x + largo_tramo_px
        if x2 > x_fin:
            x2 = x_fin
        pygame.draw.line(ventana, blanco, (x, y), (x2, y), grosor)
        x = x2 + espacio_tramo_px

def dibujar_dashes_v_segmento(x, y_inicio, y_fin, grosor):
    if y_fin <= y_inicio:
        return
    y = y_inicio
    while y < y_fin:
        y2 = y + largo_tramo_px
        if y2 > y_fin:
            y2 = y_fin
        pygame.draw.line(ventana, blanco, (x, y), (x, y2), grosor)
        y = y2 + espacio_tramo_px

def pintar_bordes_y_separadores():
    linea_h_respetando_pare(y_america_sup, grosor_borde_px)
    linea_h_respetando_pare(y_america_inf, grosor_borde_px)
    linea_v_respetando_pare(x_lib_izq, grosor_borde_px)
    linea_v_respetando_pare(x_lib_der, grosor_borde_px)

    i = 0
    while i < len(america_sep):
        y = america_sep[i]
        linea_h_respetando_pare(y, grosor_separador_px)
        i += 1

    i = 0
    while i < len(libertador_sep):
        x = libertador_sep[i]
        linea_v_respetando_pare(x, grosor_separador_px)
        i += 1

    linea_h_respetando_pare(cruce_y, grosor_separador_px)
    linea_v_respetando_pare(cruce_x, grosor_separador_px)

def pintar_guias_dentro_de_carril():
    i = 0
    while i < len(america_oe):
        y = america_oe[i]
        dibujar_dashes_h_segmento(y, 0, linea_pare_oeste - margen_linea_pare, grosor_guia_px)
        dibujar_dashes_h_segmento(y, linea_pare_este + margen_linea_pare, ancho_ventana, grosor_guia_px)
        i += 1

    i = 0
    while i < len(america_eo):
        y = america_eo[i]
        dibujar_dashes_h_segmento(y, 0, linea_pare_oeste - margen_linea_pare, grosor_guia_px)
        dibujar_dashes_h_segmento(y, linea_pare_este + margen_linea_pare, ancho_ventana, grosor_guia_px)
        i += 1

    i = 0
    while i < len(libertador_ns):
        x = libertador_ns[i]
        dibujar_dashes_v_segmento(x, 0, linea_pare_norte - margen_linea_pare, grosor_guia_px)
        dibujar_dashes_v_segmento(x, linea_pare_sur + margen_linea_pare, alto_ventana, grosor_guia_px)
        i += 1

    i = 0
    while i < len(libertador_sn):
        x = libertador_sn[i]
        dibujar_dashes_v_segmento(x, 0, linea_pare_norte - margen_linea_pare, grosor_guia_px)
        dibujar_dashes_v_segmento(x, linea_pare_sur + margen_linea_pare, alto_ventana, grosor_guia_px)
        i += 1

def pintar_cebra_rect(zona, orientacion):
    if orientacion == "h":
        pos = zona.top + margen_cebra_px
        limite = zona.bottom - margen_cebra_px
        while pos + grosor_barra_cebra <= limite:
            pygame.draw.rect(ventana, blanco, (zona.left + margen_cebra_px, pos, zona.width - 2 * margen_cebra_px, grosor_barra_cebra))
            pos += (grosor_barra_cebra + espacio_barra_cebra)
    else:
        pos = zona.left + margen_cebra_px
        limite = zona.right - margen_cebra_px
        while pos + grosor_barra_cebra <= limite:
            pygame.draw.rect(ventana, blanco, (pos, zona.top + margen_cebra_px, grosor_barra_cebra, zona.height - 2 * margen_cebra_px))
            pos += (grosor_barra_cebra + espacio_barra_cebra)

def pintar_cebras():
    pintar_cebra_rect(cebra_arriba, "v")
    pintar_cebra_rect(cebra_abajo, "v")
    pintar_cebra_rect(cebra_izquierda, "h")
    pintar_cebra_rect(cebra_derecha, "h")

def dibujar_semaforo(px, py, es_vertical, color):
    if es_vertical:
        caja = pygame.Rect(px, py, ancho_semaforo_px, alto_semaforo_px)
    else:
        caja = pygame.Rect(px, py, alto_semaforo_px, ancho_semaforo_px)

    pygame.draw.rect(ventana, (0, 0, 0), caja, border_radius=3)
    radio = 5

    if color == "rojo":
        c_rojo = rojo_claro
        c_amarillo = amarillo_oscuro
        c_verde = verde_oscuro
    elif color == "amarillo":
        c_rojo = rojo_oscuro
        c_amarillo = amarillo_claro
        c_verde = verde_oscuro
    else:
        c_rojo = rojo_oscuro
        c_amarillo = amarillo_oscuro
        c_verde = verde_claro

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
    margen = 6

    dibujar_semaforo(int(x_centro_n - ancho_semaforo_px / 2), int(linea_pare_norte - alto_semaforo_px - margen), True, color_libertador)
    dibujar_semaforo(int(x_centro_s - ancho_semaforo_px / 2), int(linea_pare_sur + margen), True, color_libertador)

    dibujar_semaforo(int(linea_pare_oeste - alto_semaforo_px - margen), int(y_centro_e - ancho_semaforo_px / 2), False, color_america)
    dibujar_semaforo(int(linea_pare_este + margen), int(y_centro_o - ancho_semaforo_px / 2), False, color_america)

mostrar_estacionados = True
plazas_est = []

def poblar_estacionamiento():
    if not mostrar_estacionados:
        return

    y_arr = cruce_y - media_via_px + ancho_estacionar_px // 2

    i = 0
    while i < 5:
        plazas_est.append(("h", 10 + i * (largo_auto_px + 14), y_arr))
        i += 1

    y_aba = cruce_y + media_via_px - ancho_estacionar_px // 2
    i = 0
    while i < 5:
        plazas_est.append(("h", ancho_ventana - 10 - i * (largo_auto_px + 14), y_aba))
        i += 1

    x_izq = cruce_x - media_via_px + ancho_estacionar_px // 2
    i = 0
    while i < 4:
        plazas_est.append(("v", x_izq, 10 + i * (largo_auto_px + 14)))
        i += 1

    x_der = cruce_x + media_via_px - ancho_estacionar_px // 2
    i = 0
    while i < 4:
        plazas_est.append(("v", x_der, alto_ventana - 10 - i * (largo_auto_px + 14)))
        i += 1

def dibujar_estacionamiento():
    if not mostrar_estacionados:
        return
    img_h = sprites["e"][0]
    img_v = sprites["s"][0]

    i = 0
    while i < len(plazas_est):
        ori, cx, cy = plazas_est[i]
        if ori == "h":
            ventana.blit(img_h, img_h.get_rect(center=(int(cx), int(cy))))
        else:
            ventana.blit(img_v, img_v.get_rect(center=(int(cx), int(cy))))
        i += 1

def contar_conteos():
    return {
        "oeste":
            sum(len(colas["oeste"][i]) 
                for i in range(carriles_por_sentido)),
        "este":
            sum(len(colas["este"][i])  
                for i in range(carriles_por_sentido)),
        "norte": 
            sum(len(colas["norte"][i]) 
                for i in range(carriles_por_sentido)),
        "sur":   
            sum(len(colas["sur"][i])   
                for i in range(carriles_por_sentido))
    }

def dibujar_panel_info():
    panel_w = 260
    panel_h = 200
    panel_x = ancho_ventana - panel_w - 10
    panel_y = 10
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    s = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    s.fill((20, 20, 20, 180))
    ventana.blit(s, (panel_x, panel_y))
    pygame.draw.rect(ventana, blanco, panel_rect, 2)

    font = pygame.font.SysFont(None, 20)
    conteos = contar_conteos()
    lines = [
        f"Conteos por carril:",
        f" Oeste:  {conteos['oeste']} autos",
        f" Este:   {conteos['este']} autos",
        f" Norte:  {conteos['norte']} autos",
        f" Sur:    {conteos['sur']} autos",
        "",
        f"America base:      {tiempo_verde_america_base}s",
        f"America ajustado:  {int(tiempo_verde_america)}s",
        f"Libertador base:   {tiempo_verde_libertador_base}s",
        f"Libertador ajust:  {int(tiempo_verde_libertador)}s",
        ""
    ]

    if fase == 0:
        restante = max(0, int(tiempo_verde_america - tiempo_en_fase))
        lines.append(f"Fase: America VERDE")
        lines.append(f"Queda: {restante}s")
    elif fase == 1:
        restante = max(0, int(tiempo_amarillo - tiempo_en_fase))
        lines.append("Fase: Amarillo America")
        lines.append(f"Queda: {restante}s")
    elif fase == 2:
        restante = max(0, int(tiempo_verde_libertador - tiempo_en_fase))
        lines.append("Fase: Libertador VERDE")
        lines.append(f"Queda: {restante}s")
    else:
        restante = max(0, int(tiempo_amarillo - tiempo_en_fase))
        lines.append("Fase: Amarillo Libertador")
        lines.append(f"Queda: {restante}s")

    y = panel_y + 8
    x = panel_x + 8
    for ln in lines:
        img = font.render(ln, True, blanco)
        ventana.blit(img, (x, y))
        y += 18

def pintar_escena():
    pintar_base()
    pintar_bordes_y_separadores()
    pintar_guias_dentro_de_carril()
    pintar_cebras()

    pygame.draw.line(ventana, blanco, (inter_x_izq + 8, linea_pare_norte), (inter_x_der - 8, linea_pare_norte), 5)
    pygame.draw.line(ventana, blanco, (inter_x_izq + 8, linea_pare_sur), (inter_x_der - 8, linea_pare_sur), 5)
    pygame.draw.line(ventana, blanco, (linea_pare_oeste, inter_y_sup + 8), (linea_pare_oeste, inter_y_inf - 8), 5)
    pygame.draw.line(ventana, blanco, (linea_pare_este, inter_y_sup + 8), (linea_pare_este, inter_y_inf - 8), 5)

    dibujar_estacionamiento()
    dibujar_autos()
    pintar_semaforos()
    dibujar_panel_info()

def main():
    global tiempo_verde_america_base, tiempo_verde_libertador_base, tiempo_verde_america, tiempo_verde_libertador, tiempo_en_fase
    poblar_estacionamiento()
    sembrar_autos_iniciales()

    conteos = contar_conteos()
    total_america = conteos["oeste"] + conteos["este"]
    total_lib = conteos["norte"] + conteos["sur"]
    tiempo_verde_america_base = max(total_america * 3, min_green)
    tiempo_verde_libertador_base = max(total_lib * 3, min_green)

    reduction_L = total_america * reduction_per_opposing_car
    tiempo_verde_libertador = min(max_green, max(min_green, tiempo_verde_libertador_base - min(reduction_L, tiempo_verde_libertador_base - min_green)))

    reduction_A = total_lib * reduction_per_opposing_car
    tiempo_verde_america = min(max_green, max(min_green, tiempo_verde_america_base - min(reduction_A, tiempo_verde_america_base - min_green)))

    print(f"Inicial: base_A={tiempo_verde_america_base}s adj_A={tiempo_verde_america}s | base_L={tiempo_verde_libertador_base}s adj_L={tiempo_verde_libertador}s")

    while True:
        dt = reloj.tick(fps) / 1000.0
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        avanzar_fase(dt)
        intentar_aparicion(dt)
        actualizar_autos()
        ventana.fill((0,0,0))
        pintar_escena()
        pygame.display.flip()

if __name__ == "__main__":
    main()
