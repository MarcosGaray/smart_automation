from utils.helpers import assert_real_function_result, wait_visible
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from utils.logger import get_logger
from sheets.sheets_reader import load_check_connection_list
from sheets.sheets_writer import log_connection_success, log_connection_fail
from exceptions import ElementException,  ConnectionValidationException
from smartolt.onu_actions import get_onu_status, resync_onu_config
from utils.helpers import safe_click
import time
from data import PPP_GATEWAY
from utils import words_and_messages as msg
from smartolt.onu_functions import get_ppp_gateway


logger = get_logger(__name__)

def start_connection_validation(driver, onu_list = None, step = 1):
    try:
        if(onu_list is None):
            onu_list= load_check_connection_list()
    except Exception:  
        raise ConnectionValidationException(f"No se pudo leer archivo de entrada")
    
    check_again_onu_list = []

    for onu_data in onu_list:
        print("------------------")
        onu_username = onu_data[0]
        onu_url = onu_data[1]
        logger.info(f"Step {step}: Iniciando validación de conexión... ONU: {onu_username}")
        driver.get(onu_url)

        # 1) Revisar el estado de la ONU
        expected_status = 'Online'
        try:
            onu_status = assert_real_function_result(get_onu_status,driver, expected_status, msg.ONU_STATUS_ATTEMP_MSG)  
            logger.info("Estado de la ONU: " + onu_status)
        except Exception:
            log_connection_fail(onu_username, f"Error al obtener el estado de la ONU", onu_url)
            logger.error(f"ERROR {onu_username}: Error al obtener el estado de la ONU")
            continue

        if not onu_status.__contains__(expected_status):
            if step <= 3:
                logger.warning(f"ONU {onu_username} Offline. Se agrega a la lista de ONUs para reintentar")
                check_again_onu_list.append(onu_data)
            else:
                log_connection_fail(onu_username, "ONU Offline", onu_url)
                logger.error(f"ERROR {onu_username}: ONU Offline")
            continue

        # open_tr069_and_check_ppp
        try:
            connection_status_text, resync= open_tr069_and_check_connectivity(driver)
            if resync:
                logger.warning(f"ONU {onu_username} - PPP Gateway no es el esperado. Se agrega a la lista de ONUs para reintentar")
                check_again_onu_list.append(onu_data)
                continue
        except Exception as e:
            short_msg = getattr(e, "msg", str(e)).split("\n")[0].strip()
            if step <= 3:
                logger.warning(f"ONU {onu_username} - {short_msg}. Se agrega a la lista de ONUs para reintentar")
                check_again_onu_list.append(onu_data)
            else:
                # Hacer resync
                try:
                    log_connection_fail(onu_username, f"{short_msg}", onu_url)
                    logger.error(f"ERROR {onu_username}: {e}")
                    resync_onu_config(driver, timeout=60)
                    logger.info(f"ONU {onu_username} Resync exitoso")
                except Exception as ex:
                    logger.error(f"Error al intentar resync de la ONU {onu_username}: {ex}")
            
            continue

        if connection_status_text == 'connected':
            log_connection_success(onu_username,onu_url)
            logger.info(f"CONEXION EXITOSA {onu_username}")
        else:
            if step <= 3:
                check_again_onu_list.append(onu_data)
            else:
                # Hacer resync
                try:
                    resync_onu_config(driver, timeout=60)
                    logger.info(f"ONU {onu_username} Resync exitoso")
                except Exception as ex:
                    logger.error(f"Error al intentar resync de la ONU {onu_username}: {ex}")

                log_connection_fail(onu_username, "ONU PPP Status Disconnected", onu_url)
                logger.error(f"ERROR {onu_username}: ONU PPP Status Disconnected")

    if len(check_again_onu_list) > 0:
        start_connection_validation(driver, check_again_onu_list, step + 1)

    logger.info("---------------------------------------------------------")
    logger.info(f'Finalizado el step {step} de la validación de conexiones')
    logger.info("---------------------------------------------------------")

    

def open_tr069_section(driver):
    tr69_status_button_locator = (By.XPATH, "//button[@id='tr69_status_button']")
    if not safe_click(driver, tr69_status_button_locator):
        raise ElementException("No se pudo abrir la ventana Configure. Error al clicar en el botón Configure")
    return True

