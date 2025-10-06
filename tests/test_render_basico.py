import pygame
import visualizacion as vz

def test_pintado_basico_no_explota():
    vz.pintar_base()
    vz.pintar_bordes_y_separadores()
    vz.pintar_guias_dentro_de_carril()
    vz.pintar_cebras()
    vz.pintar_semaforos()
    pygame.display.flip()
