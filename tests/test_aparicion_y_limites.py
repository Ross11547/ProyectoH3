import visualizacion as vz

def test_posicion_aparicion_direcciones():
    x, y, d = vz.posicion_aparicion("oeste", 0);  assert d == "e"
    x, y, d = vz.posicion_aparicion("este", 0);   assert d == "o"
    x, y, d = vz.posicion_aparicion("norte", 0);  assert d == "s"
    x, y, d = vz.posicion_aparicion("sur", 0);    assert d == "n"

def test_limitar_margen_visible_no_sale_de_rango():
    x, y = vz.limitar_margen_visible(-10_000, -10_000, "e")
    assert x >= -2 * vz.largo_auto_px - 2
    assert y >= -2 * vz.largo_auto_px - 2
    x, y = vz.limitar_margen_visible(10_000, 10_000, "n")
    assert x <= vz.ancho_ventana + 2 * vz.largo_auto_px + 2
    assert y <= vz.alto_ventana + 2 * vz.largo_auto_px + 2
