import os
import time
import logging
from selenium.webdriver.support.ui import WebDriverWait

from utils.downloadUtils import mover_e_copiar_arquivo, DOWNLOAD_DIR
from pages.faturasPendentes import FaturasPendentesPage

logger = logging.getLogger(__name__)

class DownloadService:
    def __init__(self, driver, faturas_pendentes_page: FaturasPendentesPage, timeout=60):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.faturas_pendentes_page = faturas_pendentes_page

    def baixar_faturas(self, numero_contrato: str, linux_download_dir: str, windows_download_dir: str):
        """
        Orquestra o processo de download da fatura.
        """
        logger.info(f"Iniciando processo de download para o contrato {numero_contrato}...")

        nome_arquivo = self.faturas_pendentes_page.selecionar_e_baixar_fatura()

        if nome_arquivo:
            # Garante um nome de arquivo padrão se o atributo 'download' estiver vazio
            if not nome_arquivo:
                nome_arquivo = f"fatura_claro_{numero_contrato}.pdf"
            
            logger.info(f"Nome do arquivo para download: {nome_arquivo}")
            
            # Mover e copiar o arquivo após o download ser concluído
            mover_e_copiar_arquivo(nome_arquivo, linux_download_dir, windows_download_dir, numero_contrato)
            
            logger.info("Download concluído e arquivo movido com sucesso.")

        else:
            logger.info("Não foi possível iniciar o download da fatura. Nenhuma fatura pendente foi encontrada.")