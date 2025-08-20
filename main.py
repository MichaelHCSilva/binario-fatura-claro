# main.py
import logging
import sys
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pages.loginClaro import LoginPage
from pages.faturaClaro import FaturaPage
from pages.faturasPendentes import FaturasPendentesPage
from pages.downloadFaturaClaro import DownloadService
from utils.downloadUtils import garantir_diretorio
from utils.configuracoes import configurar_driver_chrome
from utils.interacoes import tratar_popup_cookies

logger = logging.getLogger(__name__)

def main():
    load_dotenv()

    USUARIO_CLARO = os.getenv("USUARIO_CLARO")
    SENHA_CLARO = os.getenv("SENHA_CLARO")
    LOGIN_URL = os.getenv("LOGIN_URL")
    CONTRATOS_URL = os.getenv("CONTRATOS_URL")

    LINUX_DOWNLOAD_DIR = os.getenv("LINUX_DOWNLOAD_DIR")
    WINDOWS_DOWNLOAD_DIR = os.getenv("WINDOWS_DOWNLOAD_DIR")
    USER_DATA_DIR = os.getenv("CHROME_USER_DATA_DIR")
    PROFILE_DIRECTORY = os.getenv("CHROME_PROFILE_DIRECTORY")

    download_dir = LINUX_DOWNLOAD_DIR if os.name == 'posix' else WINDOWS_DOWNLOAD_DIR
    garantir_diretorio(download_dir)

    driver = configurar_driver_chrome(
        user_data_dir=USER_DATA_DIR,
        profile_directory=PROFILE_DIRECTORY,
        download_dir=download_dir
    )

    try:
        logger.info("Iniciando o processo de login...")
        login_page = LoginPage(driver, LOGIN_URL)
        login_page.open_login_page()

        if not login_page.esta_logado():
            logger.info("Usuário não está logado. Iniciando login...")
            login_page.click_entrar()
            login_page.selecionar_minha_claro_residencial()
            tratar_popup_cookies(driver)
            login_page.preencher_login_usuario(USUARIO_CLARO)
            login_page.clicar_continuar()
            login_page.preencher_senha(SENHA_CLARO)
            login_page.clicar_botao_acessar()
        else:
            logger.info("Sessão já ativa, pulando login.")
            tratar_popup_cookies(driver)

        fatura_page = FaturaPage(driver)
        faturas_pendentes_page = FaturasPendentesPage(driver)
        download_service = DownloadService(driver, faturas_pendentes_page)

        def processar_contrato(numero_contrato: str):
            download_service.baixar_faturas(numero_contrato, LINUX_DOWNLOAD_DIR, WINDOWS_DOWNLOAD_DIR)
            
        fatura_page.processar_todos_contratos_ativos(processar_contrato, CONTRATOS_URL)

    except Exception as e:
        logger.error(f"Erro geral na execução: {e}", exc_info=True)
    finally:
        input("⏸ Pressione Enter para encerrar...")
        driver.quit()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    main()