import logging
import os
from logging import Logger
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

LOG_FILE = "automation.log"

def get_logger(name: str = "automation") -> Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # ya configurado

    logger.setLevel(logging.DEBUG)

    # File handler (DEBUG+)
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    # Console handler (INFO+), con colores simples
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
