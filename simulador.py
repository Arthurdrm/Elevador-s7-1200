"""Ponto de Entrada do Projeto_Elevador_s7-1200 — Simulador Interativo Siemens S7-1200.
Desenvolvido para Prática Avaliativa SENAI - Desafio Industrial 3.

Execução:
    ./run_simulador.sh
    ou
    python simulador.py
"""

import sys
import os

# Configurações de ambiente para Linux/X11 e PySide6
local_lib = os.path.expanduser("~/.local/lib")
if os.path.isdir(local_lib):
    curr_ld = os.environ.get("LD_LIBRARY_PATH", "")
    if local_lib not in curr_ld:
        os.environ["LD_LIBRARY_PATH"] = f"{local_lib}:{curr_ld}" if curr_ld else local_lib

try:
    import PySide6
    qt_plugins = os.path.join(os.path.dirname(PySide6.__file__), "Qt", "plugins")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_plugins
except Exception:
    pass

from PySide6.QtWidgets import QApplication
from src.simulador.ui_window import MainWindowSimuladorElevador

def main():
    app = QApplication(sys.argv)
    window = MainWindowSimuladorElevador()
    window.show()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
