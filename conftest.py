# conftest.py
# Le dice a pytest que la raíz del proyecto es el directorio actual
# para que los imports funcionen igual que cuando corres la app normal.
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))