def open_ppp_interface_section(driver):
    ppp_interface_locator = (
        By.XPATH,
        "//div[@id='status_tr69']//div[@id='all_tr69_pannels']"
        "//div[contains(@class,'panel-heading') and contains(@data-groupname,'PPP Interface')]"
        )
    if not safe_click(driver, ppp_interface_locator):
        raise ElementException("No se pudo desplegar la sección PPP Interface. Error al clicar en el botón PPP Interface")
    return True

def check_connection_status(driver):
    connection_status_span_locator = (By.XPATH, "//td[normalize-space()='Connection status']/following-sibling::td//span")
    try:
        connection_status_span = wait_visible(driver, connection_status_span_locator,6)
        connection_status_text = connection_status_span.text.strip().lower()
    except Exception:
        raise ElementException("No se pudo obtener el estado de la conexión PPP")
    return connection_status_text
    
def reset_ppp_connection(driver, timeout=60):
    time.sleep(4)
    # 1) Localizador del combo "Reset connection"
    reset_select_locator = (By.XPATH,
        "//td[normalize-space()='Reset connection']/following-sibling::td//select"
    )
    # 2) Esperar y seleccionar "Yes"
    try:
        reset_select = wait_visible(driver, reset_select_locator)
        Select(reset_select).select_by_value("1")     # value="1" → Yes
    except Exception:
        raise ElementException("No se pudo seleccionar 'Yes' en Reset connection")

    # 3) Click en "Apply one change"
    apply_btn_locator = (By.ID, "applytr69changes")
    if not safe_click(driver, apply_btn_locator):
        raise ElementException("No se pudo hacer click en Apply one change")

    # 4) Modal de confirmación "OK" 2 veces el mismo boton
    for i in range(2):
        modal_ok_btn_locator = (By.XPATH,"//div[@class='messagebox_buttons']//button[@class='messagebox_button_done']")

        try:
            ok_btn = wait_visible(driver, modal_ok_btn_locator)
            driver.execute_script("arguments[0].scrollIntoView(true);", ok_btn)
            time.sleep(0.1)
            driver.execute_script("arguments[0].click();", ok_btn)  
        except Exception:
            raise ElementException("No apareció el modal o no se pudo confirmar Reset con OK")

        time.sleep(3)  # Para que se actualice la modal
    return True

def open_tr069_and_check_connectivity(driver, timeout=60):          
    # Abre la sección tr069Stat -> PPP Interface y devuelve 'connected', 'connecting', 'disconnected' o None.
    try:
        espected_connection_status = 'connected'
        open_tr069_section(driver)
        open_ppp_interface_section(driver)   

        connection_status_text = assert_real_function_result(check_connection_status, driver, espected_connection_status, msg.PPP_STATUS_ATTEMP_MSG)
        logger.info(f"Estado de la conexión PPP Interface: {connection_status_text}")
    except ElementException:
        raise
    except Exception:
        raise ElementException("Error inesperado al abrir la sección tr069 y PPP Interface Status")

    try:
        ppp_gateway_value = get_ppp_gateway(driver,False)
        if ppp_gateway_value:
            logger.info(f"PPP Gateway REAL obtenido: {ppp_gateway_value}")
            if ppp_gateway_value.strip().lower() != PPP_GATEWAY.strip().lower():
                try:
                    logger.warning(f"Gateway ({ppp_gateway_value}) no es el esperado ({PPP_GATEWAY}). Intentando resync")
                    resync_onu_config(driver)
                    logger.info(f"Resync exitoso")
                    return connection_status_text, True
                except Exception as ex:
                    raise
            else:
                logger.info(f"Gateway ({ppp_gateway_value}) es el esperado ({PPP_GATEWAY})")
        else:
            logger.info("Resultado None en PPP Gateway. Sigue el flujo normal")
    except ElementException:
        raise
    except Exception:
        raise ElementException("Error inesperado al obtener PPP Gateway")

    if connection_status_text != espected_connection_status:
        try:
            logger.info("Intentando Reset ppp connection. Flujo normal")
            reset_ppp_connection(driver)
        except ElementException:
            raise
        except Exception:
            raise ElementException("Error inesperado al intentar Reset ppp connection")
    
    return connection_status_text, False

