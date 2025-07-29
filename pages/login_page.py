from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class LoginPage:
    URL = "https://minhaclaro.claro.com.br/acesso-rapido/"

    def __init__(self, driver, timeout=25):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_login_page(self):
        print("🔄 Abrindo página de login...")
        self.driver.get(self.URL)
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(3)

    def click_entrar(self):
        try:
            xpath = "//button[contains(@class, 'mdn-Button--primaryInverse') and .//span[text()='Entrar']]"
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            self.driver.execute_script("arguments[0].click();", btn)

            print("✅ Botão 'Entrar' clicado com sucesso.")
            time.sleep(5)

        except Exception as e:
            print(f"❌ Erro ao clicar no botão 'Entrar': {e}")
