def test_importa_y_tiene_ventana(vis):
    # El módulo define la superficie/ventana de pygame al importarse
    assert hasattr(vis, "ventana")
    w, h = vis.ventana.get_size()
    assert (w, h) == (vis.ancho_ventana, vis.alto_ventana)

def test_sprites_cargados(vis):
    # Asegura que hay sprites para cada dirección
    for d in ("n", "s", "e", "o"):
        assert d in vis.sprites_autos
        assert len(vis.sprites_autos[d]) >= 1
