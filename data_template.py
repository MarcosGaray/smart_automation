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
INPUT_ONUS_FILE = "exports/input/onus.txt"
FOLDER_NAME = "RName"

#RECHECK: Es para determinar si procesar onus que ya fueron migradas anteriormente. Afecta al paso 10 y 11 de onu_actions.py
# Comportamiento normal: False -> no procesa la onu si ya se encuentra en la target_vlan
# Comportamiento alternativo: True -> procesa la onu incluso aunque ya se encuentre en la target_vlan
RECHECK = False

# PPP_VALID_GATEWAY_LIST: Lista de nombres de las interfaces PPP validas
PPP_VALID_GATEWAY_LIST = ["Ip_address1", "Ip_address2", "Ip_address3"]

#Vlan migration dictionaries: {'actual_vlan': 'target_vlan'}

#Aqui va un diccionario del nombre exacto de la VLAN como aparece en el select del smartOLT. Para más precisión extraer el texto del elemento HTML inspeccionando elemento.
VLAN_MIGRATION_DICT = {'actual_vlan1': 'target_vlan1', 
                        'actual_vlan2': 'target_vlan2'
                        }



######### SPEED PROFILE CHANGE  ########
#CAMBIAR ID'S A LOS PROPIOS
SPEED_PROFILE_URLS = [f"{CONFIGURED_URL}/?sort_by=id&sort_order=desc&speed_profile_id=63",
                      f"{CONFIGURED_URL}/?sort_by=id&sort_order=desc&speed_profile_id=65",
                      f"{CONFIGURED_URL}/?sort_by=id&sort_order=desc&speed_profile_id=62",
                      f"{CONFIGURED_URL}/?sort_by=id&sort_order=desc&speed_profile_id=60",
                      f"{CONFIGURED_URL}/?sort_by=id&sort_order=desc&speed_profile_id=58"
                      ]


#SPEEDS_PROFILE_DICT

SPEEDS_PROFILE_DICT = {
    '25Mbps': '25M',
    '25M': '25M',

    '50Mbps': '50M',
    '50M': '50M',

    '75Mbps': '75M',
    '75M': '75M',

    '100Mbps': '100M',
    '100M': '100M',

    '150Mbps': '150M',
    '150M': '150M',

    '125Mbps': '125M',
    '125M': '125M',

    '200Mbps': '200M',
    '200M': '200M',

    '300Mbps': '300M',
    '300M': '300M',

    '350Mbps': '350M',
    '350M': '350M',

    '400Mbps': '400M',
    '400M': '400M',

    '500Mbps': '500M',
    '500M': '500M',
}