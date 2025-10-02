import visualizacion as vz

def test_metros_a_px_monotono():
    assert vz.m_a_px(0) == 0
    assert vz.m_a_px(1) < vz.m_a_px(2)
    assert vz.m_a_px(5) == 5 * vz.escala_px_por_metro

def test_construir_centros_dimensiones_y_orden():
    lista_pos = vz.construir_centros(100, 10, 3, True)
    assert lista_pos == [105, 115, 125]
    lista_neg = vz.construir_centros(100, 10, 3, False)
    assert lista_neg == [95, 85, 75]

def test_construir_separadores_intermedios():
    seps_pos = vz.construir_separadores(0, 10, 4, True)
    assert seps_pos == [10, 20, 30]
    seps_neg = vz.construir_separadores(0, 10, 4, False)
    assert seps_neg == [-10, -20, -30]

def test_promedio_basico():
    assert vz.promedio([]) == 0
    assert vz.promedio([2, 4, 6]) == 4
