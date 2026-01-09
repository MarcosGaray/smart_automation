from selenium.webdriver.common.by import By
from smartolt.onu_functions import alternate_svlan_checkbox, check_svlan_id, get_attached_vlans, get_configuration_modal, get_onu_mode_modal, get_onu_status, get_select_element, get_select_target_option, get_selenium_select_element, get_selenium_select_innerText, is_speed_in_speed_profile_dictionary, is_vlan_in_migration_dictionary, open_configure_modal, open_onu_mode_modal, reveal_pppoe_username, save_and_close_configuration_modal, update_and_close_onu_mode_modal
from utils.helpers import assert_real_function_result
from utils.locators import DOWNSTREAM_SPEED_SELECT_LOCATOR, UPSTREAM_SPEED_SELECT_LOCATOR, VLAN_SELECT_LOCATOR
from utils.logger import get_logger
from data import SPEEDS_PROFILE_DICT, VLAN_MIGRATION_DICT, RECHECK
from exceptions import ElementException
from utils import words_and_messages as msg
import time

logger = get_logger(__name__)

def migrate_vlan(driver, onu, timeout=70):
    # Supuesto: ESTAMOS EN LA PAGINA DE CONFIGURACIÓN DE LA ONU

    # 0) Verificar si tiene attached VLANs
    try:
        attached_vlans = get_attached_vlans(driver)
    except ElementException:
        raise
    except Exception:
        raise ElementException("Error detectando si la ONU tiene attached VLANs")

    # 1) Abrir modal de configuración
    try:
        open_configure_modal(driver)
        config_modal = get_configuration_modal(driver)
    except ElementException as ex:
        raise


    # 2) Buscar el SELECT de VLAN
    # 3) Convertir a objeto Select de Selenium
    # 4) Leer la opción actualmente seleccionada por su texto (innerText)
    try:
        select_element = get_select_element(driver,VLAN_SELECT_LOCATOR, timeout=6)
        selenium_select = get_selenium_select_element(select_element)
        current_selected_vlan_text = get_selenium_select_innerText(selenium_select)
    except ElementException:
        raise
    

    # 5) Checkear si tiene SVLAN-ID
    try:
        use_svlan = check_svlan_id(driver) # True si tiene SVLAN-ID
        deactivated_vlan = False
    except ElementException:
        raise
    except Exception:
        raise ElementException("Error inesperado detectando si la ONU usa SVLAN-ID")
    
    # 6) Si tiene attached VLANs → no se puede migrar
    if len(attached_vlans) > 1:
        return False, False, use_svlan, attached_vlans, deactivated_vlan


    logger.info(f"ONU {onu} - VLAN actual (texto): '{current_selected_vlan_text}'")

    # 7) Verificar si la VLAN actual está en el diccionario
    if not is_vlan_in_migration_dictionary(current_selected_vlan_text):
        raise ElementException(f"VLAN actual '{current_selected_vlan_text}' no está en el diccionario de migración")

    target_vlan_text = VLAN_MIGRATION_DICT[current_selected_vlan_text]
        

    # 8) Revisar el estado de la ONU
    expected_onu_status = 'Online'
    is_online = True
    try:
        onu_status = assert_real_function_result(get_onu_status,driver, expected_onu_status, msg.ONU_STATUS_ATTEMP_MSG)   
    except Exception as ex:
        raise ElementException(f"Error al obtener el estado de la ONU")

    if not onu_status.__contains__(expected_onu_status):
        is_online = False

    #9) si tiene SVLAN, desactivar
    try:
        if use_svlan:
            alternate_svlan_checkbox(driver)
            deactivated_vlan = True
            logger.info(f"{onu} - SVLAN desactivada")
    except ElementException:
        raise
    except Exception:
        raise ElementException("Error inesperado al alternar el checkbox de SVLAN")

    # 10) Si vlan_actual == vlan_target → ya está migrada. Recheck indica que se quiere verificar que la ONU se haya migrado correctamente
    if current_selected_vlan_text == target_vlan_text:
        if not RECHECK:
            logger.info(f"ONU {onu} ya estaba en target VLAN '{target_vlan_text}'")
            try:
                save_and_close_configuration_modal(driver,config_modal)
            except ElementException as ex:
                raise
            except Exception as ex:
                raise ElementException(f"Error inesperado al cerrar la ventana modal de configuración")

            return True,is_online, use_svlan, attached_vlans, deactivated_vlan

    # 11) Buscar la opción cuyo texto coincida con target_text y seleccionar
    if not RECHECK:
        try:
            vlan_target_option = get_select_target_option(selenium_select, target_vlan_text)
            try:
                # seleccionar por visible text si coincide exactamente:
                selenium_select.select_by_visible_text(target_vlan_text)
            except Exception:
                # fallback: seleccionar por value del option encontrado
                value = vlan_target_option.get_attribute("value")
                selenium_select.select_by_value(value)
        except ElementException as ex:
            raise
        except Exception as ex:
            raise ElementException(f"No se pudo seleccionar la VLAN target '{target_vlan_text}': {ex}")


    logger.info(f"ONU {onu} - VLAN target seleccionada '{target_vlan_text}'")

    # 12) Click en Save y esperar confirmación (si corresponde)
    try:
        save_and_close_configuration_modal(driver,config_modal)
    except ElementException as ex:
        raise
    except Exception as ex:
        raise ElementException(f"Error inesperado al cerrar la ventana modal de configuración")

    # 13) Abrir modal de ONU mode y Click en Update
    try:
        open_onu_mode_modal(driver)
        onu_mode_modal = get_onu_mode_modal(driver)
        update_and_close_onu_mode_modal(driver,onu_mode_modal)
    except ElementException as ex:
        raise
    except Exception as ex:
        raise ElementException(f"Error inesperado al cerrar la ventana modal de ONU mode")


    """ # 13) Determinar si hacer resync o no
    if is_online:
        # Hacer resync
        try:
            resync_onu_config(driver)
            logger.info(f"ONU {onu} Resync exitoso")
        except Exception as ex:
            raise
        
        # Hacer Reboot
        try:
            reboot_onu(driver, timeout=8)
            logger.info(f"ONU {onu} Reboot Exitoso")
        except Exception as ex:
            raise """

    logger.info("---------------------------------------------")
    logger.info(f"ONU {onu} VLAN migrada correctamente: {current_selected_vlan_text} -> {target_vlan_text}")
    logger.info("---------------------------------------------")

    return True, is_online ,use_svlan, attached_vlans, deactivated_vlan

