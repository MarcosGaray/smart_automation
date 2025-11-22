from driver_setup import start_driver
from smartolt.login import login_smartolt
from data import USER,PASSWORD


def main():
    driver = start_driver()

    print("Iniciando sesión...")
    login_smartolt(driver, USER, PASSWORD)
    print("Sesión iniciada correctamente.")

    input("Presiona ENTER para cerrar...")
    driver.quit()

if __name__ == "__main__":
    main()
