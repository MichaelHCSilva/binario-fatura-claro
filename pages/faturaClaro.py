import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException
)
from pages.contractClaro import ContratoCard
from typing import Callable, Any, List, Dict

logger = logging.getLogger(__name__)

class FaturaPage:
    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _aguardar_renderizacao_contratos(self):
        """Aguardar a renderização completa dos cards de contrato."""
        logger.info("Aguardando renderização completa dos contratos...")
        
        def contratos_visiveis_e_renderizados(driver):
            try:
                contratos = driver.find_elements(By.CLASS_NAME, "contract")
                if not contratos:
                    return False
                # Verifica se pelo menos um contrato está visível e tem texto
                return any(el.is_displayed() and el.text.strip() for el in contratos)
            except StaleElementReferenceException:
                return False

        try:
            self.wait.until(contratos_visiveis_e_renderizados)
            logger.info("Pelo menos um contrato está visível e carregado.")
        except TimeoutException:
            logger.warning("Timeout ao esperar pelos contratos. A página pode estar vazia.")
            return

    def _retornar_para_lista_contratos(self):
        """Retorna à página de lista de contratos clicando no botão 'Voltar' ou navegando por URL."""
        try:
            voltar_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Voltar')]"))
            )
            logger.info("Clicando no botão 'Voltar' para retornar à lista de contratos.")
            self.driver.execute_script("arguments[0].click();", voltar_btn)
            self._aguardar_renderizacao_contratos()
            return True
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException):
            logger.warning("Botão 'Voltar' não encontrado ou não clicável. Tentando retorno por URL como alternativa.")
            self.driver.get("https://minhaclaroresidencial.claro.com.br/empresas/contratos")
            self._aguardar_renderizacao_contratos()
            return True

    def _avancar_para_proxima_pagina(self) -> bool:
        """Avança para a próxima página usando o botão >."""
        try:
            next_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    '.mdn-Pagination-Link.mdn-Pagination-Link--next:not([disabled="disabled"])'
                ))
            )
            self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2) # Pequena espera para renderização
            self._aguardar_renderizacao_contratos()
            return True
        except TimeoutException:
            logger.info("Botão de próxima página não encontrado ou desabilitado.")
            return False

    def _obter_lista_de_contratos_ativos(self) -> List[Dict[str, Any]]:
        """Obtém uma lista de todos os contratos ativos, navegando por todas as páginas."""
        contratos_ativos = []
        pagina_atual = 1
        
        while True:
            logger.info(f"Coletando contratos na página {pagina_atual}...")
            self._aguardar_renderizacao_contratos()
            
            contratos_elements = self.driver.find_elements(By.CLASS_NAME, "contract")
            
            for element in contratos_elements:
                try:
                    card = ContratoCard(self.driver, element)
                    if not card.esta_encerrado():
                        contrato_info = {
                            'numero': card.obter_numero_contrato(),
                            'pagina': pagina_atual,
                            'indice_na_pagina': contratos_elements.index(element)
                        }
                        contratos_ativos.append(contrato_info)
                except Exception as e:
                    logger.warning(f"Erro ao processar um card de contrato: {e}")

            if not self._avancar_para_proxima_pagina():
                logger.info("Não há mais páginas. Coleta de contratos concluída.")
                break
            
            pagina_atual += 1
            
        return contratos_ativos

    def processar_todos_contratos_ativos(self, callback_processamento: Callable[[str], Any]):
        """
        Processa cada contrato ativo de forma individual e robusta.
        """
        try:
            # 1. Coleta a lista de contratos e suas localizações antes de começar
            contratos_para_processar = self._obter_lista_de_contratos_ativos()
            
            if not contratos_para_processar:
                logger.info("Nenhum contrato ativo encontrado para processar.")
                return

            logger.info(f"Iniciando processamento de {len(contratos_para_processar)} contratos ativos.")

            # 2. Processa cada contrato individualmente
            for i, contrato in enumerate(contratos_para_processar):
                try:
                    logger.info(f"Processando contrato {i+1} de {len(contratos_para_processar)}: {contrato['numero']}")
                    
                    # Navega para a página de contratos e aguarda
                    self.driver.get("https://minhaclaroresidencial.claro.com.br/empresas/contratos")
                    self._aguardar_renderizacao_contratos()
                    
                    # Navega para a página correta do contrato
                    for _ in range(contrato['pagina'] - 1):
                        self._avancar_para_proxima_pagina()
                        
                    # Encontra o contrato na página atual
                    contratos_na_pagina = self.wait.until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "contract"))
                    )
                    
                    # Tenta clicar no contrato usando o índice
                    contrato_element = contratos_na_pagina[contrato['indice_na_pagina']]
                    card = ContratoCard(self.driver, contrato_element)

                    if card.clicar_selecionar():
                        logger.info(f"Contrato {contrato['numero']} selecionado. Prosseguindo para download.")
                        callback_processamento(contrato['numero'])
                        
                        # Retorna à lista para a próxima iteração
                        self._retornar_para_lista_contratos()
                        
                except Exception as e:
                    logger.error(f"Falha ao processar o contrato {contrato['numero']}: {e}", exc_info=True)
                    # Tenta retornar à lista para continuar para o próximo contrato
                    self._retornar_para_lista_contratos()
                    
        except Exception as e:
            logger.error(f"Erro fatal na execução principal: {e}", exc_info=True)