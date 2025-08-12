#faturaClaro
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pages.contractClaro import ContratoCard

logger = logging.getLogger(__name__)

class FaturaPage:
    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _aguardar_renderizacao_contratos(self):
        """
        Aguarda até que todos os contratos tenham texto visível.
        """
        logger.info("Aguardando renderização completa dos contratos...")
        self.wait.until(
            lambda d: all(
                el.text.strip() != ""
                for el in d.find_elements(By.CLASS_NAME, "contract")
            )
        )
        logger.info("Todos os contratos possuem texto carregado.")

    def processar_todos_contratos_ativos(self, callback_processamento):
        try:
            logger.info("Aguardando a página de contratos carregar...")

            while True:
                contratos_elements = self.wait.until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "contract"))
                )
                self._aguardar_renderizacao_contratos()

                encontrou_ativo = False
                total_contratos = len(contratos_elements)

                for i in range(total_contratos):
                    # Recarrega a lista sempre que voltar para esta página
                    contratos_elements = self.wait.until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "contract"))
                    )
                    self._aguardar_renderizacao_contratos()

                    contrato_element = contratos_elements[i]
                    card = ContratoCard(self.driver, contrato_element)

                    if card.esta_encerrado():
                        logger.info(f"Contrato {i+1} encerrado. Pulando...")
                        continue

                    numero_contrato = card.obter_numero_contrato()
                    logger.info(f"Contrato {i+1} é ativo ({numero_contrato}).")

                    if card.clicar_selecionar():
                        logger.info(f"Contrato {numero_contrato} selecionado com sucesso.")
                        callback_processamento(numero_contrato)
                        self.driver.back()
                        encontrou_ativo = True

                if  not encontrou_ativo:
                    logger.info("Nenhum contrato ativo encontrado. Encerrando busca.")
                    break

        except Exception as e:
            logger.error(f"Erro ao processar contratos: {e}", exc_info=True)
