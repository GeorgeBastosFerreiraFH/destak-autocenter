import os
import sys
import logging
from pathlib import Path

# Configurações do aplicativo
APP_NAME = "Destak Autocenter"
APP_VERSION = "1.0.0"
DB_NAME = "oficina.db"

# Diretórios
if getattr(sys, 'frozen', False):
    # Se estiver executando como executável compilado
    APP_DIR = Path(sys.executable).parent
else:
    # Se estiver executando como script Python
    APP_DIR = Path(__file__).parent

RESOURCES_DIR = APP_DIR / "resources"
TEMP_DIR = APP_DIR / "temp"
LOG_DIR = APP_DIR / "logs"
DB_PATH = APP_DIR / DB_NAME
CSS_FILE = RESOURCES_DIR / "styles" / "main.css"

# Criar diretórios necessários
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(APP_NAME)

# Configurações da API de veículos
VEHICLE_API_URL = "https://parallelum.com.br/fipe/api/v1"