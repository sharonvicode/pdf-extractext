"""
Configuración de pytest a nivel raíz.

Añade el directorio del proyecto a sys.path para que los tests
puedan importar los paquetes locales (app, main) sin depender de
variables de entorno externas.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
