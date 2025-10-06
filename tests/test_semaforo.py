import visualizacion as vz

def test_ciclo_semaforo():
    assert vz.estado_semaforo() == ("verde", "rojo")
    vz.avanzar_fase(vz.tiempo_verde_america + 0.001)
    assert vz.estado_semaforo() == ("amarillo", "rojo")
    vz.avanzar_fase(vz.tiempo_amarillo + 0.001)
    assert vz.estado_semaforo() == ("rojo", "verde")
    vz.avanzar_fase(vz.tiempo_verde_libertador + 0.001)
    assert vz.estado_semaforo() == ("rojo", "amarillo")
    vz.avanzar_fase(vz.tiempo_amarillo + 0.001)
    assert vz.estado_semaforo() == ("verde", "rojo")
