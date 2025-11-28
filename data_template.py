# data_template.py
# -----------------
# Copiar este archivo como 'data.py' y completar USER, PASSWORD, URL, y archivo entrada.

USER = "tu_usuario_aqui"
PASSWORD = "tu_password_aqui"
URL = "https://empresa.smartolt.com/auth/login"
CONFIGURED_URL = "https://empresa.smartolt.com/onu/configured"
INPUT_ONUS_FILE = "sheets/input/onus.txt"

# Opcional: tiempo máximo de espera para WebDriverWait en segundos
DEFAULT_WAIT = 15

#vlan migration dictionary
#Aqui va un diccionario del nombre exacto de la VLAN como aparece en el select del smartOLT. Para más precisión extraer el texto del elemento HTML inspeccionando elemento.
#{'actual_vlan': 'target_vlan'}
VLAN_MIGRATION_DICT = {'actual_vlan1': 'target_vlan1', 'actual_vlan2': 'target_vlan2'}