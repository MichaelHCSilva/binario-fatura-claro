import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)
from pages.contractClaro import ContratoCard
import time

logger = logging.getLogger(__name__)

class FaturaPage:
    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _aguardar_renderizacao_contratos(self):
        """
        Aguarda até que todos os contratos estejam visíveis e tenham texto não vazio.
        """
        logger.info("Aguardando renderização completa dos contratos...")

        def contratos_visiveis_e_renderizados(driver):
            contratos = driver.find_elements(By.CLASS_NAME, "contract")
            if not contratos:
                return False

            for el in contratos:
                if not el.is_displayed() or not el.text.strip():
                    return False
            return True

        self.wait.until(contratos_visiveis_e_renderizados)
        logger.info("Todos os contratos estão visíveis e com texto carregado.")

    def _tratar_popup_cookies(self):
        """
        Trata o popup de consentimento de cookies da OneTrust.
        """
        logger.info("Verificando a presença do popup de cookies...")
        try:
            accept_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            accept_button.click()
            logger.info("Popup de cookies aceito com sucesso.")
            time.sleep(2)
        except (TimeoutException, ElementClickInterceptedException, NoSuchElementException):
            logger.info("Popup de cookies não foi encontrado ou não precisa ser tratado.")

    def processar_todos_contratos_ativos(self, callback_processamento):
        try:
            logger.info("Iniciando o processamento dos contratos por página...")

            self._tratar_popup_cookies()

            pagina_atual = 1
            while True:
                logger.info(f"Processando a página {pagina_atual}...")

                # Espera os contratos carregarem
                self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "contract")))
                self._aguardar_renderizacao_contratos()

                contratos_elements = self.driver.find_elements(By.CLASS_NAME, "contract")
                total_contratos = len(contratos_elements)

                for i in range(total_contratos):
                    contratos_elements = self.driver.find_elements(By.CLASS_NAME, "contract")
                    contrato_element = contratos_elements[i]
                    card = ContratoCard(self.driver, contrato_element)

                    if card.esta_encerrado():
                        logger.info(f"Contrato {i+1} da página {pagina_atual} está encerrado. Pulando...")
                        continue

                    numero_contrato = card.obter_numero_contrato()
                    logger.info(f"Contrato {i+1} da página {pagina_atual} é ativo ({numero_contrato}).")

                    if card.clicar_selecionar():
                        logger.info(f"Contrato {numero_contrato} selecionado com sucesso. Processando...")
                        callback_processamento(numero_contrato)

                        self.driver.back()

                        # Espera os contratos recarregarem após o back()
                        self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "contract")))
                        self._aguardar_renderizacao_contratos()

                        # Garante que ainda está na página certa da paginação
                        try:
                            link_pagina_atual = self.wait.until(
                                EC.element_to_be_clickable((
                                    By.XPATH,
                                    f"//a[contains(@class, 'mdn-Pagination-Link') and normalize-space()='{pagina_atual}']"
                                ))
                            )
                            link_pagina_atual.click()
                            self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "contract")))
                            self._aguardar_renderizacao_contratos()
                            logger.info(f"Retornou com sucesso para a página {pagina_atual}.")
                        except TimeoutException:
                            logger.warning("Não foi possível clicar no link da página atual. Pode haver um erro na navegação.")

                # Paginação - avançar para próxima página se existir
                try:
                    link_proxima_pagina = self.wait.until(
                        EC.element_to_be_clickable((
                            By.CSS_SELECTOR,
                            '.mdn-Pagination-Link.mdn-Pagination-Link--next:not([disabled="disabled"])'
                        ))
                    )

                    logger.info("Avançando para a próxima página...")
                    link_proxima_pagina.click()
                    pagina_atual += 1

                    self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "contract")))
                    self._aguardar_renderizacao_contratos()

                except TimeoutException:
                    logger.info("Não há mais páginas. Todos os contratos ativos foram processados.")
                    break

        except Exception as e:
            logger.error(f"Erro ao processar contratos: {e}", exc_info=True)
