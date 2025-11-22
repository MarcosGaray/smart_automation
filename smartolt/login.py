import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from data import URL

def login_smartolt(driver, user, password):

    driver.get(URL)

    user_input = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="identity"]'))
    )
    pass_input = driver.find_element(By.XPATH, '//*[@id="password"]')

    user_input.send_keys(user)
    pass_input.send_keys(password)

    login_button = driver.find_element(
        By.XPATH,
        '/html/body/div/div/div/div/div[2]/form/fieldset/input'
    )
    login_button.click()

    time.sleep(2)
