from selenium.webdriver.common.by import By
from driver_setup import start_driver
from smartolt.login import login_smartolt
from smartolt.navigate import go_to_configured_tab, search_user, open_matching_result, go_back, go_to_configured_by_URL
from sheets.sheets_reader import load_debbuggin_check_connection_list
from sheets.sheets_writer import log_migration_success, log_fail, save_unprocessed,log_disconected_success, log_check_svlan_success
from utils.logger import get_logger
from smartolt.onu_actions import migrate_vlan
from data import USER, PASSWORD
from exceptions import ElementException,Disconnected_ONU_Exception,ConnectionValidationException
from smartolt.connectivity import start_connection_validation
import pdb

logger = get_logger(__name__)


def main():
    # 1. Cargar lista de ONUs para debbug
    try:
        onu_list = load_debbuggin_check_connection_list()
    except Exception as e:
        logger.error(f"No se pudo leer archivo de entrada: {e}")
        return

    if len(onu_list) == 0:
        logger.info("La lista de ONUs está vacía. Colocar nombres en sheets/input/onus.txt")
        return

    # INICIALIZAR no_procesados CON TODAS
    no_procesados = set(onu_list)  # <<< ✔ importante ✔

    logger.info("Cargando webdriver...")
    driver = start_driver()

    try:
        logger.info("Iniciando sesión...")
        login_smartolt(driver, USER, PASSWORD)
        logger.info("Sesión iniciada.")
    except Exception as e:
        logger.error(f"Error en login: {e}")
        driver.quit()
        save_unprocessed(list(no_procesados))
        return

    try:
        go_to_configured_tab(driver)
    except ElementException as elemExc:
        logger.warning(f"Abortando. {elemExc}")
        driver.quit()
        save_unprocessed(list(no_procesados))
        return
        

    # PROCESAR ONUs

    print('')
    print('---------------------------------------------------------')
    try:
        start_connection_validation(driver, onu_list)
    except ConnectionValidationException as e:
        logger.error(str(e))
    except Exception as e:
        logger.error(f"Error en validación de conexión: {e}")

    input("ENTER para cerrar...")
    driver.quit()


if __name__ == "__main__":
    main()
