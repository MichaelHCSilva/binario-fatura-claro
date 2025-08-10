from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ContratoCard:
    def __init__(self, driver, card_element: WebElement):
        self.driver = driver
        self.card_element = card_element
        self.wait = WebDriverWait(self.driver, 10)

    def esta_encerrado(self) -> bool:
        """
        Verifica se o contrato está encerrado procurando pelo texto 'encerrado'
        no span específico.
        """
        try:
            # Espera até 2s para o span carregar (caso exista)
            span_inativo = WebDriverWait(self.card_element, 2).until(
                lambda el: el.find_element(By.CSS_SELECTOR, "span.contract__infos-inactive")
            )
            texto = span_inativo.text.strip().lower()
            if "encerrado" in texto:
                print("Verificação de 'Contrato encerrado': True")
                return True
            else:
                print(f"Span encontrado, mas texto diferente: '{texto}'")
                return False
        except:
            print("Verificação de 'Contrato encerrado': False")
            return False

    def clicar_selecionar(self) -> bool:
        """
        Tenta clicar no botão 'Selecionar' do contrato.
        """
        try:
            print("Contrato ativo encontrado. Tentando clicar em 'Selecionar'.")
            botao_selecionar = self.card_element.find_element(
                By.XPATH, ".//button[contains(text(), 'Selecionar')]"
            )
            self.wait.until(EC.element_to_be_clickable(botao_selecionar))
            self.driver.execute_script("arguments[0].click();", botao_selecionar)
            print("Botão 'Selecionar' clicado com sucesso.")
            return True
        except Exception as e:
            print(f"Erro ao clicar no botão 'Selecionar': {e}")
            return False