def change_speed_profile(driver,username,timeout=70):
    # Supuesto: ESTAMOS EN LA PAGINA DE CONFIGURACIÓN DE LA ONU
        
    # 1) Abrir modal de configuración
    try:
        open_configure_modal(driver)
        config_modal = get_configuration_modal(driver)
    except ElementException as ex:
        raise

    logger.info("PROCESANDO DOWNSTREAM...")

    # 2) OBTENER DOWNSTREAM SPEED ACTUAL 
    try:
        """ import pdb
        pdb.set_trace() """
        select_element = get_select_element(driver, DOWNSTREAM_SPEED_SELECT_LOCATOR, timeout=6)
        selenium_select = get_selenium_select_element(select_element)
        current_selected_downstream_text = get_selenium_select_innerText(selenium_select)
    except ElementException:
        raise

    logger.info(f"ONU {username} - downstream actual: '{current_selected_downstream_text}'")

    # 3) Verificar si la speed actual está en el diccionario
    if not is_speed_in_speed_profile_dictionary(current_selected_downstream_text):
        raise ElementException(f"Speed actual '{current_selected_downstream_text}' no está en el diccionario de Speed profiles")

    target_downstream_speed_text = SPEEDS_PROFILE_DICT[current_selected_downstream_text]
        

    # 4) Si speed_actual == target_downspeed_text → ya está migrada. 
    if current_selected_downstream_text == target_downstream_speed_text:
        logger.info(f"ONU {username} ya estaba en downstream speed target '{target_downstream_speed_text}'")
    else:
        try:
            downstream_target_option = get_select_target_option(selenium_select, target_downstream_speed_text)
            try:
                selenium_select.select_by_visible_text(target_downstream_speed_text)
            except Exception:
                value = downstream_target_option.get_attribute("value")
                selenium_select.select_by_value(value)
        except ElementException as ex:
            raise
        except Exception as ex:
            raise ElementException(f"No se pudo seleccionar la velocidad downstream target '{target_downstream_speed_text}': {ex}")


        logger.info(f"ONU {username} - downstream speed target seleccionada '{target_downstream_speed_text}'")

    logger.info("PROCESANDO UPSTREAM...")
    # 5) OBTENER UPSTREAM SPEED ACTUAL 
    try:
        select_element = get_select_element(driver, UPSTREAM_SPEED_SELECT_LOCATOR, timeout=6)
        selenium_select = get_selenium_select_element(select_element)
        current_selected_upstream_text = get_selenium_select_innerText(selenium_select)
    except ElementException:
        raise


    logger.info(f"ONU {username} - upstream actual: '{current_selected_upstream_text}'")

    # 6) Verificar si la speed actual está en el diccionario
    if not is_speed_in_speed_profile_dictionary(current_selected_upstream_text):
        raise ElementException(f"Speed actual '{current_selected_upstream_text}' no está en el diccionario de Speed profiles")

    target_upstream_speed_text = SPEEDS_PROFILE_DICT[current_selected_upstream_text]
        

    # 7) Si speed_actual == target_upspeed_text → ya está migrada. 
    if current_selected_upstream_text == target_upstream_speed_text:
        logger.info(f"ONU {username} ya estaba en upstream speed target '{target_upstream_speed_text}'")
    else:
        try:
            upstream_target_option = get_select_target_option(selenium_select, target_upstream_speed_text)
            try:
                selenium_select.select_by_visible_text(target_upstream_speed_text)
            except Exception:
                value = upstream_target_option.get_attribute("value")
                selenium_select.select_by_value(value)
        except ElementException as ex:
            raise
        except Exception as ex:
            raise ElementException(f"No se pudo seleccionar la velocidad upstream target '{target_upstream_speed_text}': {ex}")


        logger.info(f"ONU {username} - upstream speed target seleccionada '{target_upstream_speed_text}'")
    

    # 8) Click en Save y esperar confirmación (si corresponde)
    try:
        save_and_close_configuration_modal(driver,config_modal)
    except ElementException as ex:
        raise
    except Exception as ex:
        raise ElementException(f"Error inesperado al cerrar la ventana modal de configuración")


    logger.info("---------------------------------------------")
    logger.info(f"ONU {username} speeds corregidos correctamente")
    logger.info("---------------------------------------------")

