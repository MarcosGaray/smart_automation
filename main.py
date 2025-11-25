# main.py
from driver_setup import start_driver
from smartolt.login import login_smartolt
from smartolt.navigate import go_to_configured_tab, search_user, open_matching_result
from sheets.sheets_reader import load_onu_list
from sheets.sheets_writer import log_success, log_fail, save_unprocessed
from utils.logger import get_logger
from utils.helpers import wait_visible
from data import USER, PASSWORD, INPUT_ONUS_FILE

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

    if not go_to_configured_tab(driver):
        logger.warning("No se pudo acceder a Configured. Abortando.")
        driver.quit()
        save_unprocessed(list(no_procesados))
        return

    # PROCESAR ONUs
    for onu in onu_list:
        logger.info(f"Procesando {onu} ...")
        try:
            search_user(driver, onu)
            
            matched = open_matching_result(driver, onu)

            if matched:
                log_success(onu)
                no_procesados.discard(onu)  # <<< ✔ quitar procesado
                logger.info(f"ÉXITO: {onu}")
            else:
                log_fail(onu, "Sin coincidencia exacta")
                logger.warning(f"FALLO: {onu}")

        except Exception as e:
            log_fail(onu, f"Error inesperado: {e}")
            logger.error(f"ERROR {onu}: {e}")

    # EXPORTAR RESTANTES SIEMPRE
    save_unprocessed(list(no_procesados))
    logger.info("Proceso finalizado. Archivo sheets/output/no_procesados.csv creado.")

    input("ENTER para cerrar...")
    driver.quit()


if __name__ == "__main__":
    main()
