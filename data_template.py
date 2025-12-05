# data_template.py
# Copiar este archivo como 'data.py' y completar datos
# -----------------

#Credenciales de inicio de sesión
USER = "tu_usuario_aqui"
PASSWORD = "tu_password_aqui"

# URL: URL de inicio de sesión SmartOLT
URL = "https://smartolt.com/auth/login"

# CONFIGURED_URL: URL para acceder al buscador de ONUS configuradas
CONFIGURED_URL = "https://smartolt.com/onu/configured"

# INPUT_ONUS_FILE: Archivo de entrada de ONUs. Tiene que ser una columna de usernames. Sin HEADER.
#EJEMPLO:
""" 
    username1
    username2
    username3
"""
INPUT_ONUS_FILE = "sheets/input/onus.txt"


#Vlan migration dictionaries: {'actual_vlan': 'target_vlan'}

#Aqui va un diccionario del nombre exacto de la VLAN como aparece en el select del smartOLT. Para más precisión extraer el texto del elemento HTML inspeccionando elemento.
VLAN_MIGRATION_DICT = {'actual_vlan1': 'target_vlan1', 'actual_vlan2': 'target_vlan2'}