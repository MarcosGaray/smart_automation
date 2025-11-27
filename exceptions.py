class SmartOLTException(Exception):
    """Error general del proceso SmartOLT."""
    pass

class ElementException(SmartOLTException):
    """No se encontró un elemento esperado."""
    pass

class InteractionError(SmartOLTException):
    """Falla en una interacción Selenium."""
    pass

class VlanMigrationError(SmartOLTException):
    """Error específico durante la migración de VLAN."""
    pass
