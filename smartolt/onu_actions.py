from selenium.webdriver.common.by import By
from utils.helpers import wait_until, wait_visible, wait_clickable, find_in,wait_presence, wait_clickable, safe_click
from utils.logger import get_logger
from sheets.sheets_writer import log_success, log_fail, save_unprocessed
import pdb
from data import VLAN_MIGRATION_DICT
from exceptions import ElementException

logger = get_logger(__name__)

def reveal_pppoe_username(driver, timeout=8):
    # Buscar el botón que muestra el username
    possible_buttons = [
        (By.XPATH, "//a[contains(@class,'show_pppoe_username')]")
    ]

    clicked = False
    for sel in possible_buttons:
        try:
            if wait_clickable(driver, sel, timeout=2):
                driver.find_element(*sel).click()
                clicked = True
                break
        except Exception:
            continue

    # Buscar el span que contiene el username
    possible_spans = [
        (By.XPATH, "//span[contains(@class, 'pppoe_username') and not(contains(@class, 'hidden'))]")
    ]
    #pdb.set_trace()
    for span in possible_spans:
        try:
            username_field = wait_presence(driver, span, timeout=4)
            text = username_field.get_attribute("innerText").strip()
            if text:
                return text
        except Exception:
            continue

    logger.warning("No se pudo obtener PPPoE username con los selectores configurados.")
    return None


##ACCIONES/INTERACCIONES
# Obtiene el status de la ONU (online, disconnected, etc.)
def get_onu_status(driver, timeout=8):
    element_status = wait_visible(driver, (By.XPATH, "//dd[@id='onu_status_wrapper']"), timeout=timeout)
    return element_status.get_attribute("innerText").strip()


def open_configure_modal(driver, configure_locator = (By.XPATH, "//a[@href='#updateSpeedProfiles']"),timeout=8):
    if not safe_click(driver, configure_locator):
        raise ElementException("No se pudo abrir la ventana Configure.")
    return True



from selenium.common.exceptions import StaleElementReferenceException
def modal_closed(modal):
    try:
        if not modal.is_displayed():
            return True

        style = modal.get_attribute("style") or ""
        if "display: none" in style.lower():
            return True

    except StaleElementReferenceException:
        return True
    return False


def migrate_vlan(driver, onu, timeout=8):
    # 1) Verificar estado
    try:
        onu_status = get_onu_status(driver, timeout=timeout)    
        expected_status = 'Online'
    except Exception as ex:
        raise ElementException(f"Error al obtener el estado de la ONU")
    
    # 2) Abrir modal Configure
    try:
        open_configure_modal(driver)
    except Exception as ex:
        raise ElementException(f"Error al abrir la ventana modal de configuración")

    
    # 3) Esperar a que la modal esté presente y visible (manejar animación)
    # Intentamos detectar la modal visible (Bootstrap usa clase 'in' o 'show' según versión)
    modal_locators = [
        (By.XPATH, "//div[contains(@class,'modal') and @id='updateSpeedProfiles']"),
        (By.XPATH, "//div[contains(@class,'modal') and not(contains(@style,'display: none'))]"),
    ]

    modal = None
    for loc in modal_locators:
        try:
            modal = wait_visible(driver, loc, timeout=6)
            break
        except Exception:
            continue

    if modal is None:
        raise ElementException("No apareció la ventana modal de configuración (posible animación/carga).")

    # 4️⃣ Buscar el SELECT de VLAN
    select_locator = (By.XPATH, "//select[@id='extra_vlan_id']")
    try:
        select_el = wait_visible(driver, select_locator, timeout=6)
    except:
        log_fail(onu, "No se encontró el selector de VLAN.")
        logger.error("No se encontró el selector de VLAN.")
        return False
    
    # 5 Convertir a objeto Select de Selenium
    try:
        from selenium.webdriver.support.ui import Select
        select = Select(select_el)
    except:
        log_fail(onu, "Error creando objeto Select.")
        logger.error("Error creando objeto Select.")
        return False
    
    # 6) Leer la opción actualmente seleccionada por su texto (innerText)
    try:
        current_option = select.first_selected_option
        current_text = current_option.get_attribute("innerText").strip()
    except Exception:
        log_fail(onu, "No se pudo obtener la opción actualmente seleccionada.")
        logger.error("No se pudo leer la opción seleccionada del select.")
        return False

    logger.info(f"ONU {onu} - VLAN actual (texto): '{current_text}'")


    # 7) Verificar si la VLAN actual está en el mapa
    if current_text not in VLAN_MIGRATION_DICT.keys():
        log_fail(onu, f"VLAN actual '{current_text}' no está en el diccionario de migración.")
        logger.error(f"VLAN actual '{current_text}' no está en el diccionario de migración.")
        return False
    
    target_text = VLAN_MIGRATION_DICT[current_text]
    # 8) Si actual == target → ya migrada
    if current_text == target_text:
        logger.info(f"ONU {onu} ya estaba en target VLAN '{target_text}'.")
        log_success(onu)
        return True

    # 9) Buscar la opción cuyo texto coincida con target_text
    target_option = None
    for option in select.options:
        option_text = option.get_attribute("innerText").strip()
        if option_text == target_text:
            target_option = option
            break

    if target_option is None:
        log_fail(onu, f"Target VLAN '{target_text}' no encontrada entre las opciones.")
        logger.error(f"Target VLAN '{target_text}' no encontrada en select.")
        return False
    
    # 10) Seleccionar la opción target (select_by_value o select_by_visible_text)
    try:
        # preferimos seleccionar por visible text si coincide exactamente:
        try:
            select.select_by_visible_text(target_text)
        except Exception:
            # fallback: seleccionar por value del option encontrado
            value = target_option.get_attribute("value")
            select.select_by_value(value)
    except Exception as ex:
        log_fail(onu, f"No se pudo seleccionar la VLAN target '{target_text}': {ex}")
        logger.error(f"No se pudo seleccionar la VLAN target '{target_text}': {ex}")
        return False

    logger.info(f"ONU {onu} - Seleccionada VLAN target '{target_text}'")

    # 11) Click en Save y esperar confirmación (si corresponde)
    save_locator = (By.XPATH, "//a[@id='submitUpdateSpeedProfiles' or contains(@class,'submitUpdateSpeedProfiles') or normalize-space(.)='Save']")
    if not safe_click(driver, save_locator, timeout=6):
        log_fail(onu, "No se pudo hacer click en Save.")
        logger.error("No se pudo hacer click en Save.")
        return False

    # 12) Opcional: esperar a que la modal se cierre / que termine la operación
    # Esperar a que la modal desaparezca
    #CONTINUAR AQUI, NO FUNCIONA
    wait_until(driver, modal_closed, timeout=10)
    
    logger.info(f"ONU {onu} VLAN migrada correctamente: {current_text} -> {target_text}")
    log_success(onu)
    input("LLegamos hasta el final")
    return True

# TODO: agregar migrate_vlan(driver), reboot_onu(driver), etc. cuando tengamos los selectores exactos.
