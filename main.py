from selenium.webdriver.common.by import By
from driver_setup import start_driver
from smartolt.login import login_smartolt
from smartolt.navigate import go_to_configured_tab, search_user, open_matching_result, go_back, go_to_configured_by_URL
from sheets.sheets_reader import load_onu_list
from sheets.sheets_writer import log_success, log_fail, save_unprocessed
from utils.logger import get_logger
from smartolt.onu_actions import migrate_vlan
from data import USER, PASSWORD, INPUT_ONUS_FILE
import pdb
from exceptions import ElementException

logger = get_logger(__name__)


def main():
    # 1. Cargar lista de ONUs
    try:
        onu_list = load_onu_list(INPUT_ONUS_FILE)
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
    for onu in onu_list:
        print('')
        print('---------------------------------------------------------')
        logger.info(f"Procesando {onu} ...")
        try:
            search_user(driver, onu)
            
            matched = open_matching_result(driver, onu)

            if matched:
                migrated = migrate_vlan(driver, onu)
                if migrated:
                    log_success(onu)
                    no_procesados.discard(onu)  # <<< ✔ quitar procesado
                    logger.info(f"ÉXITO: {onu}")
                else:
                    log_fail(onu, "Fallo en la migración")
                    logger.warning(f"FALLO: {onu}")
                
                #go_back(driver)
                #pdb.set_trace()
            else:
                log_fail(onu, "Sin coincidencia exacta")
                logger.warning(f"FALLO: {onu}")

        except Exception as e:
            short_msg = getattr(e, "msg", str(e)).split("\n")[0].strip()
            log_fail(onu, f"{short_msg}")
            logger.error(f"ERROR {onu}: {e}")
        
        try:
            go_to_configured_by_URL(driver)
        except Exception as e:
            logger.error(f"No se pudo volver a Configured: {e}")
            break

    # EXPORTAR RESTANTES SIEMPRE
    save_unprocessed(list(no_procesados))
    logger.info("Proceso finalizado. Archivo sheets/output/no_procesados.csv creado.")

    input("ENTER para cerrar...")
    driver.quit()


if __name__ == "__main__":
    main()
