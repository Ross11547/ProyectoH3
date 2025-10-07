import visualizacion as vis

# -------- helpers --------
def _reset_colas(module):
    for ent in module.entradas:
        for c in range(module.carriles_por_sentido):
            module.colas[ent][c].clear()

def _mk_auto(module, dir_):
    if dir_ == "e":
        return module.Auto(module.cruce_x - module.media_via_px - 200, module.america_oe[0], "e", module.vel_min_px_s)
    if dir_ == "o":
        return module.Auto(module.cruce_x + module.media_via_px + 200, module.america_eo[0], "o", module.vel_min_px_s)
    if dir_ == "s":
        return module.Auto(module.libertador_ns[0], module.cruce_y - module.media_via_px - 200, "s", module.vel_min_px_s)
    # "n"
    return module.Auto(module.libertador_sn[0], module.cruce_y + module.media_via_px + 200, "n", module.vel_min_px_s)

# -------- tests --------

def test_forzado_de_cambio_en_fase_0_por_congestion_en_libertador():
    _reset_colas(vis)
    vis.fase = 0  # América verde
    # Clave: igualar base y ajustado, avanzar_fase recalcula usando *_base
    vis.tiempo_verde_america_base = 20.0
    vis.tiempo_verde_america = 20.0
    vis.tiempo_en_fase = 0.0

    # congestión fuerte en Libertador (norte/sur) para disparar el forzado
    for _ in range(vis.disparador_por_sentido + 1):
        vis.colas["norte"][0].append(_mk_auto(vis, "s"))
        vis.colas["norte"][1].append(_mk_auto(vis, "s"))
        vis.colas["sur"][0].append(_mk_auto(vis, "n"))
        vis.colas["sur"][1].append(_mk_auto(vis, "n"))

    vis.avanzar_fase(0.1)

    # Debe reducir el remanente a <= forzar_cambio_restante
    remanente = vis.tiempo_verde_america - vis.tiempo_en_fase
    assert remanente <= vis.forzar_cambio_restante + 1e-6
