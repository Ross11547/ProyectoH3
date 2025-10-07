# tests/conftest.py
import os
import sys
import importlib
import types
import pytest

# Headless (sin GUI) para pygame y matplotlib
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("MPLBACKEND", "Agg")

@pytest.fixture
def vis(monkeypatch):

    proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if proj_root not in sys.path:
        sys.path.insert(0, proj_root)

    if "visualizacion" in sys.modules:
        del sys.modules["visualizacion"]
    mod = importlib.import_module("visualizacion")

    mod.iniciar_estructuras()
    mod.fase = 0
    mod.tiempo_en_fase = 0.0
    mod.pasaron_america = 0
    mod.pasaron_libertador = 0

    return mod
