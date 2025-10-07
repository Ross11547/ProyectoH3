import random

def test_posicion_aparicion_por_entrada(vis):
    for i in range(vis.carriles_por_sentido):
        x, y, d = vis.posicion_aparicion("oeste", i)
        assert d == "e" and y == vis.america_oe[i]
        x, y, d = vis.posicion_aparicion("este", i)
        assert d == "o" and y == vis.america_eo[i]
        x, y, d = vis.posicion_aparicion("norte", i)
        assert d == "s" and x == vis.libertador_ns[i]
        x, y, d = vis.posicion_aparicion("sur", i)
        assert d == "n" and x == vis.libertador_sn[i]

def test_aplicar_avance_inicial_limites(vis, monkeypatch):
    random.seed(123)

    vel = vis.vel_min_px_s
    for entrada in ("oeste","este","norte","sur"):
        for i in range(vis.carriles_por_sentido):
            x0, y0, d = vis.posicion_aparicion(entrada, i)
            xi, yi = vis.aplicar_avance_inicial(x0, y0, d, vel)

            assert -2 * vis.largo_auto_px - 4 <= xi <= vis.ancho_ventana + 2 * vis.largo_auto_px + 4
            assert -2 * vis.largo_auto_px - 4 <= yi <= vis.alto_ventana + 2 * vis.largo_auto_px + 4

def test_ajustar_por_ultimo_gap(vis):

    lista = []
    a1 = vis.Auto(100, vis.america_oe[0], "e", vis.vel_min_px_s)
    lista.append(a1)

    x0, y0 = 110, vis.america_oe[0]
    x2, y2 = vis.ajustar_por_ultimo(lista, "e", x0, y0)
    assert (a1.x - x2) >= vis.gap_necesario_px
