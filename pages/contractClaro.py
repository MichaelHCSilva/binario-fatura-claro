#contractClaro.py
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class ContratoCard:
    def __init__(self, driver, card_element: WebElement):
        self.driver = driver
        self.card_element = card_element
        self.wait = WebDriverWait(self.driver, 10)

    def esta_encerrado(self) -> bool:
        """
        Verifica se o contrato está encerrado procurando pelo texto 'encerrado'.
        """
        try:
            span_inativo = WebDriverWait(self.card_element, 3).until(
                lambda el: el.find_element(By.CSS_SELECTOR, "span.contract__infos-inactive")
            )
            self.wait.until(lambda d: span_inativo.is_displayed() and span_inativo.text.strip() != "")
            texto = span_inativo.text.strip().lower()

            if "encerrado" in texto:
                logger.info("Contrato encerrado detectado.")
                return True

            logger.info(f"Contrato não encerrado. Texto: '{texto}'")
            return False
        except Exception:
            logger.info("Contrato ativo (span de encerrado não encontrado).")
            return False

    def clicar_selecionar(self) -> bool:
        """
        Clica no botão 'Selecionar' do contrato.
        """
        try:
            logger.info("Tentando clicar em 'Selecionar' no contrato.")
            botao_locator = (By.XPATH, ".//button[contains(text(), 'Selecionar')]")

            botao_selecionar = WebDriverWait(self.card_element, 5).until(
                EC.element_to_be_clickable(botao_locator)
            )

            self.driver.execute_script("arguments[0].click();", botao_selecionar)
            logger.info("Botão 'Selecionar' clicado com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro ao clicar no botão 'Selecionar': {e}", exc_info=True)
            return False

    def obter_numero_contrato(self) -> str:
        """
        Obtém o número do contrato exibido no card.
        Como o número está junto no texto, retiramos o texto do span 'encerrado'.
        """
        try:
            numero_div = self.card_element.find_element(By.CSS_SELECTOR, "div.mdn-Text.mdn-Text--body")
            
            span_inativo = None
            try:
                span_inativo = numero_div.find_element(By.CSS_SELECTOR, "span.contract__infos-inactive")
            except:
                pass
            
            texto_completo = numero_div.text.strip()
            
            if span_inativo:
                texto_span = span_inativo.text.strip()
                numero = texto_completo.replace(texto_span, "").strip()
            else:
                numero = texto_completo
            
            logger.info(f"Número do contrato encontrado: {numero}")
            return numero
        except Exception as e:
            logger.error(f"Não foi possível obter o número do contrato: {e}", exc_info=True)
            return "contrato_desconhecido"
