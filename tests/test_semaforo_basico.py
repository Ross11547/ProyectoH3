def test_transicion_ciclo_completo(vis, monkeypatch):
    # Desactivar PID (no cambia los tiempos base en función del error)
    monkeypatch.setattr(vis.pid_controller, "update", lambda error, dt: 0.0, raising=True)

    # Fijamos tiempos MUY cortos para la fase 0 (solo el activo de América se respeta);
    # luego el propio código pondrá 30s para Libertador al pasar a fase 2.
    vis.tiempo_verde_america_base = 0.2
    vis.tiempo_verde_america = 0.2
    vis.tiempo_verde_libertador_base = 0.2
    vis.tiempo_verde_libertador = 0.2

    vis.fase = 0
    vis.tiempo_en_fase = 0.0

    # 0 -> 1 (usa el activo de América = 0.2)
    vis.avanzar_fase(0.25)
    assert vis.fase == 1

    # 1 -> 2 (amarillo fijo)
    vis.avanzar_fase(vis.tiempo_amarillo + 0.01)
    assert vis.fase == 2

    # OJO: al entrar a 2, el código hace: tiempo_verde_libertador = tiempo_verde_libertador_base,
    # y como el PID (0) recalculó la base a 30, ahora hay que avanzar ese valor:
    vis.avanzar_fase(vis.tiempo_verde_libertador + 0.01)
    assert vis.fase == 3

    # 3 -> 0 (amarillo fijo)
    vis.avanzar_fase(vis.tiempo_amarillo + 0.01)
    assert vis.fase == 0
