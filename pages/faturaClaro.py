# faturaPage.py
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)
from pages.contractClaro import ContratoCard
from typing import Callable, Any

logger = logging.getLogger(__name__)

class FaturaPage:
    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
    
    def _aguardar_renderizacao_contratos(self):
        logger.info("Aguardando renderização completa dos contratos...")
        
        try:
            self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "contract"))
            )
            self.wait.until(
                lambda d: all(el.is_displayed() for el in d.find_elements(By.CLASS_NAME, "contract"))
            )
            logger.info("Todos os contratos estão visíveis e carregados.")
        except TimeoutException:
            logger.warning("Timeout ao esperar pelos contratos. A página pode estar vazia.")
            raise

    def _avancar_para_proxima_pagina(self) -> bool:
        try:
            next_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    '.mdn-Pagination-Link.mdn-Pagination-Link--next:not([disabled="disabled"])'
                ))
            )
            self.driver.execute_script("arguments[0].click();", next_button)
            self.wait.until(EC.staleness_of(next_button))
            self._aguardar_renderizacao_contratos()
            return True
        except TimeoutException:
            logger.info("Botão de próxima página não encontrado ou desabilitado.")
            return False

    def _voltar_para_pagina_contratos(self, contratos_url: str):
        try:
            self.driver.back()
            self._aguardar_renderizacao_contratos()
            logger.info("Retorno à página de contratos via 'driver.back()' bem-sucedido.")
        except (TimeoutException, Exception):
            logger.warning("Falha ao usar 'driver.back()'. Tentando retorno completo via URL...")
            self.driver.get(contratos_url)
            self._aguardar_renderizacao_contratos()
            logger.info("Retorno à página de contratos via URL bem-sucedido.")

    def processar_todos_contratos_ativos(self, callback_processamento: Callable[[str], Any], contratos_url: str):

        pagina_atual = 1
        
        while True:
            logger.info(f"Processando contratos na página {pagina_atual}...")
            
            try:
                self._aguardar_renderizacao_contratos()
            except TimeoutException:
                logger.warning(f"Timeout ao carregar a página {pagina_atual}. O processo pode ter terminado ou a página está vazia.")
                if not self._avancar_para_proxima_pagina():
                    break
                else:
                    continue

            contratos_elements = self.driver.find_elements(By.CLASS_NAME, "contract")
            
            for i in range(len(contratos_elements)):
                try:
                    contrato_element = self.driver.find_elements(By.CLASS_NAME, "contract")[i]
                    card = ContratoCard(self.driver, contrato_element)

                    if card.esta_encerrado():
                        logger.info(f"Contrato {card.obter_numero_contrato()} está encerrado, pulando.")
                        continue
                    
                    logger.info(f"Processando contrato {i+1} da página {pagina_atual}: {card.obter_numero_contrato()}")
                    
                    if card.clicar_selecionar():
                        logger.info(f"Contrato {card.obter_numero_contrato()} selecionado. Prosseguindo para download.")
                        callback_processamento(card.obter_numero_contrato())
                        
                        self._voltar_para_pagina_contratos(contratos_url)
                        
                        for _ in range(pagina_atual - 1):
                            self._avancar_para_proxima_pagina()
                
                except Exception as e:
                    logger.error(f"Falha ao processar um contrato. Tentando continuar o processo. Erro: {e}", exc_info=True)
                    try:
                        self._voltar_para_pagina_contratos(contratos_url)
                        for _ in range(pagina_atual - 1):
                            self._avancar_para_proxima_pagina()
                    except Exception as fallback_e:
                        logger.error(f"Falha na tentativa de recuperação. O processo será interrompido: {fallback_e}")
                        return
            
            if not self._avancar_para_proxima_pagina():
                logger.info("Não há mais páginas. Processamento concluído.")
                break
            
            pagina_atual += 1