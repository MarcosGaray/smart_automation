import logging
import os
from logging import Logger
from colorama import Fore, Style, init as colorama_init
from datetime import datetime
from data import FOLDER_NAME
colorama_init(autoreset=True)

# Folder donde se guardan los logs
LOG_FOLDER = f"logs/{FOLDER_NAME}"

# Usamos fecha + hora sin ":" para Windows
timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
LOG_FILE = os.path.join(LOG_FOLDER, f"migration_{timestamp}.log")


def ensure_log_folder():
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)


def get_logger(name: str = "automation") -> Logger:
    ensure_log_folder()

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Ya está configurado

    logger.setLevel(logging.DEBUG)

    # ----------------------------------------
    # File Handler (DEBUG+)
    # ----------------------------------------
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    # ----------------------------------------
    # Console Handler (INFO+) con color
    # ----------------------------------------
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    def color_formatter(record):
        level = record.levelno
        msg = record.getMessage()
        if level >= logging.ERROR:
            prefix = Fore.RED + "[ERR]" + Style.RESET_ALL
        elif level >= logging.WARNING:
            prefix = Fore.YELLOW + "[WARN]" + Style.RESET_ALL
        elif level >= logging.INFO:
            prefix = Fore.GREEN + "[INFO]" + Style.RESET_ALL
        else:
            prefix = Fore.CYAN + "[DBG]" + Style.RESET_ALL
        return f"{prefix} {msg}"

    class ColorFormatter(logging.Formatter):
        def format(self, record):
            return color_formatter(record)

    ch.setFormatter(ColorFormatter())
    logger.addHandler(ch)

    return logger
