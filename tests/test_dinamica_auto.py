# tests/test_dinamica_auto.py
def test_auto_frena_en_rojo(vis):
    y = vis.america_oe[0]
    # punta = pos_pare - 0.1  (apenas antes de la línea)
    x = vis.cebra_izquierda.left - 4 - (vis.largo_auto_px // 2) - 0.1
    a = vis.Auto(x, y, "e", vis.vel_min_px_s)

    vis.fase = 2          # América rojo
    vis.tiempo_en_fase = 0.0
    a.actualizar(None)

    # No debe avanzar (o casi nada)
    assert a.x <= x + 0.1

def test_auto_avanza_en_verde(vis):
    y = vis.america_oe[0]
    x = vis.cebra_izquierda.left - 4 - (vis.largo_auto_px//2) - 5
    a = vis.Auto(x, y, "e", vis.vel_min_px_s)

    # América VERDE => fase 0
    vis.fase = 0
    vis.tiempo_en_fase = 0.0
    old = a.x
    a.actualizar(None)
    assert a.x > old  # avanzó

def test_respeta_gap_con_auto_delante(vis):
    y = vis.america_oe[0]
    # Auto delantero
    lead = vis.Auto(300, y, "e", vis.vel_min_px_s)
    # Auto detrás muy cerca, debería no avanzar
    tail = vis.Auto(lead.x - (vis.gap_necesario_px - 2), y, "e", vis.vel_min_px_s)

    vis.fase = 0  # verde América
    tail_x = tail.x
    tail.actualizar(lead)
    assert tail.x <= tail_x + 0.1  # prácticamente no se mueve
