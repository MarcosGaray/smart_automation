from driver_setup import start_driver
from smartolt.login import login_smartolt
from smartolt.navigate import go_to_configured_tab, search_user, open_first_result
from data import USER,PASSWORD,ONU_PRUEBA


def main():
    driver = start_driver()

    print("Iniciando sesión...")
    login_smartolt(driver, USER, PASSWORD)
    print("Sesión iniciada correctamente.")

    print("Moviéndose a Configured...")
    go_to_configured_tab(driver)

    print("Buscando usuario de prueba...")
    search_user(driver, ONU_PRUEBA)  # Cambiar por un test

    print("Abriendo primer resultado...")
    open_first_result(driver)


    input("Presiona ENTER para cerrar...")
    driver.quit()

if __name__ == "__main__":
    main()
