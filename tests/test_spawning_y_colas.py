

def _reset_colas(vis):
    for ent in vis.entradas:
        for c in range(vis.carriles_por_sentido):
            vis.colas[ent][c].clear()
            vis.temporizadores[ent][c] = 0.0

def test_aparicion_cuando_temporizador_supera_intervalo(vis):
    _reset_colas(vis)
    ent, c = "oeste", 0
    assert len(vis.colas[ent][c]) == 0
    vis.temporizadores[ent][c] = vis.intervalo_aparicion_seg
    vis.intentar_aparicion(0.0)
    assert len(vis.colas[ent][c]) == 1

def test_no_supera_cola_maxima_por_carril(vis):
    _reset_colas(vis)
    ent, c = "norte", 0
    while len(vis.colas[ent][c]) < vis.cola_maxima_por_carril:
        vis.temporizadores[ent][c] = vis.intervalo_aparicion_seg
        vis.intentar_aparicion(0.0)
    n = len(vis.colas[ent][c])
    vis.temporizadores[ent][c] = vis.intervalo_aparicion_seg
    vis.intentar_aparicion(0.0)
    assert len(vis.colas[ent][c]) == n
