import os
import logging
from dotenv import load_dotenv

__version__ = "1.0.0"

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# Configurar el logger principal
logging.basicConfig(
    level=LOG_LEVEL.upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)
