class SmartOLTException(Exception):
    """Error general del proceso SmartOLT."""
    pass

class ElementException(SmartOLTException):
    """No se encontró un elemento esperado."""
    pass