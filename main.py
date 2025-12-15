from selenium.webdriver.common.by import By
from driver_setup import start_driver
from smartolt.login import login_smartolt
from smartolt.navigate import go_to_configured_tab, search_user, open_matching_result, go_back, go_to_configured_by_URL
from sheets.sheets_reader import load_onu_list
from sheets.sheets_writer import log_migration_success, log_fail, log_disconected_success, log_check_svlan_success, backup_success_block,create_not_processed_temp, remove_from_not_processed_temp,rename_not_processed_temp,log_check_attached_vlans
from utils.logger import get_logger
from smartolt.onu_actions import migrate_vlan
from data import USER, PASSWORD, INPUT_ONUS_FILE
import pdb
from exceptions import ElementException,Disconnected_ONU_Exception,ConnectionValidationException, AttachedVlansException
from smartolt.connectivity import start_connection_validation

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
    create_not_processed_temp(onu_list)

    logger.info("Cargando webdriver...")
    driver = start_driver(True)

    try:
        logger.info("Iniciando sesión...")
        login_smartolt(driver, USER, PASSWORD)
        logger.info("Sesión iniciada.")
    except Exception as e:
        logger.error(f"Error en login: {e}")
        rename_not_processed_temp()
        driver.quit()
        return

    try:
        go_to_configured_tab(driver)
    except ElementException as e:
        logger.warning(f"Abortando. {e}")
        rename_not_processed_temp()
        driver.quit()
        return
        
    success_account = 0
    MAX_ONUS_ACCOUNT = 20
    block_number = 1   # <<< CONTADOR DE BLOQUES DE BACKUP

    # PROCESAR ONUs
    for onu in onu_list:        
        logger.info('')
        logger.info('---------------------------------------------------------')

        logger.info(f"Procesando {onu} ...")
        try:
            search_user(driver, onu)
            
            matched = open_matching_result(driver, onu)

            if matched:
                migrated, is_online, use_svlan, attached_vlans_list, deactivated_vlan = migrate_vlan(driver, onu)

                if use_svlan: 
                    svlan_status = "desactivada" if deactivated_vlan else "activada"
                    log_check_svlan_success(onu,svlan_status)
                    logger.warning("La ONU posee SVLAN. Status: " + svlan_status)
                else:
                    logger.info("La ONU no posee SVLAN.")
                
                vlans = ",".join(attached_vlans_list)

                if len(attached_vlans_list) > 1:
                    raise AttachedVlansException(f"{onu} tiene {len(attached_vlans_list)} VLANs asociadas ({vlans}). Revisar a mano. No se procesa")
                
                logger.info(f'"{onu}" - Migrated: {migrated} - Is Online: {is_online} - Usa SVLAN: {use_svlan} - SVLAN desactivada: {deactivated_vlan}')
                if migrated:
                        
                    current_onu_url = driver.current_url
                    if is_online:
                        log_migration_success(onu,current_onu_url)
                        logger.info(f"ÉXITO: {onu}. Lista para checkear conectividad")
                        success_account += 1

                        # <<< CHECKEO DE CONECTIVIDAD POR BLOQUES
                        if success_account >= MAX_ONUS_ACCOUNT:
                            block_number = excecute_connection_validation_block(driver, block_number)
                            success_account = 0
                        else:
                            logger.info(f"Faltan {MAX_ONUS_ACCOUNT - success_account} ONUs para iniciar checkeo de conectividad")
                    else:
                        log_disconected_success(onu, "ONU Offline")
                        logger.info(f"ÉXITO: {onu}. La ONU no se encuentra Online. Reboot innecesario. Migración Exitosa!")
                else:
                    log_fail(onu, "Fallo en la migración")
                    logger.warning(f"FALLO: {onu}")
            else:
                log_fail(onu, "Sin coincidencia exacta en resultados del SMARTOLT")
                logger.warning(f"FALLO: {onu}")
        except AttachedVlansException as exception_msg:
            log_check_attached_vlans(onu,exception_msg)
            logger.warning(exception_msg)
        except Exception as e:
            short_msg = getattr(e, "msg", str(e)).split("\n")[0].strip()
            log_fail(onu, f"{short_msg}")
            logger.error(f"ERROR {onu}: {short_msg}")
            #En el caso de que se registra como failure, se mantiene como no_procesado
        finally:
            remove_from_not_processed_temp(onu)
        
        try:
            go_to_configured_by_URL(driver)
        except Exception as e:
            logger.error(f"No se pudo volver a Configured: {e}")
            break

    
    logger.info('---------------------------------------------------------')
    logger.info("Se finaliza procesamiento. Se checkean las ONUs restantes si es que quedan")

    # CHECKEO FINAL SI QUEDARON <20 PENDIENTES
    if success_account > 0:
        logger.info(f"Faltan {MAX_ONUS_ACCOUNT - success_account} ONUs para procesar. Comenzando...")
        block_number = excecute_connection_validation_block(driver, block_number)

    # EXPORTAR RESTANTES SIEMPRE
    rename_not_processed_temp()
    logger.info("Proceso finalizado. Archivo sheets/output/no_procesados.csv creado.")

    input("ENTER para cerrar...")
    driver.quit()


def excecute_connection_validation_block(driver, block_number):
    logger.info('')
    logger.info('---------------------------------------------------------')
    
    #Excepciones manejadas internamente
    try:
        start_connection_validation(driver)
        # Si todo va bien, se debe crearse una subcarpeta en output llamada "processed-blocks-backup" y copiar los renglones de migration-success.csv en un nuevo archivo "migration-success-block-{numero_de_bloque}.csv"

        if backup_success_block(block_number):
            logger.info(f"Backup creado: migration-success-block-{block_number}.csv")
        else:
            logger.warning("No se pudo crear backup: migration-success.csv no existe")

        return block_number + 1 
    
    except ConnectionValidationException as e:
        logger.error(str(e))
    except Exception as e:
        logger.error(f"Error inesperado en la validación de conexión: {e}")
    
    return block_number

if __name__ == "__main__":
    main()
