#faturasPendentes.py
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Tuple, List
from datetime import datetime, timedelta
import locale
import time

logger = logging.getLogger(__name__)

# Configurar locale para português do Brasil
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

class FaturasPendentesPage:
    def __init__(self, driver, timeout=30):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _obter_mes_ano_atual_e_anterior(self) -> Tuple[Tuple[str, int], Tuple[str, int]]:
        hoje = datetime.today()
        mes_atual = hoje.strftime('%B').lower()
        ano_atual = hoje.year
        mes_anterior_data = hoje.replace(day=1) - timedelta(days=1)
        mes_anterior = mes_anterior_data.strftime('%B').lower()
        ano_anterior = mes_anterior_data.year
        return (mes_atual, ano_atual), (mes_anterior, ano_anterior)

    def _normalizar_texto(self, texto: str) -> str:
        return texto.strip().lower()

    def _clicar_aba_mes(self, mes: str, ano: int) -> bool:
        xpath_aba = (
            f"//li[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{mes}') "
            f"and contains(., '{ano}')]"
        )
        try:
            logger.info(f"Tentando localizar a aba do mês '{mes} {ano}'...")
            aba_mes = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_aba)))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", aba_mes)
            self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_aba)))
            self.driver.execute_script("arguments[0].click();", aba_mes)
            logger.info(f"Aba do mês '{mes} {ano}' clicada com sucesso.")
            self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "invoice-list-item")))
            return True
        except Exception as e:
            logger.warning(f"Falha ao clicar na aba do mês '{mes} {ano}': {e}")
            return False

    def _buscar_faturas_pendentes(self, mes: str, ano: int) -> List:
        try:
            faturas = self.wait.until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "invoice-list-item"))
            )
        except Exception as e:
            logger.error(f"Erro ao localizar faturas na aba '{mes} {ano}': {e}")
            return []

        mes_ano_str = f"{mes} {ano}".lower()
        faturas_pendentes = []
        for fatura in faturas:
            try:
                titulo = self._normalizar_texto(
                    fatura.find_element(By.CLASS_NAME, "invoice-list-item__content-infos-text--title").text
                )
                status_element = fatura.find_element(By.CLASS_NAME, "status-tag")
                status_texto = self._normalizar_texto(status_element.text)

                if mes_ano_str in titulo and status_texto == 'aguardando':
                    faturas_pendentes.append(fatura)
            except Exception as e:
                logger.warning(f"Erro ao verificar fatura: {e}")
        return faturas_pendentes

    def selecionar_e_baixar_fatura(self) -> str or None:
        """
        Navega, localiza e baixa faturas pendentes dos meses atual e anterior.
        Retorna o nome do arquivo se o download começar, ou None caso contrário.
        """
        (mes_atual, ano_atual), (mes_anterior, ano_anterior) = self._obter_mes_ano_atual_e_anterior()
        logger.info(f"Meses para verificação: {mes_atual} {ano_atual} e {mes_anterior} {ano_anterior}")

        for mes, ano in [(mes_atual, ano_atual), (mes_anterior, ano_anterior)]:
            if self._clicar_aba_mes(mes, ano):
                faturas = self._buscar_faturas_pendentes(mes, ano)
                if faturas:
                    fatura_element = faturas[0]
                    try:
                        logger.info(f"Fatura pendente encontrada para {mes} {ano}. Clicando em 'Selecionar'...")
                        botao_selecionar = fatura_element.find_element(By.XPATH, ".//a[contains(text(), 'Selecionar')]")
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao_selecionar)
                        self.wait.until(EC.element_to_be_clickable(botao_selecionar))
                        self.driver.execute_script("arguments[0].click();", botao_selecionar)
                        
                        logger.info("Fatura selecionada. Aguardando link de download...")
                        
                        # Espera de forma mais robusta pelo botão de download usando o 'data-testid'
                        download_link = self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="download-invoice"]'))
                        )
                        
                        logger.info("Botão de download encontrado. Clicando...")
                        nome_arquivo = download_link.get_attribute("download")
                        self.driver.execute_script("arguments[0].click();", download_link)
                        
                        return nome_arquivo
                    
                    except Exception as e:
                        logger.error(f"Falha ao selecionar ou baixar fatura de {mes} {ano}: {e}", exc_info=True)
                        continue
        
        logger.info("Nenhuma fatura pendente encontrada nos meses atual e anterior.")
        return None