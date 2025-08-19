import logging
import sys
import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException

# Ajusta path para importar módulos locais
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pages.loginClaro import LoginPage
from pages.faturaClaro import FaturaPage
from pages.faturasPendentes import FaturasPendentesPage
from pages.downloadFaturaClaro import DownloadService
from utils.downloadUtils import garantir_diretorio

logger = logging.getLogger(__name__)

def _tratar_popup_cookies(driver: webdriver.Chrome, timeout: int = 10):
    """Trata o popup de cookies, se ele aparecer."""
    logger.info("Verificando a presença do popup de cookies...")
    try:
        wait = WebDriverWait(driver, timeout)
        accept_button = wait.until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        accept_button.click()
        logger.info("Popup de cookies aceito com sucesso.")
        time.sleep(2)
    except (TimeoutException, ElementClickInterceptedException, NoSuchElementException):
        logger.info("Popup de cookies não foi encontrado ou não precisa ser tratado.")

def main():
    load_dotenv()

    LINUX_DOWNLOAD_DIR = "/home/allancdev/faturas_temp"
    WINDOWS_DOWNLOAD_DIR = "/mnt/c/Users/compu/OneDrive/Documentos/binario-fatura-claro/fatura/Claro"

    garantir_diretorio(LINUX_DOWNLOAD_DIR)
    garantir_diretorio(WINDOWS_DOWNLOAD_DIR)

    options = Options()
    options.add_argument("--user-data-dir=/mnt/c/Users/compu/AppData/Local/Google/Chrome/User Data")
    options.add_argument("--profile-directory=Profile 2")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    service = Service("/usr/local/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
    })

    try:
        logger.info("Abrindo página de login...")
        login_page = LoginPage(driver)
        login_page.open_login_page()

        if not login_page.esta_logado():
            logger.info("Usuário não está logado. Iniciando login...")
            login_page.click_entrar()
            login_page.selecionar_minha_claro_residencial()
            _tratar_popup_cookies(driver)
            login_page.preencher_login_usuario()
            login_page.clicar_continuar()
            login_page.preencher_senha()
            login_page.clicar_botao_acessar()
        else:
            logger.info("Sessão já ativa, pulando login.")
            _tratar_popup_cookies(driver)

        fatura_page = FaturaPage(driver)
        faturas_pendentes_page = FaturasPendentesPage(driver)
        download_service = DownloadService(driver, faturas_pendentes_page)

        def processar_contrato(numero_contrato: str):
            download_service.baixar_faturas(numero_contrato, LINUX_DOWNLOAD_DIR, WINDOWS_DOWNLOAD_DIR)
            
        fatura_page.processar_todos_contratos_ativos(processar_contrato)

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