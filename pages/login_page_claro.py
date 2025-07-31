from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


class LoginPage:
    URL = "https://minhaclaro.claro.com.br/acesso-rapido/"

    def __init__(self, driver, timeout=25):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_login_page(self):
        print("🔄 Abrindo página de login...")
        self.driver.get(self.URL)
        self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

    def click_entrar(self):
        try:
            xpath = "//button[contains(@class, 'mdn-Button--primaryInverse') and .//span[text()='Entrar']]"
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            self.driver.execute_script("arguments[0].click();", btn)

            print("✅ Botão 'Entrar' clicado com sucesso.")
            # Aguarda próximo elemento da página
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//p[text()='Minha Claro Residencial']")))

        except Exception as e:
            print(f"❌ Erro ao clicar no botão 'Entrar': {e}")

    def selecionar_minha_claro_residencial(self):
        try:
            print("🔍 Procurando opção 'Minha Claro Residencial'...")
            xpath = "//a[contains(@class, 'mdn-Shortcut') and .//p[text()='Minha Claro Residencial']]"
            link = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

            self.driver.execute_script("arguments[0].scrollIntoView(true);", link)
            self.driver.execute_script("arguments[0].click();", link)

            print("✅ Opção 'Minha Claro Residencial' selecionada.")
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="cpfCnpj"]')))

        except Exception as e:
            print(f"❌ Erro ao selecionar 'Minha Claro Residencial': {e}")

    def preencher_login_usuario(self):
        try:
            usuario = os.getenv("LOGIN_USUARIO")
            if not usuario:
                raise Exception("LOGIN_USUARIO não encontrado no .env")

            print(f"⌨️ Preenchendo login com CNPJ: {usuario}")
            campo = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[data-testid="cpfCnpj"]')))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", campo)
            campo.clear()
            campo.send_keys(usuario)

        except Exception as e:
            print(f"❌ Erro ao preencher o campo de login: {e}")

    def clicar_continuar(self):
        try:
            print("🟢 Clicando no botão 'Continuar'...")
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='continuar']")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            self.driver.execute_script("arguments[0].click();", btn)
            print("✅ Botão 'Continuar' clicado.")
            self.wait.until(EC.visibility_of_element_located((By.ID, "password")))

        except Exception as e:
            print(f"❌ Erro ao clicar no botão 'Continuar': {e}")

    def preencher_senha(self):
        try:
            senha = os.getenv("LOGIN_SENHA")
            if not senha:
                raise Exception("LOGIN_SENHA não encontrada no .env")

            print("🔐 Preenchendo senha...")
            campo_senha = self.wait.until(EC.visibility_of_element_located((By.ID, "password")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", campo_senha)
            campo_senha.send_keys(senha)

        except Exception as e:
            print(f"❌ Erro ao preencher a senha: {e}")

    def clicar_botao_acessar(self):
        try:
            print("🔓 Clicando no botão 'Acessar'...")
            botao_acessar = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='acessar']")))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", botao_acessar)
            self.driver.execute_script("arguments[0].click();", botao_acessar)
            print("✅ Botão 'Acessar' clicado com sucesso.")
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        except Exception as e:
            print(f"❌ Erro ao clicar no botão 'Acessar': {e}")
