import visualizacion as vz

def _frames(auto, lista_delante=None, n=1):
    for _ in range(n):
        auto.actualizar(lista_delante[-1] if lista_delante else None)

def test_auto_frena_en_rojo_y_avanza_en_verde_este():
    vz.fase = 2  # rojo América, verde Libertador
    vz.tiempo_en_fase = 0.0
    assert vz.estado_semaforo() == ("rojo", "verde")

    vel_px_s = (vz.vel_min_px_s + vz.vel_max_px_s) // 2
    auto = vz.Auto(vz.linea_pare_oeste - vz.largo_auto_px//2, vz.promedio(vz.america_oe), "e", vel_px_s)

    x0 = auto.x
    _frames(auto, n=5)
    assert auto.x <= x0 + auto.vel_px_por_frame + 1.0

    vz.fase = 0  # verde América
    vz.tiempo_en_fase = 0.0
    assert vz.estado_semaforo() == ("verde", "rojo")

    _frames(auto, n=10)
    assert auto.x > x0 + 3 * auto.vel_px_por_frame
