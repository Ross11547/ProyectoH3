# tests/test_semaforo_basico.py
def test_transicion_fase_0_a_1(vis):
    # fija bases y tiempos a valores pequeños
    vis.tiempo_verde_america_base = 2.0
    vis.tiempo_verde_america = 2.0
    vis.tiempo_verde_libertador_base = 30.0  # da igual aquí
    vis.tiempo_verde_libertador = 30.0

    # evita overrides/adaptaciones durante el test
    vis.fila_minima_para_reducir = 999
    vis.disparador_por_sentido = 999
    vis.disparador_total = 999

    vis.fase = 0
    vis.tiempo_en_fase = 0.0

    vis.avanzar_fase(2.1)  # supera el verde de América
    assert vis.fase == 1 and vis.tiempo_en_fase == 0.0

def test_transicion_ciclo_completo(vis):
    # fija bases y tiempos cortos para avanzar de fase rápido
    vis.tiempo_verde_america_base = 0.2
    vis.tiempo_verde_america = 0.2
    vis.tiempo_verde_libertador_base = 0.2
    vis.tiempo_verde_libertador = 0.2

    vis.fila_minima_para_reducir = 999
    vis.disparador_por_sentido = 999
    vis.disparador_total = 999

    vis.fase = 0
    vis.tiempo_en_fase = 0.0

    vis.avanzar_fase(0.25)              # 0 -> 1
    assert vis.fase == 1
    vis.avanzar_fase(vis.tiempo_amarillo + 0.01)  # 1 -> 2
    assert vis.fase == 2
    vis.avanzar_fase(0.25)              # 2 -> 3
    assert vis.fase == 3
    vis.avanzar_fase(vis.tiempo_amarillo + 0.01)  # 3 -> 0
    assert vis.fase == 0
