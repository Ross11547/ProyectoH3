# tests/test_utils_geometria.py
def test_metros_a_pixeles(vis):
    assert vis.metros_a_pixeles(0) == 0
    assert vis.metros_a_pixeles(1) == 8
    assert vis.metros_a_pixeles(2.5) == 20

def test_puntos_equiespaciados(vis):
    xs = vis.puntos_equiespaciados(0, 10, 5)
    assert xs == [0, 2, 5, 7, 10] or xs == [0, 2, 5, 7, 10]  # tolerante por ints
    assert vis.puntos_equiespaciados(5, 5, 1) == [5]
    assert vis.puntos_equiespaciados(0, 10, 0) == []

def test_equiespaciados_segmento(vis):
    assert vis.equiespaciados_segmento(0, 10, 1) == [5]
    xs = vis.equiespaciados_segmento(0, 12, 3)
    # 3 puntos internos, no tocan bordes
    assert len(xs) == 3
    assert xs[0] > 0 and xs[-1] < 12

def test_distribuir_en_dos_segmentos(vis):
    a1, a2 = vis.distribuir_en_dos_segmentos(0, 50, 60, 100, 6)
    assert len(a1) + len(a2) == 6
    # Todos dentro de sus segmentos
    assert all(0 < x < 50 for x in a1)
    assert all(60 < x < 100 for x in a2)
