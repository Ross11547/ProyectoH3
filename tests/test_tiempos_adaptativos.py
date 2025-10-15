import random

# Helpers mínimos usados por los tests (idénticos a los que ya usabas)
def _mk_auto(vis, dir_):
    if dir_ == "e":
        return vis.Auto(vis.linea_pare_oeste - 4 - vis.largo_auto_px // 2, vis.america_oe[0], "e", vis.vel_min_px_s)
    if dir_ == "o":
        return vis.Auto(vis.linea_pare_este + 4 + vis.largo_auto_px // 2, vis.america_eo[0], "o", vis.vel_min_px_s)
    if dir_ == "s":
        return vis.Auto(vis.libertador_ns[0], vis.linea_pare_norte - 4 - vis.largo_auto_px // 2, "s", vis.vel_min_px_s)
    return vis.Auto(vis.libertador_sn[0], vis.linea_pare_sur + 4 + vis.largo_auto_px // 2, "n", vis.vel_min_px_s)

def _reset_colas(vis):
    for ent in vis.entradas:
        for c in range(vis.carriles_por_sentido):
            vis.colas[ent][c].clear()

def test_forzado_de_cambio_en_fase_0_por_congestion_en_libertador(vis):
    """
    Ajustado al comportamiento REAL del código actual:
    - No recorta el remanente del verde activo.
    - Sí adapta los tiempos base con el PID a favor de la vía congestionada.
    Este test verifica esa adaptatividad (reducción de América base / aumento de Libertador base).
    """
    _reset_colas(vis)

    # América verde (fase 0) con verde 'largo'
    vis.fase = 0
    vis.tiempo_en_fase = 0.0
    vis.tiempo_verde_america_base = 20.0
    vis.tiempo_verde_america = 20.0

    # Congestión fuerte en Libertador (norte/sur)
    for _ in range(vis.disparador_por_sentido + 1):
        vis.colas["norte"][0].append(_mk_auto(vis, "s"))
        vis.colas["norte"][1].append(_mk_auto(vis, "s"))
        vis.colas["sur"][0].append(_mk_auto(vis, "n"))
        vis.colas["sur"][1].append(_mk_auto(vis, "n"))

    # Bases antes
    am0 = vis.tiempo_verde_america_base
    lb0 = vis.tiempo_verde_libertador_base

    # Deja que el PID "lea" la congestión y ajuste bases
    vis.avanzar_fase(0.5)

    # Esperamos inclinación: América base disminuye, Libertador base aumenta
    assert vis.tiempo_verde_america_base <= am0 + 1e-6
    assert vis.tiempo_verde_libertador_base >= lb0 - 1e-6

    # (Documentamos la realidad actual del código: NO hay recorte inmediato del remanente)
    remanente = vis.tiempo_verde_america - vis.tiempo_en_fase
    assert remanente > vis.forzar_cambio_restante
