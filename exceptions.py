class SmartOLTException(Exception):
    """Error general del proceso SmartOLT."""
    pass

class ElementException(SmartOLTException):
    """No se encontró un elemento esperado."""
    pass

class Disconnected_ONU_Exception(SmartOLTException):
    """Estado de la ONU en 'Power fail','LOS' u 'Offline'."""
    pass

class SVLANException(SmartOLTException):
    """La ONU posee SVLAN. Revisar a mano."""
    pass

class AttachedVlansException(SmartOLTException):
    """La ONU posee mas de una VLANs. Revisar a mano."""
    pass

class ConnectionValidationException(SmartOLTException):
    """Error en el proceso de validar conexión."""
    pass