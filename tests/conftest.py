import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import importlib
import pytest

@pytest.fixture(autouse=True)
def reload_module_and_reset_globals():
    # Recargar el módulo para empezar limpio cada test
    if "visualizacion" in importlib.sys.modules:
        del importlib.sys.modules["visualizacion"]

    mod = importlib.import_module("visualizacion")

    # Reset semáforo
    mod.fase = 0
    mod.tiempo_en_fase = 0.0

    # Reset colas/temporizadores
    for k in mod.colas.keys():
        for i in range(len(mod.colas[k])):
            mod.colas[k][i].clear()
    for k in mod.temporizadores.keys():
        for i in range(len(mod.temporizadores[k])):
            mod.temporizadores[k][i] = 0.0

    yield
