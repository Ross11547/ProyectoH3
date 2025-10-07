def test_sembrar_autos_y_contar(vis):
    vis.sembrar_autos_iniciales()
    # Hay autos en al menos una cola por entrada
    assert any(len(l) > 0 for l in vis.colas["oeste"])
    assert any(len(l) > 0 for l in vis.colas["este"])
    assert any(len(l) > 0 for l in vis.colas["norte"])
    assert any(len(l) > 0 for l in vis.colas["sur"])

    conteos = vis.contar_conteos_parados()
    # Debería haber al menos algunos parados antes de cebra
    assert sum(conteos.values()) >= vis.autos_iniciales_por_carril
