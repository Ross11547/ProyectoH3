import visualizacion as vis

# ----------------- helpers -----------------

def _mk_pair_following(module, dir_):
    """Crea un líder y un seguidor en el mismo carril con separación > gap."""
    if dir_ in ("e", "o"):
        y = module.america_oe[0]
        if dir_ == "e":
            lead_x = module.cruce_x - module.media_via_px - module.largo_auto_px
            a1 = module.Auto(lead_x, y, "e", module.vel_min_px_s)
            a2 = module.Auto(lead_x - (module.gap_necesario_px + 5), y, "e", module.vel_min_px_s)
        else:  # "o"
            y = module.america_eo[0]
            lead_x = module.cruce_x + module.media_via_px + module.largo_auto_px
            a1 = module.Auto(lead_x, y, "o", module.vel_min_px_s)
            a2 = module.Auto(lead_x + (module.gap_necesario_px + 5), y, "o", module.vel_min_px_s)
    else:
        x = module.libertador_ns[0]
        if dir_ == "s":
            lead_y = module.cruce_y - module.media_via_px - module.largo_auto_px
            a1 = module.Auto(x, lead_y, "s", module.vel_min_px_s)
            a2 = module.Auto(x, lead_y - (module.gap_necesario_px + 5), "s", module.vel_min_px_s)
        else:  # "n"
            x = module.libertador_sn[0]
            lead_y = module.cruce_y + module.media_via_px + module.largo_auto_px
            a1 = module.Auto(x, lead_y, "n", module.vel_min_px_s)
            a2 = module.Auto(x, lead_y + (module.gap_necesario_px + 5), "n", module.vel_min_px_s)
    return a1, a2

def _reset_colas(module):
    for ent in module.entradas:
        for c in range(module.carriles_por_sentido):
            module.colas[ent][c].clear()

# ----------------- tests -----------------

def test_mantiene_separacion_minima():
    a1, a2 = _mk_pair_following(vis, "e")
    vis.fase = 2  # América en rojo
    vis.tiempo_en_fase = 0.0
    a1.actualizar(None)
    a2.actualizar(a1)
    # Tolerancia de ~2px por avance de un frame
    assert (a1.x - a2.x) >= (vis.gap_necesario_px - 2)

def test_contar_parados_antes_de_cebra():
    _reset_colas(vis)

    # OESTE (dir "e"): punta < (left - 4)
    vis.colas["oeste"][0].append(
        vis.Auto(vis.cebra_izquierda.left - 4 - vis.largo_auto_px // 2 - 1,
                 vis.america_oe[0], "e", vis.vel_min_px_s)
    )
    # ESTE (dir "o"): punta > (right + 4)
    vis.colas["este"][0].append(
        vis.Auto(vis.cebra_derecha.right + 4 + vis.largo_auto_px // 2 + 1,
                 vis.america_eo[0], "o", vis.vel_min_px_s)
    )
    # NORTE (dir "s"): punta < (top - 4)
    vis.colas["norte"][0].append(
        vis.Auto(vis.libertador_ns[0],
                 vis.cebra_arriba.top - 4 - vis.largo_auto_px // 2 - 1,
                 "s", vis.vel_min_px_s)
    )
    # SUR (dir "n"): punta > (bottom + 4)
    vis.colas["sur"][0].append(
        vis.Auto(vis.libertador_sn[0],
                 vis.cebra_abajo.bottom + 4 + vis.largo_auto_px // 2 + 1,
                 "n", vis.vel_min_px_s)
    )

    conteos = vis.contar_conteos_parados()
    assert conteos == {"oeste": 1, "este": 1, "norte": 1, "sur": 1}
